from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT

from zuno.api.errcode.user import UserValidateError
from zuno.api.services.user import UserService, get_user_jwt
from zuno.schema.schemas import UnifiedResponseModel, resp_200

router = APIRouter(tags=["User"])


@router.post("/user/register", response_model=UnifiedResponseModel)
async def register(
    user_name: str = Body(description="user name"),
    user_email: Optional[str] = Body(description="user email"),
    user_password: str = Body(description="user password"),
):
    try:
        UserService.register_user(user_name, user_email, user_password)
    except ValueError as exc:
        detail = str(exc)
        if detail == "user_name_exists":
            raise HTTPException(status_code=500, detail="user name already exists")
        if detail == "user_name_too_long":
            raise HTTPException(status_code=500, detail="user name must be at most 20 characters")
        raise HTTPException(status_code=500, detail=detail)
    return resp_200()


@router.post("/user/login", response_model=UnifiedResponseModel)
async def login(
    user_name: str = Body(description="user name"),
    user_password: str = Body(description="user password"),
    Authorize: AuthJWT = Depends(),
):
    db_user = UserService.authenticate_user(user_name, user_password)
    if not db_user:
        return UserValidateError.return_resp()

    if db_user.delete:
        raise HTTPException(status_code=500, detail="this account has been disabled")

    access_token, refresh_token, role = get_user_jwt(db_user)
    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)
    UserService.persist_auth_session(db_user.user_id, access_token)

    return resp_200(data={"user_id": db_user.user_id, "access_token": access_token})


@router.put("/user/update", response_model=UnifiedResponseModel)
async def update_user_info(
    user_id: str = Body(description="user id"),
    user_avatar: Optional[str] = Body(description="user avatar url"),
    user_description: Optional[str] = Body(description="user description"),
):
    UserService.update_user_info(user_id, user_avatar, user_description)
    return resp_200()


@router.get("/user/icons", response_model=UnifiedResponseModel)
async def get_select_user_avatar():
    return resp_200(UserService.get_available_avatars())


@router.get("/user/info", response_model=UnifiedResponseModel)
async def get_user_info(user_id: str):
    return resp_200(UserService.get_user_info_by_id(user_id))


__all__ = [
    "get_select_user_avatar",
    "get_user_info",
    "login",
    "register",
    "router",
    "update_user_info",
]
