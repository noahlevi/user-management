import re
from datetime import datetime

from pydantic import validator, BaseModel  # , EmailStr


class UserRegisterRequestSchema(BaseModel):
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    password: str  # , EmailStr

    @validator("role", check_fields=False)
    def role_match(cls, v: str, values, **kwargs):
        from user_management.utils.enums import UserRoleEnum

        if v.lower() not in UserRoleEnum.list():
            raise ValueError("Role doesn't match to existing roles")
        return v

    @validator("first_name", "last_name", check_fields=False)
    def names_match(cls, v: str, values, **kwargs):
        if not re.match(
            r"^(?=.{2,32}$)(?![_.-])(?!.*[_.]{2})[a-zA-Z0-9._-]+(?<![_.])$", v
        ):
            raise ValueError(
                "First and last names should be: \n"
                " - 2-32 symbols long \n"
                " - no _,- or . at the beginning \n"
                " - no __ or . or . or .. or .- or _- inside \n"
                " - no _,- or . at the end \n"
            )
        return v

    @validator("email", check_fields=False)
    def email_match(cls, v: str, values, **kwargs):
        if not re.match(r"^((?!\.)[\w_.]*[^.])(@\w+)(\.\w+(\.\w+)?[^.\W])$", v):
            raise ValueError(
                "Incorrect email. The email couldn't start or finish with a '.', "
                "shouldn't contain spaces into the string, contain special chars (<:, *,ecc), "
                "could contain dots in the middle of mail address before the '@' and "
                "double domain ( '.de.org' or similar rarity)"
            )
        return v

    @validator("password", check_fields=False)
    def password_match(cls, v: str, values, **kwargs):
        if not re.match(r"^(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[^\w\d\s:])([^\s]){4,16}$", v):
            raise ValueError(
                "Incorrect password. Password is 4-16 characters "
                "with no space and should contains: "
                "1 number (0-9), 1 uppercase letters, "
                "1 lowercase letters, "
                "1 non-alpha numeric number, "
            )
        return v


class AdminUpdateUserRequestSchema(BaseModel):
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    role: str | None = None
    is_active: bool | None = None
    password: str | None = None
    last_login: datetime | None = None
    created_at: datetime | None = None

    @validator("role", check_fields=False)
    def role_match(cls, v: str, values, **kwargs):
        from user_management.utils.enums import UserRoleEnum

        if v:
            role_list = UserRoleEnum.list()
            if v.lower() not in UserRoleEnum.list():
                raise ValueError(f"Role doesn't match to existing roles. Choose between {role_list}")
            return v

    @validator("email", check_fields=False)
    def email_match(cls, v: str, values, **kwargs):
        if v:
            if not re.match(r"^((?!\.)[\w_.]*[^.])(@\w+)(\.\w+(\.\w+)?[^.\W])$", v):
                raise ValueError(
                    "Incorrect email. The email couldn't start or finish with a '.', "
                    "shouldn't contain spaces into the string, contain special chars (<:, *,ecc), "
                    "could contain dots in the middle of mail address before the '@' and "
                    "double domain ( '.de.org' or similar rarity)"
                )
            return v

    @validator("first_name", "last_name", check_fields=False)
    def names_match(cls, v: str, values, **kwargs):
        if v:
            if not re.match(
                r"^(?=.{2,32}$)(?![_.-])(?!.*[_.]{2})[a-zA-Z0-9._-]+(?<![_.])$", v
            ):
                raise ValueError(
                    "First and last names should be: \n"
                    " - 2-32 symbols long \n"
                    " - no _,- or . at the beginning \n"
                    " - no __ or . or . or .. or .- or _- inside \n"
                    " - no _,- or . at the end \n"
                )
            return v

    @validator("password", check_fields=False)
    def password_match(cls, v: str, values, **kwargs):
        if v:
            if not re.match(r"^(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[^\w\d\s:])([^\s]){4,16}$", v):
                raise ValueError(
                    "Incorrect password. Password is 4-16 characters "
                    "with no space and should contains: "
                    "1 number (0-9), 1 uppercase letters, "
                    "1 lowercase letters, "
                    "1 non-alpha numeric number, "
                )
            return v


class UserAuthResponseSchema(BaseModel):
    access_token: str
    success: bool = True
    token_type: str = "bearer"


class AdminDeleteUserSuccessResponseSchema(BaseModel):
    user_id: str
    success: bool = True


class SimplePaginationSchema(BaseModel):
    page: int = 1
    per_page: int = 10

    @validator("page", "per_page", check_fields=False)
    def paginator_match(cls, v: int, values, **kwargs):
        if v <= 0:
            raise ValueError("Pagination parameters should be greater then 0")
        return v
