from langchain_core.language_models import BaseChatModel

from zuno.core.models.embedding import EmbeddingModel
from zuno.core.models.reason_model import ReasoningModel
from zuno.database.dao.llm import LLMDao
from zuno.platform.model_gateway import build_openai_chat_gateway_model
from zuno.schema.common import ModelConfig
from zuno.settings import app_settings
from zuno.utils.model_output import normalize_model_id_for_provider


class ModelManager:
    @staticmethod
    def _require_model_config(model_config, label: str):
        if not model_config.is_configured():
            raise ValueError(f"{label} 鏈厤缃紝璇峰厛鍦ㄧ郴缁熶腑鏂板妯″瀷閰嶇疆")
        return model_config

    @classmethod
    def get_model_config(cls, model_slot: str, label: str) -> ModelConfig:
        slot_model = LLMDao.get_llm_by_slot(model_slot)
        if slot_model:
            return ModelConfig(
                model_name=normalize_model_id_for_provider(
                    slot_model.model,
                    provider=slot_model.provider,
                    base_url=slot_model.base_url,
                ),
                api_key=slot_model.api_key,
                base_url=slot_model.base_url,
            )

        fallback_config = getattr(app_settings.multi_models, model_slot, ModelConfig())
        return cls._require_model_config(fallback_config, label)

    @classmethod
    def get_tool_invocation_model(cls, **kwargs) -> BaseChatModel:
        tool_call_model = cls.get_model_config("tool_call_model", "宸ュ叿璋冪敤妯″瀷")
        model_name = normalize_model_id_for_provider(
            tool_call_model.model_name,
            base_url=tool_call_model.base_url,
        )
        return build_openai_chat_gateway_model(
            stream_usage=True,
            model=model_name,
            api_key=tool_call_model.api_key,
            base_url=tool_call_model.base_url,
        )

    @classmethod
    def get_conversation_model(cls, **kwargs) -> BaseChatModel:
        conversation_model = cls.get_model_config("conversation_model", "瀵硅瘽妯″瀷")
        return build_openai_chat_gateway_model(
            stream_usage=True,
            model=conversation_model.model_name,
            api_key=conversation_model.api_key,
            base_url=conversation_model.base_url,
        )

    @classmethod
    def get_reasoning_model(cls) -> ReasoningModel:
        reasoning_model = cls.get_model_config("reasoning_model", "鎺ㄧ悊妯″瀷")
        return ReasoningModel(
            model_name=normalize_model_id_for_provider(
                reasoning_model.model_name,
                base_url=reasoning_model.base_url,
            ),
            api_key=reasoning_model.api_key,
            base_url=reasoning_model.base_url,
        )

    @classmethod
    def get_qwen_vl_model(cls) -> BaseChatModel:
        qwen_vl_model = cls._require_model_config(
            app_settings.multi_models.qwen_vl,
            "瑙嗚妯″瀷",
        )
        return build_openai_chat_gateway_model(
            stream_usage=True,
            model=normalize_model_id_for_provider(
                qwen_vl_model.model_name,
                base_url=qwen_vl_model.base_url,
            ),
            api_key=qwen_vl_model.api_key,
            base_url=qwen_vl_model.base_url,
        )

    @classmethod
    def get_user_model(cls, **kwargs) -> BaseChatModel:
        user_model = kwargs
        model_name = normalize_model_id_for_provider(
            user_model.get("model"),
            provider=user_model.get("provider"),
            base_url=user_model.get("base_url"),
        )
        return build_openai_chat_gateway_model(
            stream_usage=True,
            model=model_name,
            api_key=user_model.get("api_key"),
            base_url=user_model.get("base_url"),
        )

    @classmethod
    def get_embedding_model(cls) -> EmbeddingModel:
        embedding_model = cls.get_model_config("embedding", "Embedding 妯″瀷")
        return EmbeddingModel(
            model=normalize_model_id_for_provider(
                embedding_model.model_name,
                base_url=embedding_model.base_url,
            ),
            base_url=embedding_model.base_url,
            api_key=embedding_model.api_key,
        )


__all__ = ["ModelManager"]
