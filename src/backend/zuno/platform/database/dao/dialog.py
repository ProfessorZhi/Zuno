from datetime import datetime, timezone

from sqlmodel import delete, desc, select, update

from zuno.database.models.dialog import DialogTable
from zuno.platform.database.session import session_getter


class DialogDao:
    @classmethod
    async def _get_dialog_sql(cls, name: str, agent_id: str, agent_type: str, user_id: str):
        return DialogTable(name=name, agent_id=agent_id, agent_type=agent_type, user_id=user_id)

    @classmethod
    async def create_dialog(cls, name: str, agent_id: str, agent_type: str, user_id: str):
        with session_getter() as session:
            dialog = await cls._get_dialog_sql(name, agent_id, agent_type, user_id)
            session.add(dialog)
            session.flush()
            session.refresh(dialog)
            return dialog

    @classmethod
    async def select_dialog(cls, dialog_id: str):
        with session_getter() as session:
            sql = select(DialogTable).where(DialogTable.dialog_id == dialog_id)
            return session.exec(sql).all()

    @classmethod
    async def get_dialog_by_user(cls, user_id: str):
        with session_getter() as session:
            sql = select(DialogTable).where(DialogTable.user_id == user_id).order_by(desc(DialogTable.create_time))
            return session.exec(sql).all()

    @classmethod
    async def get_agent_by_dialog_id(cls, dialog_id: str):
        with session_getter() as session:
            sql = select(DialogTable).where(DialogTable.dialog_id == dialog_id)
            return session.exec(sql).first()

    @classmethod
    async def update_dialog_time(cls, dialog_id: str):
        with session_getter() as session:
            sql = update(DialogTable).where(DialogTable.dialog_id == dialog_id).values(update_time=datetime.now(timezone.utc))
            session.exec(sql)
            session.flush()

    @classmethod
    async def delete_dialog_by_id(cls, dialog_id: str):
        with session_getter() as session:
            sql = delete(DialogTable).where(DialogTable.dialog_id == dialog_id)
            session.exec(sql)
            session.flush()

    @classmethod
    async def check_dialog_iscustom(cls, dialog_id: str):
        with session_getter() as session:
            sql = select(DialogTable).where(DialogTable.dialog_id == dialog_id)
            return session.exec(sql).first()

    @classmethod
    async def delete_from_agent_id(cls, agent_id):
        with session_getter() as session:
            sql = delete(DialogTable).where(DialogTable.agent_id == agent_id)
            session.exec(sql)
            session.flush()

    @classmethod
    async def reassign_agent_id(cls, source_agent_id: str, target_agent_id: str):
        with session_getter() as session:
            sql = update(DialogTable).where(DialogTable.agent_id == source_agent_id).values(agent_id=target_agent_id)
            session.exec(sql)
            session.flush()


__all__ = ["DialogDao"]
