"""Compatibility exports for vendored FastAPI JWT Auth exceptions."""

from zuno.vendor.fastapi_jwt_auth.exceptions import (
    AccessTokenRequired,
    AuthJWTException,
    CSRFError,
    FreshTokenRequired,
    InvalidHeaderError,
    JWTDecodeError,
    MissingTokenError,
    RefreshTokenRequired,
    RevokedTokenError,
)

__all__ = [
    "AccessTokenRequired",
    "AuthJWTException",
    "CSRFError",
    "FreshTokenRequired",
    "InvalidHeaderError",
    "JWTDecodeError",
    "MissingTokenError",
    "RefreshTokenRequired",
    "RevokedTokenError",
]
