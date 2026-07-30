from pathlib import Path
from pkgutil import extend_path

import yaml
import zuno as zuno_package
from loguru import logger
from sqlalchemy.engine import make_url
from sqlmodel import SQLModel

from zuno.platform.database.runtime import PostgresRuntime, PostgresRuntimeConfig

__path__ = extend_path(__path__, __name__)


from zuno.platform.database.models.agent import AgentTable
from zuno.platform.database.models.agent_skill import AgentSkill
from zuno.platform.database.models.dialog import DialogTable
from zuno.platform.database.models.history import HistoryTable
from zuno.platform.database.models.knowledge import KnowledgeTable
from zuno.platform.database.models.knowledge_file import KnowledgeFileTable
from zuno.platform.database.models.knowledge_task import KnowledgeTaskEventTable, KnowledgeTaskTable
from zuno.platform.database.models.llm import LLMTable
from zuno.platform.database.models.mcp_agent import MCPAgentTable
from zuno.platform.database.models.mcp_server import MCPServerStdioTable, MCPServerTable
from zuno.platform.database.models.mcp_user_config import MCPUserConfigTable
from zuno.platform.database.models.memory_history import MemoryHistoryTable
from zuno.platform.database.models.memory_runtime import (
    MemoryCandidateTable,
    MemoryGovernanceLedgerTable,
    MemoryRawEventTable,
    MemoryReviewDecisionTable,
    MemoryTaskSummaryTable,
)
from zuno.platform.database.models.message import MessageDownTable, MessageLikeTable
from zuno.platform.database.models.role import Role
from zuno.platform.database.models.tool import ToolTable
from zuno.platform.database.models.usage_stats import UsageStats
from zuno.platform.database.models.user import SystemUser
from zuno.platform.database.models.user_role import UserRole
from zuno.platform.database.models.workspace_session import WorkSpaceSession
from zuno.settings import app_settings, resolve_app_config_path


def _load_database_config() -> dict:
    if app_settings.database:
        return app_settings.database

    config_path = resolve_app_config_path()
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}
        database = data.get("database") or {}
        if database:
            return database

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


postgres_runtime = PostgresRuntime(
    PostgresRuntimeConfig(
        sync_url=str(database_config.get("sync_endpoint") or ""),
        async_url=str(database_config.get("async_endpoint") or ""),
        pool_size=int(database_config.get("pool_size", 10)),
        max_overflow=int(database_config.get("max_overflow", 20)),
        pool_timeout_seconds=float(database_config.get("pool_timeout_seconds", 30)),
        pool_recycle_seconds=int(database_config.get("pool_recycle_seconds", 3600)),
        statement_timeout_ms=int(database_config.get("statement_timeout_ms", 30_000)),
        lock_timeout_ms=int(database_config.get("lock_timeout_ms", 5_000)),
        echo=bool(database_config.get("echo", False)),
    )
)
engine = postgres_runtime.sync_engine
async_engine = postgres_runtime.async_engine


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
    "MemoryCandidateTable",
    "MemoryGovernanceLedgerTable",
    "MemoryRawEventTable",
    "MemoryReviewDecisionTable",
    "MemoryTaskSummaryTable",
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
    "postgres_runtime",
]
