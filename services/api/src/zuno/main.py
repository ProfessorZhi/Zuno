import asyncio
import logging
import warnings
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

from zuno.middleware.trace_id_middleware import TraceIDMiddleware
from zuno.middleware.white_list_middleware import WhitelistMiddleware
from zuno.settings import app_settings, initialize_app_settings
from zuno.utils.runtime_observability import configure_langsmith

warnings.filterwarnings("ignore")
logging.getLogger("chromadb").setLevel(logging.WARNING)


async def register_router(app: FastAPI):
    from zuno.api.router import router

    app.include_router(router)

    @app.get("/health")
    def check_health():
        return {"status": "OK"}


def register_middleware(app: FastAPI):
    app.add_middleware(TraceIDMiddleware)
    app.add_middleware(WhitelistMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


async def init_config():
    await initialize_app_settings()
    configure_langsmith()

    from zuno.database.init_data import (
        init_database,
        init_default_agent,
        update_system_mcp_server,
        upload_user_avatars_storage,
    )

    database_ready = await init_database()
    if not database_ready:
        raise RuntimeError("Database bootstrap failed during Phase 0 startup recovery")

    await init_default_agent()

    async def run_optional_startup(name, coroutine, timeout_seconds: int = 20):
        try:
            await asyncio.wait_for(coroutine, timeout=timeout_seconds)
        except Exception as err:
            logging.getLogger(__name__).warning("Optional startup task %s skipped: %s", name, err)

    await run_optional_startup("update_system_mcp_server", update_system_mcp_server())
    await run_optional_startup("upload_user_avatars_storage", upload_user_avatars_storage())


def print_logo():
    from pyfiglet import Figlet

    figlet = Figlet(font="slant")
    print(figlet.renderText("Zuno"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_config()
    await register_router(app)
    print_logo()
    yield


def create_app():
    app = FastAPI(
        title=app_settings.server.get("project_name", "Zuno"),
        version=app_settings.server.get("version", "v2.4.0"),
        lifespan=lifespan,
    )
    app = register_middleware(app)

    from zuno.api.JWT import Settings

    @AuthJWT.load_config
    def get_config():
        return Settings()

    @app.exception_handler(AuthJWTException)
    def authjwt_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    return app


app = create_app()


__all__ = ["app", "create_app", "lifespan", "init_config", "register_router", "register_middleware"]
