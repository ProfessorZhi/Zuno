from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    authjwt_secret_key: str = "secret"
    authjwt_token_location: list = ["cookies", "headers"]
    authjwt_cookie_csrf_protect: bool = False


__all__ = ["Settings"]
