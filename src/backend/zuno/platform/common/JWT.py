from typing import List

from pydantic import BaseModel


ACCESS_TOKEN_EXPIRE_TIME = 86400


class Settings(BaseModel):
    authjwt_secret_key: str = "secret"
    authjwt_token_location: List[str] = ["cookies", "headers"]
    authjwt_cookie_csrf_protect: bool = False


__all__ = ["ACCESS_TOKEN_EXPIRE_TIME", "Settings"]
