from typing import List, Optional

from sqlmodel import and_, delete, select, update

from zuno.database.models.mcp_user_config import MCPUserConfigTable
from zuno.platform.database.session import session_getter


class MCPUserConfigDao:
    @classmethod
    async def create_mcp_user_config(cls, mcp_server_id: str, user_id: str, config: List[dict] = None):
        with session_getter() as session:
            mcp_user_config = MCPUserConfigTable(mcp_server_id=mcp_server_id, user_id=user_id, config=config)
            session.add(mcp_user_config)
            session.flush()

    @classmethod
    async def get_mcp_user_config_from_id(cls, config_id: str):
        with session_getter() as session:
            sql = select(MCPUserConfigTable).where(MCPUserConfigTable.id == config_id)
            return session.exec(sql).first()

    @classmethod
    async def delete_mcp_user_config(cls, config_id: str):
        with session_getter() as session:
            sql = delete(MCPUserConfigTable).where(MCPUserConfigTable.id == config_id)
            session.exec(sql)
            session.flush()

    @classmethod
    async def update_mcp_user_config(
        cls,
        mcp_server_id: List[dict] = None,
        user_id: Optional[str] = None,
        config: Optional[dict] = None,
    ):
        with session_getter() as session:
            update_values = {}
            if config is not None:
                update_values["config"] = config

            if update_values:
                sql = update(MCPUserConfigTable).where(
                    and_(
                        MCPUserConfigTable.user_id == user_id,
                        MCPUserConfigTable.mcp_server_id == mcp_server_id,
                    )
                ).values(**update_values)
                session.exec(sql)
                session.flush()

    @classmethod
    async def get_mcp_user_configs(cls, user_id: str, mcp_server_id: str):
        with session_getter() as session:
            sql = select(MCPUserConfigTable).where(
                and_(
                    MCPUserConfigTable.user_id == user_id,
                    MCPUserConfigTable.mcp_server_id == mcp_server_id,
                )
            )
            results = session.exec(sql)
            return results.first()


__all__ = ["MCPUserConfigDao"]
