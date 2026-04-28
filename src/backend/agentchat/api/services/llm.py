from loguru import logger
from agentchat.database.dao.llm import LLMDao
from agentchat.database.models.user import AdminUser, SystemUser

LLM_Types = ['LLM', 'Embedding', 'Rerank']
MODEL_SLOTS = {
    "conversation_model": {"llm_types": {"LLM"}, "label": "聊天模型"},
    "embedding": {"llm_types": {"Embedding"}, "label": "文本 Embedding 模型"},
    "vl_embedding": {"llm_types": {"Embedding"}, "label": "VL Embedding 模型"},
    "rerank": {"llm_types": {"Rerank"}, "label": "Rerank 模型"},
}


class LLMService:
    @staticmethod
    def normalize_llm_type(llm_type: str | None) -> str:
        if llm_type == "Reranker":
            return "Rerank"
        return llm_type or "LLM"

    @classmethod
    async def create_llm(cls, **kwargs):
        if "llm_type" in kwargs:
            kwargs["llm_type"] = cls.normalize_llm_type(kwargs["llm_type"])
        await LLMDao.create_llm(**kwargs)

    @classmethod
    async def delete_llm(cls, llm_id: str):
        await LLMDao.delete_llm(llm_id)

    @classmethod
    async def verify_user_permission(cls, llm_id: str, user_id: str):
        owner_id = await cls.get_user_id_by_llm(llm_id)
        if user_id not in (AdminUser, owner_id):
            raise ValueError("没有权限访问")

    @classmethod
    async def get_user_id_by_llm(cls, llm_id: str):
        llm = await LLMDao.get_user_id_by_llm(llm_id)
        return llm.user_id

    @classmethod
    async def update_llm(cls, **kwargs):
        if "llm_type" in kwargs:
            kwargs["llm_type"] = cls.normalize_llm_type(kwargs["llm_type"])
        await LLMDao.update_llm(**kwargs)

    @classmethod
    def validate_model_slot(cls, llm_type: str, model_slot: str):
        slot_config = MODEL_SLOTS.get(model_slot)
        if not slot_config:
            raise ValueError("不支持的模型槽位")

        normalized_type = cls.normalize_llm_type(llm_type)
        if normalized_type not in slot_config["llm_types"]:
            raise ValueError(f"{slot_config['label']} 只能绑定 {', '.join(slot_config['llm_types'])} 类型")

    @classmethod
    async def activate_model_slot(cls, llm_id: str, model_slot: str):
        llm = await LLMDao.get_llm_by_id(llm_id)
        if not llm:
            raise ValueError("模型不存在")

        cls.validate_model_slot(llm.llm_type, model_slot)
        await LLMDao.clear_model_slot(model_slot)
        await LLMDao.update_llm(llm_id=llm_id, model_slot=model_slot)

    @staticmethod
    def _group_by_type(llms: list, hide_api_key: bool = False):
        resp = {t: [] for t in LLM_Types}
        for item in llms:
            item["llm_type"] = LLMService.normalize_llm_type(item.get("llm_type"))
            if hide_api_key:
                item["api_key"] = "************"
            resp[item["llm_type"]].append(item)
        return resp

    @classmethod
    async def get_personal_llm(cls, user_id: str):
        llms = await LLMDao.get_llm_by_user(user_id)
        result = [llm.to_dict() for llm in llms]

        for r in result:
            if r["user_id"] == SystemUser:
                r["api_key"] = "************"

        return cls._group_by_type(result)

    @classmethod
    async def get_visible_llm(cls, user_id: str):
        user_llms = await LLMDao.get_llm_by_user(user_id)
        system_llms = await LLMDao.get_llm_by_user(SystemUser)

        result = [llm.to_dict() for llm in (user_llms + system_llms)]
        for r in result:
            if r["user_id"] == SystemUser:
                r["api_key"] = "************"

        return cls._group_by_type(result)

    @classmethod
    async def get_all_llm(cls, user_id):
        if user_id != AdminUser:
            raise ValueError("无权限访问模型数据")
        llms = await LLMDao.get_all_llm()
        result = [llm.to_dict() for llm in llms]
        return cls._group_by_type(result, hide_api_key=True)

    @classmethod
    async def get_llm_by_id(cls, llm_id: str):
        llm = await LLMDao.get_llm_by_id(llm_id)
        return llm.to_dict() if llm else None

    @classmethod
    async def get_one_llm(cls):
        llms = await LLMDao.get_all_llm()
        return llms[0].to_dict() if llms else None

    @classmethod
    async def get_llm_type(cls):
        llms = await LLMDao.get_llm_by_type('LLM')
        return [llm.to_dict() for llm in llms]

    @classmethod
    async def get_llm_id_from_name(
        cls,
        llm_name: str,
        user_id: str
    ):
        llm = await LLMDao.get_llm_id_from_name(llm_name, user_id)
        if llm:
            return llm.llm_id
        llm = await LLMDao.get_llm_id_from_name(llm_name, SystemUser)
        return llm.llm_id if llm else None

    @classmethod
    async def search_llms_by_name(
        cls,
        user_id,
        llm_name
    ):
        results = await LLMDao.search_llms_by_name(user_id, llm_name)
        return [result.to_dict(["api_key"]) for result in results]

