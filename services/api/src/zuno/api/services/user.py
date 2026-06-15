import hashlib
import json
import random
from base64 import b64decode
from typing import Optional

import rsa
from fastapi import Depends, HTTPException, Request
from fastapi_jwt_auth import AuthJWT
from loguru import logger

from zuno.api.errcode.user import UserNameAlreadyExistError
from zuno.database.dao.user import UserDao
from zuno.database.dao.user_role import UserRoleDao
from zuno.database.models.role import AdminRole
from zuno.database.models.user import AdminUser, UserTable
from zuno.schema.schemas import CreateUserReq
from zuno.services.redis import redis_client
from zuno.services.storage import storage_client
from zuno.settings import app_settings
from zuno.utils.constants import RSA_KEY
from zuno.utils.hash import md5_hash
from zuno.utils.JWT import ACCESS_TOKEN_EXPIRE_TIME
from zuno.utils.runtime_observability import RedisKeys

USER_AVATAR_ASSET_VERSION = "20260511-clean3"

LOCAL_USER_AVATAR_PRESETS = [
    f"/avatars/user/zuno-user-{index:02d}.png?v={USER_AVATAR_ASSET_VERSION}"
    for index in range(1, 21)
]


class UserPayload:
    def __init__(self, **kwargs):
        self.user_id = kwargs.get("user_id")
        self.user_role = kwargs.get("role")
        if self.user_role != "admin":
            roles = UserRoleDao.get_user_roles(self.user_id)
            self.user_role = [one.role_id for one in roles]
        self.user_name = kwargs.get("user_name")

    def is_admin(self):
        if self.user_role == "admin":
            return True
        if isinstance(self.user_role, list):
            for one in self.user_role:
                if one == AdminRole:
                    return True
        return False


class UserService:
    @classmethod
    def decrypt_md5_password(cls, password: str):
        if value := redis_client.get(RedisKeys.rsa_private_key()) or redis_client.get(RSA_KEY):
            private_key = value[1]
            password = md5_hash(rsa.decrypt(b64decode(password), private_key).decode("utf-8"))
        else:
            password = md5_hash(password)
        return password

    @classmethod
    def encrypt_sha256_password(cls, password: str):
        sha256 = hashlib.sha256()
        sha256.update(password.encode("utf-8"))
        return sha256.hexdigest()

    @classmethod
    def verify_password(cls, password: str, encrypted_password: str):
        return cls.encrypt_sha256_password(password) == encrypted_password

    @classmethod
    def create_user(cls, request: Request, login_user: UserPayload, req_data: CreateUserReq):
        exists_user = UserDao.get_user_by_username(req_data.user_name)
        if exists_user:
            raise UserNameAlreadyExistError.http_exception()
        user = UserTable(
            user_name=req_data.user_name,
            user_password=cls.decrypt_md5_password(req_data.password),
        )
        return UserDao.add_user_and_default_role(
            user_name=user.user_name,
            user_password=user.user_password,
        )

    @classmethod
    def get_random_user_avatar(cls):
        if LOCAL_USER_AVATAR_PRESETS:
            return random.choice(LOCAL_USER_AVATAR_PRESETS)
        files_url = storage_client.list_files_in_folder("icons/user")
        avatars_url = [f"{app_settings.storage.active.base_url}/{file_url}" for file_url in files_url]
        return random.choice(avatars_url) if avatars_url else ""

    @classmethod
    def get_available_avatars(cls):
        return LOCAL_USER_AVATAR_PRESETS

    @classmethod
    def get_user_info_by_id(cls, user_id):
        user_info = UserDao.get_user(user_id)
        return user_info.to_dict()

    @classmethod
    def update_user_info(cls, user_id, user_avatar, user_description):
        UserDao.update_user_info(user_id, user_avatar, user_description)

    @classmethod
    def get_user_id_by_name(cls, user_name):
        user = UserDao.get_user_by_username(user_name)
        return user.user_id

    @classmethod
    def register_user(cls, user_name: str, user_email: Optional[str], user_password: str) -> None:
        exist_user = UserDao.get_user_by_username(user_name)
        if exist_user:
            raise ValueError("user_name_exists")
        if len(user_name) > 20:
            raise ValueError("user_name_too_long")

        try:
            encrypted_password = cls.encrypt_sha256_password(user_password)
            user_avatar = cls.get_random_user_avatar()
            admin = UserDao.get_user(AdminUser)

            if admin:
                UserDao.add_user_and_default_role(user_name, user_email, encrypted_password, user_avatar)
            else:
                UserDao.add_user_and_admin_role(AdminUser, user_name, user_email, encrypted_password, user_avatar)
        except Exception as exc:
            logger.error(f"register user is appear error: {exc}")
            raise ValueError(f"register user is appear error: {exc}") from exc

    @classmethod
    def authenticate_user(cls, user_name: str, user_password: str) -> UserTable | None:
        db_user = UserDao.get_user_by_username(user_name)
        if not db_user or not cls.verify_password(user_password, db_user.user_password):
            return None
        return db_user

    @classmethod
    def persist_auth_session(cls, user_id: str, access_token: str) -> None:
        redis_client.set(
            RedisKeys.auth_session(user_id),
            access_token,
            ACCESS_TOKEN_EXPIRE_TIME + 3600,
        )


async def get_login_user(request: Request, authorize: AuthJWT = Depends()) -> UserPayload:
    if request.state.is_whitelisted:
        return UserPayload(user_id="1", user_name="Admin")

    try:
        authorize.jwt_required()
        current_user = json.loads(authorize.get_jwt_subject())
        return UserPayload(**current_user)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")


def get_user_role(db_user: UserTable):
    db_user_role = UserRoleDao.get_user_roles(db_user.user_id)
    role = ""
    role_ids = []
    for user_role in db_user_role:
        if user_role.role_id == "1":
            role = "admin"
        else:
            role_ids.append(user_role.role_id)
    if role != "admin":
        role = role_ids
    return role


def get_user_jwt(db_user: UserTable):
    role = get_user_role(db_user)
    payload = {"user_name": db_user.user_name, "user_id": db_user.user_id, "role": role}

    access_token = AuthJWT().create_access_token(
        subject=json.dumps(payload),
        expires_time=ACCESS_TOKEN_EXPIRE_TIME,
    )
    refresh_token = AuthJWT().create_refresh_token(subject=db_user.user_name)
    return access_token, refresh_token, role


__all__ = [
    "LOCAL_USER_AVATAR_PRESETS",
    "USER_AVATAR_ASSET_VERSION",
    "UserPayload",
    "UserService",
    "get_login_user",
    "get_user_jwt",
    "get_user_role",
]
