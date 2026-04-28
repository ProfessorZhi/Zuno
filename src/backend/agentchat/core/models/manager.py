from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from agentchat.core.models.embedding import EmbeddingModel
from agentchat.core.models.reason_model import ReasoningModel
from agentchat.database.dao.llm import LLMDao
from agentchat.schema.common import ModelConfig
from agentchat.settings import app_settings


class ModelManager:
    @staticmethod
    def _require_model_config(model_config, label: str):
        if not model_config.is_configured():
            raise ValueError(f"{label} 未配置，请先在系统中新增模型配置")
        return model_config

    @classmethod
    def get_model_config(cls, model_slot: str, label: str) -> ModelConfig:
        slot_model = LLMDao.get_llm_by_slot(model_slot)
        if slot_model:
            return ModelConfig(
                model_name=slot_model.model,
                api_key=slot_model.api_key,
                base_url=slot_model.base_url,
            )

        fallback_config = getattr(app_settings.multi_models, model_slot, ModelConfig())
        return cls._require_model_config(fallback_config, label)

    @classmethod
    def get_tool_invocation_model(cls, **kwargs) -> BaseChatModel:
        tool_call_model = cls._require_model_config(
            app_settings.multi_models.tool_call_model,
            "工具调用模型",
        )

        return ChatOpenAI(
            stream_usage=True,
            model=tool_call_model.model_name,
            api_key=tool_call_model.api_key,
            base_url=tool_call_model.base_url,
        )

    @classmethod
    def get_conversation_model(cls, **kwargs) -> BaseChatModel:
        conversation_model = cls.get_model_config("conversation_model", "对话模型")

        return ChatOpenAI(
            stream_usage=True,
            model=conversation_model.model_name,
            api_key=conversation_model.api_key,
            base_url=conversation_model.base_url,
        )

    @classmethod
    def get_reasoning_model(cls) -> ReasoningModel:
        reasoning_model = cls._require_model_config(
            app_settings.multi_models.reasoning_model,
            "推理模型",
        )

        return ReasoningModel(
            model_name=reasoning_model.model_name,
            api_key=reasoning_model.api_key,
            base_url=reasoning_model.base_url,
        )

    @classmethod
    def get_qwen_vl_model(cls) -> BaseChatModel:
        qwen_vl_model = cls._require_model_config(
            app_settings.multi_models.qwen_vl,
            "视觉模型",
        )

        return ChatOpenAI(
            stream_usage=True,
            model=qwen_vl_model.model_name,
            api_key=qwen_vl_model.api_key,
            base_url=qwen_vl_model.base_url,
        )

    @classmethod
    def get_user_model(cls, **kwargs) -> BaseChatModel:
        user_model = kwargs

        return ChatOpenAI(
            stream_usage=True,
            model=user_model.get("model"),
            api_key=user_model.get("api_key"),
            base_url=user_model.get("base_url"),
        )

    @classmethod
    def get_embedding_model(cls) -> EmbeddingModel:
        embedding_model = cls.get_model_config("embedding", "Embedding 模型")

        return EmbeddingModel(
            model=embedding_model.model_name,
            base_url=embedding_model.base_url,
            api_key=embedding_model.api_key,
        )
