from pathlib import Path
from pkgutil import extend_path

import yaml
import zuno as zuno_package
from loguru import logger
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, create_engine

__path__ = extend_path(__path__, __name__)


from zuno.database.models.agent import AgentTable
from zuno.database.models.agent_skill import AgentSkill
from zuno.database.models.dialog import DialogTable
from zuno.database.models.history import HistoryTable
from zuno.database.models.knowledge import KnowledgeTable
from zuno.database.models.knowledge_file import KnowledgeFileTable
from zuno.database.models.knowledge_task import KnowledgeTaskEventTable, KnowledgeTaskTable
from zuno.database.models.llm import LLMTable
from zuno.database.models.mcp_agent import MCPAgentTable
from zuno.database.models.mcp_server import MCPServerStdioTable, MCPServerTable
from zuno.database.models.mcp_user_config import MCPUserConfigTable
from zuno.database.models.memory_history import MemoryHistoryTable
from zuno.database.models.message import MessageDownTable, MessageLikeTable
from zuno.database.models.role import Role
from zuno.database.models.tool import ToolTable
from zuno.database.models.usage_stats import UsageStats
from zuno.database.models.user import SystemUser
from zuno.database.models.user_role import UserRole
from zuno.database.models.workspace_session import WorkSpaceSession
from zuno.settings import app_settings


def _load_database_config() -> dict:
    if app_settings.database:
        return app_settings.database

    for package_path in __path__:
        package_root = Path(package_path).resolve().parent
        for config_path in [
            package_root / "config" / "config.yaml",
            package_root / "config" / "config.example.yaml",
            package_root / "config.yaml",
        ]:
            if config_path.exists():
                with config_path.open("r", encoding="utf-8") as file:
                    data = yaml.safe_load(file) or {}
                return data.get("database") or {}

    for zuno_package_path in getattr(zuno_package, "__path__", []):
        package_root = Path(zuno_package_path).resolve()
        for config_path in [
            package_root / "platform" / "config" / "config.yaml",
            package_root / "platform" / "config" / "config.example.yaml",
            package_root / "config.yaml",
        ]:
            if config_path.exists():
                with config_path.open("r", encoding="utf-8") as file:
                    data = yaml.safe_load(file) or {}
                return data.get("database") or {}
    return {}


database_config = _load_database_config()


engine = create_engine(
    url=database_config.get("sync_endpoint"),
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=database_config.get("echo", False),
)

async_engine = create_async_engine(
    url=database_config.get("async_endpoint"),
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=database_config.get("echo", False),
)


def ensure_database(endpoint: str | None = None) -> None:
    if not endpoint:
        endpoint = _load_database_config().get("sync_endpoint")
    if not endpoint:
        raise ValueError("Database endpoint is not configured")

    parsed = make_url(endpoint)
    database = parsed.database
    if not database:
        raise ValueError("Database endpoint must include database name")

    logger.info(f"Checking PostgreSQL database `{database}`")

    try:
        import psycopg
        from psycopg import sql
    except ImportError as exc:
        raise ImportError("psycopg is required for PostgreSQL bootstrap") from exc

    conninfo = (
        f"host={parsed.host or 'localhost'} "
        f"port={parsed.port or 5432} "
        f"user={parsed.username or ''} "
        f"password={parsed.password or ''} "
        "connect_timeout=3 "
        "dbname=postgres"
    )

    with psycopg.connect(conninfo=conninfo, autocommit=True) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,))
            if not cursor.fetchone():
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database)))
                logger.info(f"Created PostgreSQL database `{database}`")

    logger.success(f"PostgreSQL database `{database}` is ready")


__all__ = [
    "AgentSkill",
    "AgentTable",
    "DialogTable",
    "HistoryTable",
    "KnowledgeFileTable",
    "KnowledgeTable",
    "KnowledgeTaskEventTable",
    "KnowledgeTaskTable",
    "LLMTable",
    "MCPAgentTable",
    "MCPServerStdioTable",
    "MCPServerTable",
    "MCPUserConfigTable",
    "MemoryHistoryTable",
    "MessageDownTable",
    "MessageLikeTable",
    "Role",
    "SQLModel",
    "SystemUser",
    "ToolTable",
    "UsageStats",
    "UserRole",
    "WorkSpaceSession",
    "async_engine",
    "database_config",
    "ensure_database",
    "engine",
]
