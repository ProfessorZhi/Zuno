from typing import List

from sqlmodel import and_, delete, or_, select, update

from zuno.database.models.tool import ToolTable
from zuno.platform.database.session import async_session_getter, session_getter


class ToolDao:
    @classmethod
    async def _get_tool(cls, zh_name: str, en_name: str, user_id: str, description: str, logo_url: str):
        return ToolTable(
            zh_name=zh_name,
            en_name=en_name,
            logo_url=logo_url,
            user_id=user_id,
            description=description,
        )

    @classmethod
    async def delete_user_defined_tool(cls, tool_id: str):
        async with async_session_getter() as session:
            statement = delete(ToolTable).where(ToolTable.tool_id == tool_id)
            await session.exec(statement)
            await session.flush()

    @classmethod
    async def update_tool_by_id(
        cls,
        tool_id: str,
        zh_name: str,
        en_name: str,
        description: str,
        logo_url: str,
    ):
        with session_getter() as session:
            update_values = {}
            if zh_name:
                update_values["zh_name"] = zh_name
            if en_name:
                update_values["en_name"] = en_name
            if description:
                update_values["description"] = description
            if logo_url:
                update_values["logo_url"] = logo_url

            sql = update(ToolTable).where(ToolTable.tool_id == tool_id).values(**update_values)
            session.exec(sql)
            session.flush()

    @classmethod
    async def get_tool_by_user_id(cls, user_id: str):
        with session_getter() as session:
            sql = select(ToolTable).where(ToolTable.user_id == user_id)
            return session.exec(sql).all()

    @classmethod
    async def get_tool_by_name_and_user_id(cls, name: str, user_id: str):
        with session_getter() as session:
            sql = select(ToolTable).where(and_(ToolTable.name == name, ToolTable.user_id == user_id))
            return session.exec(sql).all()

    @classmethod
    async def get_tool_name_by_id(cls, tool_id: List[str]):
        with session_getter() as session:
            sql = select(ToolTable).where(ToolTable.tool_id.in_(tool_id))
            return session.exec(sql).all()

    @classmethod
    async def get_all_tools(cls, user_id):
        async with async_session_getter() as session:
            statement = select(ToolTable).where(ToolTable.user_id == user_id)
            result = await session.exec(statement)
            return result.all()

    @classmethod
    async def get_tool_by_id(cls, tool_id: str):
        with session_getter() as session:
            sql = select(ToolTable).where(ToolTable.tool_id == tool_id)
            return session.exec(sql).first()

    @classmethod
    async def get_id_by_tool_name(cls, tool_name, user_id):
        with session_getter() as session:
            sql = select(ToolTable).where(
                and_(
                    ToolTable.en_name == tool_name,
                    or_(ToolTable.user_id == user_id, ToolTable.user_id == "0"),
                )
            )
            return session.exec(sql).first()

    @classmethod
    async def get_tool_ids_from_name(cls, tool_names: List[str], user_id):
        with session_getter() as session:
            statement = select(ToolTable).where(
                and_(
                    ToolTable.display_name.in_(tool_names),
                    ToolTable.user_id == user_id,
                )
            )
            tools = session.exec(statement)
            return tools.all()

    @classmethod
    async def get_zh_name_from_en_name(cls, en_name):
        with session_getter() as session:
            sql = select(ToolTable).where(ToolTable.en_name == en_name)
            return session.exec(sql).first()

    @classmethod
    async def create_user_defined_tool(cls, tool: ToolTable):
        async with async_session_getter() as session:
            session.add(tool)
            await session.flush()
            await session.refresh(tool)
            return tool

    @classmethod
    async def create_default_tool(cls, tool):
        async with async_session_getter() as session:
            session.add(tool)
            await session.flush()
            await session.refresh(tool)
            return tool

    @classmethod
    async def delete_tool_by_id(cls, tool_id: str):
        async with async_session_getter() as session:
            statement = delete(ToolTable).where(ToolTable.tool_id == tool_id)
            await session.exec(statement)
            await session.flush()

    @classmethod
    async def get_user_defined_tools(cls, user_id):
        async with async_session_getter() as session:
            statement = select(ToolTable).where(ToolTable.user_id == user_id)
            result = await session.exec(statement)
            return result.all()

    @classmethod
    async def update_user_defined_tool(cls, tool_id, update_values):
        async with async_session_getter() as session:
            statement = update(ToolTable).where(ToolTable.tool_id == tool_id).values(**update_values)
            await session.exec(statement)
            await session.flush()


__all__ = ["ToolDao"]
