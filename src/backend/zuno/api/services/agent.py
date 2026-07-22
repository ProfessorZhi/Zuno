from zuno.database import AgentTable
from zuno.database.dao.agent import AgentDao
from zuno.database.dao.dialog import DialogDao
from zuno.database.models.user import AdminUser, SystemUser
from zuno.schema.agent import AgentCreateReq
from zuno.api.services.security_admin_actions import require_admin_action_authorized

HIDDEN_SYSTEM_AGENT_NAMES = {"联网搜索助手", "博查搜索助手"}
ADMIN_AGENT_ACTIONS = {
    "access": "admin.agent.access",
    "delete": "admin.agent.delete",
    "update": "admin.agent.update",
}


class AgentService:
    @staticmethod
    def _to_dict_list(results):
        return [res.to_dict() for res in results] if results else []

    @staticmethod
    def _dedupe_agents(agents: list[dict]):
        deduped = []
        seen = set()
        for agent in agents:
            if agent.get("user_id") != SystemUser:
                deduped.append(agent)
                continue
            key = (agent.get("user_id"), agent.get("name"))
            if key in seen:
                continue
            seen.add(key)
            deduped.append(agent)
        return deduped

    @staticmethod
    def _filter_hidden_system_agents(agents: list[dict]):
        return [
            agent for agent in agents
            if not (
                agent.get("user_id") == SystemUser
                and agent.get("name") in HIDDEN_SYSTEM_AGENT_NAMES
            )
        ]

    @staticmethod
    def _agent_request_to_db_values(req: AgentCreateReq) -> dict:
        values = req.model_dump()
        graphrag_project_id = values.pop("graphrag_project_id", None)
        if graphrag_project_id:
            values["domain_pack_id"] = graphrag_project_id
        return values

    @staticmethod
    def _agent_update_to_db_values(update_values: dict) -> dict:
        values = dict(update_values)
        graphrag_project_id = values.pop("graphrag_project_id", None)
        if graphrag_project_id is not None:
            values["domain_pack_id"] = graphrag_project_id
        return values

    @classmethod
    async def _check_permission(cls, agent_id: str, user_id: str, *, action: str = "admin.agent.access"):
        owner_id = await cls.get_agent_user_id(agent_id)
        if user_id == AdminUser:
            if owner_id != AdminUser:
                require_admin_action_authorized(
                    principal_id=user_id,
                    action=action,
                    resource_ref=f"agent:{agent_id}",
                )
            return
        if user_id != owner_id:
            raise ValueError("没有权限访问")

    @classmethod
    async def create_agent(cls, login_user, req: AgentCreateReq):
        agent = AgentTable(**cls._agent_request_to_db_values(req), user_id=login_user.user_id)
        return await AgentDao.create_agent(agent)

    @classmethod
    async def update_agent(cls, agent_id: str, update_values: dict, user_id: str):
        await cls._check_permission(agent_id, user_id, action="admin.agent.update")
        if not update_values:
            return
        await AgentDao.update_agent_by_id(
            agent_id=agent_id,
            update_values=cls._agent_update_to_db_values(update_values),
        )

    @classmethod
    async def delete_agent_by_id(cls, id: str):
        await AgentDao.delete_agent_by_id(id=id)
        await DialogDao.delete_from_agent_id(id)

    @classmethod
    async def get_agent(cls):
        results = await AgentDao.get_agent()
        return cls._to_dict_list(results)

    @classmethod
    async def get_agent_user_id(cls, agent_id: str):
        agent = await AgentDao.get_agent_user_id(agent_id=agent_id)
        return agent.user_id

    @classmethod
    async def verify_user_permission(cls, id, user_id, action: str = "update"):
        await cls._check_permission(id, user_id, action=ADMIN_AGENT_ACTIONS.get(action, "admin.agent.access"))

    @classmethod
    async def search_agent_name(cls, name: str, user_id: str):
        results = await AgentDao.search_agent_name(name=name, user_id=user_id)
        return [agent for agent in cls._to_dict_list(results) if agent.get("user_id") == user_id]

    @classmethod
    async def check_repeat_name(cls, name: str, user_id: str):
        result = await AgentDao.check_repeat_name(name=name, user_id=user_id)
        return bool(result)

    @classmethod
    async def check_name_iscustom(cls, name: str):
        agent = await AgentDao.select_agent_by_name(name=name)
        return agent.is_custom if agent else False

    @classmethod
    async def get_personal_agent_by_user_id(cls, user_id: str):
        results = await AgentDao.get_agent_by_user_id(user_id=user_id)
        return cls._filter_hidden_system_agents(
            cls._dedupe_agents(cls._to_dict_list(results))
        )

    @classmethod
    async def get_all_agent_by_user_id(cls, user_id: str):
        user_results = await AgentDao.get_agent_by_user_id(user_id=user_id)
        return cls._filter_hidden_system_agents(
            cls._dedupe_agents(cls._to_dict_list(user_results))
        )

    @classmethod
    async def select_agent_by_custom(cls, is_custom):
        results = await AgentDao.select_agent_by_custom(is_custom=is_custom)
        return cls._to_dict_list(results)

    @classmethod
    async def select_agent_by_name(cls, name: str):
        results = await AgentDao.select_agent_by_name(name)
        return cls._to_dict_list(results)

    @classmethod
    async def select_agent_by_id(cls, agent_id: str):
        agent = await AgentDao.select_agent_by_id(agent_id=agent_id)
        return agent.to_dict() if agent else None

    @classmethod
    async def get_agents_by_name_and_user_id(cls, name: str, user_id: str):
        results = await AgentDao.select_agents_by_name_and_user_id(name, user_id)
        return cls._to_dict_list(results)


__all__ = ["AgentService", "HIDDEN_SYSTEM_AGENT_NAMES"]
