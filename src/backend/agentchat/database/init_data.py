from zuno.database import SystemUser
from zuno.database.init_data import cleanup_duplicate_system_data
from zuno.database.init_data import insert_agent_to_mysql
from zuno.database.init_data import insert_llm_to_mysql
from zuno.database.init_data import insert_tools_to_mysql


async def init_default_agent():
    await cleanup_duplicate_system_data()
    await insert_tools_to_mysql()
    await insert_llm_to_mysql()


async def cleanup_legacy_seeded_system_agents():
    from agentchat.api.services.agent import AgentService
    from agentchat.database.dao.agent import AgentDao

    system_agents = await AgentService.get_personal_agent_by_user_id(SystemUser)
    deleted_count = 0
    for agent in system_agents:
        if agent.get("is_custom") is False:
            await AgentDao.delete_agent_by_id(agent["id"])
            deleted_count += 1
    return deleted_count
