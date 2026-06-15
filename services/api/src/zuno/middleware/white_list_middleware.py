from typing import List, Optional, Set

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from zuno.settings import app_settings


class WhitelistChecker:
    """白名单检查器类，负责路径匹配逻辑"""

    def __init__(self, whitelist_paths: List[str]):
        self.exact_paths: Set[str] = set()
        self.prefix_paths: List[str] = []

        for path in whitelist_paths:
            if path.endswith("/*"):
                self.prefix_paths.append(path.rstrip("/*"))
            elif path.endswith("*"):
                self.prefix_paths.append(path.rstrip("*"))
            else:
                self.exact_paths.add(path)

    def is_whitelisted(self, path: str) -> bool:
        if path in self.exact_paths:
            return True

        return any(path.startswith(prefix) for prefix in self.prefix_paths)


class WhitelistMiddleware(BaseHTTPMiddleware):
    """白名单检查中间件类"""

    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.whitelist_checker: Optional[WhitelistChecker] = None

    async def dispatch(self, request: Request, call_next):
        if not self.whitelist_checker:
            whitelist_paths = app_settings.whitelist_paths or []
            self.whitelist_checker = WhitelistChecker(whitelist_paths)

        request.state.is_whitelisted = self.whitelist_checker.is_whitelisted(request.url.path)
        response = await call_next(request)
        return response
