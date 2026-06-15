from zuno.api.errcode.base import BaseErrorCode


class UserValidateError(BaseErrorCode):
    Code: int = 10600
    Msg: str = "账号或密码错误"


class UserPasswordExpireError(BaseErrorCode):
    Code: int = 10601
    Msg: str = "您的密码已过期，请及时修改"


class UserNotPasswordError(BaseErrorCode):
    Code: int = 10602
    Msg: str = "用户尚未设置密码，请先联系管理员重置密码"


class UserPasswordError(BaseErrorCode):
    Code: int = 10603
    Msg: str = "当前密码错误"


class UserLoginOfflineError(BaseErrorCode):
    Code: int = 10604
    Msg: str = "您的账号已在另一设备登录，此设备上的会话已被注销。如非本人操作，请尽快修改账户密码。"


class UserNameAlreadyExistError(BaseErrorCode):
    Code: int = 10605
    Msg: str = "用户名已存在"


class UserNeedGroupAndRoleError(BaseErrorCode):
    Code: int = 10606
    Msg: str = "用户组和角色不能为空"


class UserGroupNotDeleteError(BaseErrorCode):
    Code: int = 10610
    Msg: str = "用户组内还有用户，不能删除"


__all__ = [
    "UserGroupNotDeleteError",
    "UserLoginOfflineError",
    "UserNameAlreadyExistError",
    "UserNeedGroupAndRoleError",
    "UserNotPasswordError",
    "UserPasswordError",
    "UserPasswordExpireError",
    "UserValidateError",
]
