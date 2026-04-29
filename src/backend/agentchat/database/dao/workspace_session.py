from typing import List

from sqlmodel import select, and_, delete, or_
from agentchat.database.session import async_session_getter
from agentchat.database.models.workspace_session import WorkSpaceSession


class WorkSpaceSessionDao:

    @classmethod
    async def get_workspace_sessions(cls, user_id, workspace_mode: str | None = None):
        async with async_session_getter() as session:
            statement = select(WorkSpaceSession).where(WorkSpaceSession.user_id == user_id)
            if workspace_mode == "agent":
                statement = statement.where(WorkSpaceSession.agent == "agent")
            elif workspace_mode == "normal":
                statement = statement.where(
                    or_(WorkSpaceSession.agent == "normal", WorkSpaceSession.agent == "simple")
                )
            result = await session.exec(statement)
            return result.all()

    @classmethod
    async def create_workspace_session(cls, workspace_session: WorkSpaceSession):
        async with async_session_getter() as session:
            # 如果没有提供session_id，自动生成一个
            if not workspace_session.session_id:
                from uuid import uuid4
                workspace_session.session_id = uuid4().hex
            session.add(workspace_session)
            await session.commit()
            await session.refresh(workspace_session)
        return workspace_session

    @classmethod
    async def delete_workspace_session(cls, session_ids: List[str], user_id):
        async with async_session_getter() as session:
            statement = delete(WorkSpaceSession).where(and_(WorkSpaceSession.session_id.in_(session_ids),
                                                            WorkSpaceSession.user_id == user_id))
            await session.exec(statement)
            await session.commit()

    @classmethod
    async def update_workspace_session_contexts(cls, session_id, session_context, title: str | None = None):
        async with async_session_getter() as session:
            workspace_session = await session.get(WorkSpaceSession, session_id)
            if workspace_session is None:
                return None
            new_contexts = workspace_session.contexts.copy()
            had_contexts = bool(new_contexts)
            new_contexts.append(session_context)
            workspace_session.contexts = new_contexts  # 重新赋值
            if title and (
                not had_contexts
                or str(workspace_session.title or "").strip().lower()
                in {"", "新对话", "未命名会话", "你好", "您好", "hi", "hello"}
            ):
                workspace_session.title = title

            await session.commit()
            await session.refresh(workspace_session)

        return workspace_session

    @classmethod
    async def get_workspace_session_from_id(cls, session_id, user_id: str | None = None):
        async with async_session_getter() as session:
            if user_id is None:
                return await session.get(WorkSpaceSession, session_id)

            statement = select(WorkSpaceSession).where(
                and_(
                    WorkSpaceSession.session_id == session_id,
                    WorkSpaceSession.user_id == user_id,
                )
            )
            result = await session.exec(statement)
            return result.first()

    @classmethod
    async def clear_workspace_session_contexts(cls, session_id):
        async with async_session_getter() as session:
            workspace_session = await session.get(WorkSpaceSession, session_id)
            new_contexts = []
            workspace_session.contexts = new_contexts  # 重新赋值

            await session.commit()
            await session.refresh(workspace_session)

        return workspace_session
