from fastapi.exceptions import HTTPException

from zuno.schema.schemas import UnifiedResponseModel


class BaseErrorCode:
    Code: int
    Msg: str

    @classmethod
    def return_resp(cls, msg: str = None, data: any = None) -> UnifiedResponseModel:
        return UnifiedResponseModel(status_code=cls.Code, status_message=msg or cls.Msg, data=data)

    @classmethod
    def http_exception(cls, msg: str = None) -> HTTPException:
        return HTTPException(status_code=cls.Code, detail=msg or cls.Msg)


class UnAuthorizedError(BaseErrorCode):
    Code: int = 403
    Msg: str = "暂无操作权限"


class NotFoundError(BaseErrorCode):
    Code: int = 404
    Msg: str = "资源不存在"


__all__ = [
    "BaseErrorCode",
    "NotFoundError",
    "UnAuthorizedError",
]
