from pathlib import Path

import yaml
from loguru import logger
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, create_engine

from agentchat.database.models.agent import AgentTable
from agentchat.database.models.agent_skill import AgentSkill
from agentchat.database.models.dialog import DialogTable
from agentchat.database.models.history import HistoryTable
from agentchat.database.models.knowledge import KnowledgeTable
from agentchat.database.models.knowledge_file import KnowledgeFileTable
from agentchat.database.models.llm import LLMTable
from agentchat.database.models.mcp_agent import MCPAgentTable
from agentchat.database.models.mcp_server import MCPServerStdioTable, MCPServerTable
from agentchat.database.models.mcp_user_config import MCPUserConfigTable
from agentchat.database.models.memory_history import MemoryHistoryTable
from agentchat.database.models.message import MessageDownTable, MessageLikeTable
from agentchat.database.models.role import Role
from agentchat.database.models.tool import ToolTable
from agentchat.database.models.usage_stats import UsageStats
from agentchat.database.models.user import SystemUser
from agentchat.database.models.user_role import UserRole
from agentchat.database.models.workspace_session import WorkSpaceSession
from agentchat.settings import app_settings


def _load_database_config() -> dict:
    if app_settings.database:
        return app_settings.database

    config_path = Path(__file__).resolve().parents[1] / "config.yaml"
    with config_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("database") or {}


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
    """
    Ensure the target PostgreSQL database exists.
    This function is safe to call on every startup.
    """
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
