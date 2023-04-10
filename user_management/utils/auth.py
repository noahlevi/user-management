from datetime import datetime, timedelta
from typing import Optional, Union, Any

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
from pydantic import ValidationError

from user_management.config import Config


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/auth", scheme_name="JWT")


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Optional["User"]:
    from user_management.db import user
    from user_management.models.user import User

    try:
        payload = jwt.decode(
            token, Config.c.app.jwt_secret_key, algorithms=[Config.c.app.algorithm]
        )
        if datetime.fromtimestamp(payload.get("exp")) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    document = await user().find_one({"email": payload.get("sub")})

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )
    document = dict(document)
    return User.parse_obj(document)


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes=Config.c.app.access_token_expire_mins
        )

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, Config.c.app.jwt_secret_key, Config.c.app.algorithm
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes=Config.c.app.refresh_token_expire_mins
        )

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, Config.c.app.jwt_refresh_secret_key, Config.c.app.algorithm
    )
    return encoded_jwt
