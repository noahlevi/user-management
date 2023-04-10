from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel

from user_management.config import Config

_client: AsyncIOMotorClient = None  # type: ignore


def get_client() -> AsyncIOMotorClient:
    return _client if _client is not None else AsyncIOMotorClient(Config.c.mongo.dsn)


def get_db(db: str = None):
    return (
        get_client().get_database(db)
        if db is not None
        else get_client().get_default_database()
    )


def user():
    return get_db()['user']


def _create_collection():
    email_unique_idx = IndexModel(
        keys='email',
        unique=True,
    )
    user().create_indexes(
        indexes=[email_unique_idx],
    )


def _drop_collection():
    user().drop_indexes()
    user().delete_many({})
