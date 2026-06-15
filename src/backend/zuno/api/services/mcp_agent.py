from typing import List

from loguru import logger

from zuno.database.dao.mcp_agent import MCPAgentDao
from zuno.database.models.user import AdminUser, SystemUser
from zuno.schema.schemas import resp_200, resp_500


class MCPAgentService:
    @classmethod
    def create_mcp_agent(
        cls,
        name: str,
        description: str,
        logo: str,
        user_id: str,
        knowledges_id: List[str],
        llm_id: str,
        mcp_servers_id: List[str],
        enable_memory: bool,
        is_custom: bool = True,
    ):
        try:
            return MCPAgentDao.create_mcp_agent(
                name=name,
                description=description,
                logo=logo,
                llm_id=llm_id,
                mcp_servers_id=mcp_servers_id,
                user_id=user_id,
                knowledges_id=knowledges_id,
                is_custom=is_custom,
                enable_memory=enable_memory,
            )
        except Exception as err:
            logger.error(f"create agent appears error: {err}")

    @classmethod
    def get_mcp_agent(cls):
        try:
            return list(MCPAgentDao.get_mcp_agent())
        except Exception as err:
            logger.error(f"get agent appears error: {err}")

    @classmethod
    def update_mcp_agent_by_id(
        cls,
        id: str,
        name: str,
        description: str,
        user_id: str,
        logo: str,
        mcp_servers_id: List[str],
        knowledges_id: List[str],
        llm_id: str,
        enable_memory: bool,
    ):
        try:
            if user_id == AdminUser or user_id == cls.get_agent_user_id(agent_id=id):
                MCPAgentDao.update_mcp_agent_by_id(
                    id=id,
                    name=name,
                    logo=logo,
                    description=description,
                    knowledges_id=knowledges_id,
                    mcp_servers_id=mcp_servers_id,
                    llm_id=llm_id,
                    enable_memory=enable_memory,
                )
                return resp_200(message="update agent success")
            return resp_500(message="no permission exec")
        except Exception as err:
            logger.error(f"update agent by id appears error: {err}")

    @classmethod
    def get_agent_user_id(cls, agent_id: str):
        try:
            agent = MCPAgentDao.get_mcp_agent_user_id(agent_id=agent_id)
            return agent.user_id
        except Exception as err:
            logger.error(f"get agent user id error: {err}")

    @classmethod
    def delete_mcp_agent_by_id(cls, id: str, user_id: str):
        try:
            if user_id == AdminUser or user_id == cls.get_agent_user_id(agent_id=id):
                MCPAgentDao.delete_mcp_agent_by_id(id=id)
                return resp_200(message="delete success")
            return resp_500(message="no permission exec")
        except Exception as err:
            logger.error(f"delete agent by id error: {err}")

    @classmethod
    def search_mcp_agent_name(cls, name: str, user_id: str):
        try:
            return list(MCPAgentDao.search_mcp_agent_name(name=name, user_id=user_id))
        except Exception as err:
            logger.error(f"search agent name error: {err}")

    @classmethod
    def check_repeat_name(cls, name: str, user_id: str):
        try:
            result = MCPAgentDao.check_repeat_name(name=name, user_id=user_id)
            return len(result) != 0
        except Exception as err:
            logger.error(f"check repeat agent name error: {err}")

    @classmethod
    def check_name_iscustom(cls, name: str):
        try:
            agent = MCPAgentDao.select_mcp_agent_by_name(name)
            return agent.is_custom
        except Exception as err:
            logger.error(f"get code by name error: {err}")

    @classmethod
    def get_personal_mcp_agent_by_user(cls, user_id: str):
        try:
            return list(MCPAgentDao.get_mcp_agent_by_user_id(user_id=user_id))
        except Exception as err:
            logger.error(f"get personal agent by user id error: {err}")

    @classmethod
    def get_all_mcp_agent_by_user(cls, user_id: str):
        try:
            system_data = MCPAgentDao.get_mcp_agent_by_user_id(user_id=SystemUser)
            user_data = MCPAgentDao.get_mcp_agent_by_user_id(user_id=user_id)
            return list(system_data + user_data)
        except Exception as err:
            logger.error(f"get all agent by user id error: {err}")

    @classmethod
    def select_mcp_agent_by_custom(cls, is_custom: bool):
        try:
            return list(MCPAgentDao.select_mcp_agent_by_custom(is_custom=is_custom))
        except Exception as err:
            logger.error(f"select agent by custom error: {err}")

    @classmethod
    def select_mcp_agent_by_name(cls, name: str):
        try:
            data = MCPAgentDao.select_mcp_agent_by_name(name)
            return [data] if data else []
        except Exception as err:
            logger.error(f"select agent by name error: {err}")

    @classmethod
    def select_mcp_agent_by_id(cls, agent_id: str):
        try:
            return MCPAgentDao.select_mcp_agent_by_id(agent_id)
        except Exception as err:
            logger.error(f"select agent by id error: {err}")


__all__ = ["MCPAgentService"]
