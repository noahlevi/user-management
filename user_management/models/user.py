from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

import pymongo
from bson import ObjectId
from bson.errors import InvalidId
from pydantic import BaseModel, parse_obj_as, Field
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from user_management.api.schemas import (
    UserRegisterRequestSchema,
    AdminUpdateUserRequestSchema,
)
from user_management.db import user
from user_management.utils.auth import get_hashed_password, verify_password
from user_management.utils.custom_fields import PydanticObjectId

log = logging.getLogger(__name__)


class User(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: datetime
    # hashed_pass: str
    # password: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}


class UserModel:
    def __new__(cls, *args, **kwargs):
        raise NotImplementedError

    @staticmethod
    async def get_by_id(user_id: str) -> User | None:
        try:
            document = await user().find_one({"_id": ObjectId(user_id)})
        except InvalidId:
            return None
        if not document:
            return None
        document = dict(document)
        return User.parse_obj(document)

    @staticmethod
    async def admin_delete_user_by_id(user_id: str) -> Optional[bool]:
        try:
            document = await user().find_one_and_delete({"_id": ObjectId(user_id)})
        except InvalidId:
            return None
        if not document:
            return None
        return True

    @staticmethod
    async def admin_update(
        user_id: str, update_schema: AdminUpdateUserRequestSchema
    ) -> User | None:
        update_schema = update_schema.dict(exclude_none=True)
        if update_schema:
            if update_schema.get("password"):
                update_schema["hashed_pass"] = get_hashed_password(
                    password=update_schema.pop("password")
                )
            try:
                document = await user().find_one_and_update(
                    {"_id": ObjectId(user_id)},
                    {"$set": update_schema},
                    return_document=ReturnDocument.AFTER,
                )
            except InvalidId:
                return None
            if not document:
                return None
            document = dict(document)
            return User.parse_obj(document)

    @staticmethod
    async def login_user(email: str, password: str) -> User | None:
        document = await user().find_one({"email": email})
        if not document:
            return None
        document = dict(document)
        if verify_password(password=password, hashed_pass=document["hashed_pass"]):
            document = await user().find_one_and_update(
                {"email": email},
                {"$set": {"last_login": datetime.now()}},
                return_document=ReturnDocument.AFTER,
            )
            document = dict(document)
            return User.parse_obj(document)

    @staticmethod
    async def admin_get_users(page: int, per_page: int) -> list[User] | []:
        documents = (
            await user()
            .find()
            .limit(per_page)
            .skip(per_page * (page - 1))
            .sort("created_at", pymongo.ASCENDING)
            .to_list(per_page)
        )
        if not documents:
            return []
        return parse_obj_as(list[User], documents)

    @classmethod
    async def insert_user(
        cls, register_schema: UserRegisterRequestSchema
    ) -> User | None:
        user_dict = register_schema.dict()
        user_dict["created_at"] = datetime.utcnow()
        user_dict["last_login"] = datetime.utcnow()
        user_dict["hashed_pass"] = get_hashed_password(
            password=user_dict.pop("password")
        )
        try:
            document = await user().insert_one(document=user_dict)
        except DuplicateKeyError:
            log.exception(
                f'Duplicate key error while inserting user: '
                f'email: {user_dict["email"]}'
            )
            return None

        if inserted_id := str(document.inserted_id):
            u = await cls.get_by_id(user_id=str(inserted_id))
            return u
