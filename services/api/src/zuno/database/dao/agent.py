from sqlmodel import and_, delete, desc, select, update

from zuno.database.models.agent import AgentTable
from zuno.database.session import session_getter


class AgentDao:
    @classmethod
    async def create_agent(cls, agent: AgentTable):
        with session_getter() as session:
            session.add(agent)
            session.commit()
            session.refresh(agent)
            return agent

    @classmethod
    async def get_agent(cls):
        with session_getter() as session:
            statement = select(AgentTable).order_by(desc(AgentTable.create_time))
            return session.exec(statement).all()

    @classmethod
    async def select_agent_by_name(cls, name: str):
        with session_getter() as session:
            statement = select(AgentTable).where(AgentTable.name == name)
            return session.exec(statement).first()

    @classmethod
    async def select_agents_by_name_and_user_id(cls, name: str, user_id: str):
        with session_getter() as session:
            statement = select(AgentTable).where(
                and_(
                    AgentTable.name == name,
                    AgentTable.user_id == user_id,
                )
            )
            return session.exec(statement).all()

    @classmethod
    async def get_agent_user_id(cls, agent_id: str):
        with session_getter() as session:
            statement = select(AgentTable).where(AgentTable.id == agent_id)
            return session.exec(statement).first()

    @classmethod
    async def select_agent_by_custom(cls, is_custom: bool):
        with session_getter() as session:
            statement = select(AgentTable).where(AgentTable.is_custom == is_custom)
            return session.exec(statement).all()

    @classmethod
    async def delete_agent_by_id(cls, id: str):
        with session_getter() as session:
            statement = delete(AgentTable).where(AgentTable.id == id)
            session.exec(statement)
            session.commit()

    @classmethod
    async def _get_logo_by_id(cls, id: str):
        with session_getter() as session:
            statement = select(AgentTable).where(AgentTable.id == id)
            result = session.exec(statement).all()
            return result[0][0].logo_url

    @classmethod
    async def check_repeat_name(cls, name: str, user_id: str):
        with session_getter() as session:
            statement = select(AgentTable).where(
                and_(
                    AgentTable.name == name,
                    AgentTable.user_id == user_id,
                )
            )
            return session.exec(statement).all()

    @classmethod
    async def search_agent_name(cls, name: str, user_id: str):
        with session_getter() as session:
            statement = select(AgentTable).where(
                and_(
                    AgentTable.name.like(f"%{name}%"),
                    AgentTable.user_id == user_id,
                )
            )
            return session.exec(statement).all()

    @classmethod
    async def get_agent_by_user_id(cls, user_id: str):
        with session_getter() as session:
            statement = select(AgentTable).where(AgentTable.user_id == user_id)
            return session.exec(statement).all()

    @classmethod
    async def select_agent_by_id(cls, agent_id: str):
        with session_getter() as session:
            statement = select(AgentTable).where(AgentTable.id == agent_id)
            return session.exec(statement).first()

    @classmethod
    async def update_agent_by_id(cls, agent_id: str, update_values: dict):
        with session_getter() as session:
            statement = update(AgentTable).where(AgentTable.id == agent_id).values(**update_values)
            session.exec(statement)
            session.commit()


__all__ = ["AgentDao"]
