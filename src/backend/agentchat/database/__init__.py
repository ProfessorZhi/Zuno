from pathlib import Path
import importlib

import yaml
from loguru import logger
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, create_engine
from agentchat.settings import app_settings, resolve_app_config_path


_MODEL_EXPORTS = {
    "AgentSkill": ("agentchat.database.models.agent_skill", "AgentSkill"),
    "AgentTable": ("agentchat.database.models.agent", "AgentTable"),
    "DialogTable": ("agentchat.database.models.dialog", "DialogTable"),
    "HistoryTable": ("agentchat.database.models.history", "HistoryTable"),
    "KnowledgeFileTable": ("agentchat.database.models.knowledge_file", "KnowledgeFileTable"),
    "KnowledgeTable": ("agentchat.database.models.knowledge", "KnowledgeTable"),
    "KnowledgeTaskEventTable": ("agentchat.database.models.knowledge_task", "KnowledgeTaskEventTable"),
    "KnowledgeTaskTable": ("agentchat.database.models.knowledge_task", "KnowledgeTaskTable"),
    "LLMTable": ("agentchat.database.models.llm", "LLMTable"),
    "MCPAgentTable": ("agentchat.database.models.mcp_agent", "MCPAgentTable"),
    "MCPServerStdioTable": ("agentchat.database.models.mcp_server", "MCPServerStdioTable"),
    "MCPServerTable": ("agentchat.database.models.mcp_server", "MCPServerTable"),
    "MCPUserConfigTable": ("agentchat.database.models.mcp_user_config", "MCPUserConfigTable"),
    "MemoryHistoryTable": ("agentchat.database.models.memory_history", "MemoryHistoryTable"),
    "MessageDownTable": ("agentchat.database.models.message", "MessageDownTable"),
    "MessageLikeTable": ("agentchat.database.models.message", "MessageLikeTable"),
    "Role": ("agentchat.database.models.role", "Role"),
    "SystemUser": ("agentchat.database.models.user", "SystemUser"),
    "ToolTable": ("agentchat.database.models.tool", "ToolTable"),
    "UsageStats": ("agentchat.database.models.usage_stats", "UsageStats"),
    "UserRole": ("agentchat.database.models.user_role", "UserRole"),
    "WorkSpaceSession": ("agentchat.database.models.workspace_session", "WorkSpaceSession"),
}


def _load_database_config() -> dict:
    if app_settings.database:
        return app_settings.database

    config_path = resolve_app_config_path()
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


def __getattr__(name: str):
    target = _MODEL_EXPORTS.get(name)
    if not target:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attr_name = target
    module = importlib.import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


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
