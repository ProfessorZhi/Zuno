from typing import List

from sqlmodel import delete, select

from zuno.database.models.history import HistoryTable
from zuno.platform.database.session import session_getter


class HistoryDao:
    @classmethod
    async def _get_history_sql(cls, role: str, content: str, events: List[dict], dialog_id: str):
        return HistoryTable(content=content, role=role, events=events, dialog_id=dialog_id)

    @classmethod
    async def create_history(cls, role: str, content: str, events: List[dict], dialog_id: str):
        with session_getter() as session:
            session.add(await cls._get_history_sql(role, content, events, dialog_id))
            session.flush()

    @classmethod
    async def select_history_from_time(cls, dialog_id: str, k: int):
        with session_getter() as session:
            sql = select(HistoryTable).where(HistoryTable.dialog_id == dialog_id).order_by(HistoryTable.create_time.desc())
            result = session.exec(sql).all()
            if len(result) > k:
                result = result[:k]
            result.reverse()
            return result

    @classmethod
    async def get_dialog_history(cls, dialog_id: str):
        with session_getter() as session:
            sql = select(HistoryTable).where(HistoryTable.dialog_id == dialog_id).order_by(HistoryTable.create_time)
            return session.exec(sql).all()

    @classmethod
    async def delete_history_by_dialog_id(cls, dialog_id: str):
        with session_getter() as session:
            sql = delete(HistoryTable).where(HistoryTable.dialog_id == dialog_id)
            session.exec(sql)
            session.flush()


__all__ = ["HistoryDao"]
