from sqlmodel import select

from zuno.database.models.message import MessageDownTable, MessageLikeTable
from zuno.platform.database.session import session_getter


class MessageLikeDao:
    @classmethod
    def _get_message_like_sql(cls, user_input: str, agent_output: str):
        return MessageLikeTable(user_input=user_input, agent_output=agent_output)

    @classmethod
    def create_message_like(cls, user_input: str, agent_output: str):
        with session_getter() as session:
            record = cls._get_message_like_sql(user_input, agent_output)
            session.add(record)
            session.flush()
            return record

    @classmethod
    def get_message_like(cls):
        with session_getter() as session:
            sql = select(MessageLikeTable)
            return session.exec(sql).all()


class MessageDownDao:
    @classmethod
    def _get_message_down_sql(cls, user_input: str, agent_output: str):
        return MessageDownTable(user_input=user_input, agent_output=agent_output)

    @classmethod
    def create_message_down(cls, user_input: str, agent_output: str):
        with session_getter() as session:
            session.add(cls._get_message_down_sql(user_input, agent_output))
            session.flush()

    @classmethod
    def get_message_down(cls):
        with session_getter() as session:
            sql = select(MessageDownTable)
            return session.exec(sql).all()


__all__ = ["MessageDownDao", "MessageLikeDao"]
