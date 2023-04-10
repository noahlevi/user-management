import logging

from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from user_management.api.schemas import (
    UserRegisterRequestSchema,
    SimplePaginationSchema,
    UserAuthResponseSchema,
    AdminUpdateUserRequestSchema,
    AdminDeleteUserSuccessResponseSchema,
)
from user_management.models.user import User, UserModel
from user_management.utils.auth import get_current_user, create_access_token
from user_management.utils.enums import UserRoleEnum

log = logging.getLogger(__name__)

router = APIRouter(prefix="/users")


@router.get(
    "{user_id}",
    description="Get user by id",
    status_code=status.HTTP_200_OK,
    response_model=User,
)
async def get_user(user_id: str):
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Provide user id"
        )

    user = await UserModel.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Did not found any user matching provided id",
        )
    return user


@router.delete(
    "{user_id}",
    description="Get user by id",
    status_code=status.HTTP_200_OK,
    response_model=AdminDeleteUserSuccessResponseSchema,
)
async def admin_delete_user(
    user_id: str,
    user: User = Depends(get_current_user),
):
    if user.role != UserRoleEnum.ADMIN.value:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access only"
            )
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Provide user id"
        )

    deleted = await UserModel.get_by_id(user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Did not found any user matching provided id",
        )
    return AdminDeleteUserSuccessResponseSchema(user_id=user_id)


@router.get(
    "/list",
    description="Get list of users by admin and dev",
    status_code=status.HTTP_200_OK,
    response_model=list[User],
)
async def admin_get_use_list(
    user: User = Depends(get_current_user),
    pagination_params: SimplePaginationSchema = Depends(),
):  #
    if user.role not in [UserRoleEnum.ADMIN.value, UserRoleEnum.DEV.value]:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access only"
            )
    users = await UserModel.admin_get_users(
        page=pagination_params.page, per_page=pagination_params.per_page
    )
    return users if users else []


@router.put(
    "{user_id}",
    description="Update user by admin",
    status_code=status.HTTP_200_OK,
    response_model=User,
)
async def admin_update_user(
    user_id: str,
    user_schema: AdminUpdateUserRequestSchema,
    user: User = Depends(get_current_user),
):
    if user.role != UserRoleEnum.ADMIN.value:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access only"
            )
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Provide user id"
        )

    user = await UserModel.admin_update(user_id=user_id, update_schema=user_schema)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Did not found any user matching provided id",
        )
    return user


@router.post(
    "/register",
    description="Register user by id",
    status_code=status.HTTP_201_CREATED,
    response_model=User,
)
async def register_user(user_schema: UserRegisterRequestSchema):
    if not (user := await UserModel.insert_user(register_schema=user_schema)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with current email is already exists",
        )

    return user


@router.post(
    "/auth",
    description="Authenticate user via email and password",
    status_code=status.HTTP_200_OK,
    response_model=UserAuthResponseSchema,
)
async def auth_user(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await UserModel.login_user(
        email=form_data.username, password=form_data.password
    )

    if user:
        return UserAuthResponseSchema(
            access_token=create_access_token(subject=user.email),
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Did not found any user matching provided id",
        )


@router.get(
    "/me/",
    description="Get current user data",
    status_code=status.HTTP_200_OK,
    response_model=User,
)
async def get_me(user: User = Depends(get_current_user)):
    return user
