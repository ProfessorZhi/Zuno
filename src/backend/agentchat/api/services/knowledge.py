from copy import deepcopy
from typing import Any, List

from agentchat.database.dao.knowledge import KnowledgeDao
from agentchat.database.dao.knowledge_file import KnowledgeFileDao
from agentchat.database.dao.llm import LLMDao
from agentchat.database.models.user import AdminUser
from agentchat.utils.file_utils import format_file_size

DEFAULT_KNOWLEDGE_CONFIG = {
    "model_refs": {
        "text_embedding_model_id": None,
        "vl_embedding_model_id": None,
        "rerank_model_id": None,
    },
    "index_settings": {
        "chunk_mode": "general",
        "chunk_size": 1024,
        "overlap": 120,
        "separator": "\n\n",
        "replace_consecutive_spaces": True,
        "remove_urls_emails": False,
        "image_indexing_mode": "dual",
    },
    "retrieval_settings": {
        "default_mode": "hybrid",
        "top_k": 5,
        "rerank_enabled": True,
        "rerank_top_k": 4,
        "score_threshold": None,
    },
}


class KnowledgeService:
    @staticmethod
    def _looks_encoding_damaged(value: str | None) -> bool:
        if not value:
            return False

        text = str(value).strip()
        if not text:
            return False

        question_count = text.count("?")
        if question_count < 3 and "??" not in text:
            return False

        non_space_count = sum(1 for char in text if not char.isspace())
        if not non_space_count:
            return False

        return question_count / non_space_count >= 0.25 or "???" in text

    @classmethod
    def _validate_text_not_encoding_damaged(cls, field_label: str, value: str | None) -> None:
        if cls._looks_encoding_damaged(value):
            raise ValueError(
                f"{field_label} 疑似发生编码损坏，内容里出现大量问号。"
                "请确认输入链路使用 UTF-8 后重新填写。"
            )

    @staticmethod
    def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        merged = deepcopy(base)
        for key, value in (override or {}).items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = KnowledgeService._deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged

    @classmethod
    def _normalize_knowledge_config(
        cls,
        knowledge_config: dict[str, Any] | None,
        legacy_default_mode: str | None = None,
    ) -> dict[str, Any]:
        normalized = deepcopy(DEFAULT_KNOWLEDGE_CONFIG)
        if knowledge_config:
            normalized = cls._deep_merge(normalized, knowledge_config)
        if legacy_default_mode and not (
            (knowledge_config or {}).get("retrieval_settings", {}).get("default_mode")
        ):
            normalized["retrieval_settings"]["default_mode"] = legacy_default_mode
        return normalized

    @classmethod
    def _sanitize_knowledge_payload(cls, knowledge: dict) -> dict:
        sanitized = dict(knowledge)
        legacy_default_mode = sanitized.pop("default_retrieval_mode", None)
        sanitized["knowledge_config"] = cls._normalize_knowledge_config(
            sanitized.get("knowledge_config"),
            legacy_default_mode,
        )
        return sanitized

    @classmethod
    async def create_knowledge(cls, knowledge_name, knowledge_desc, user_id, knowledge_config=None):
        try:
            cls._validate_text_not_encoding_damaged("知识库名称", knowledge_name)
            cls._validate_text_not_encoding_damaged("知识库说明", knowledge_desc)
            normalized_config = cls._normalize_knowledge_config(knowledge_config)
            await KnowledgeDao.create_knowledge(
                knowledge_name,
                knowledge_desc,
                user_id,
                default_retrieval_mode=normalized_config["retrieval_settings"]["default_mode"],
                knowledge_config=normalized_config,
            )
        except Exception as err:
            raise ValueError(f"Create Knowledge Error: {err}")

    @classmethod
    async def select_knowledge(cls, user_id):
        try:
            if user_id == AdminUser:
                knowledges = await cls._select_all_knowledge()
            else:
                knowledges = await KnowledgeDao.get_knowledge_by_user(user_id)
                knowledges = [cls._sanitize_knowledge_payload(knowledge.to_dict()) for knowledge in knowledges]
            for knowledge in knowledges:
                knowledge_files = await KnowledgeFileDao.select_knowledge_file(knowledge["id"])
                knowledge["count"] = len(knowledge_files)
                file_sizes = 0
                processing_count = 0
                failed_count = 0
                completed_count = 0
                for file in knowledge_files:
                    file_sizes += file.file_size
                    status_values = [
                        str(getattr(file, "status", "")).lower(),
                        str(getattr(file, "parse_status", "")).lower(),
                        str(getattr(file, "rag_index_status", "")).lower(),
                        str(getattr(file, "graph_index_status", "")).lower(),
                    ]
                    if any(value in status for status in status_values for value in ["process", "pending", "queued", "running"]):
                        processing_count += 1
                    elif getattr(file, "last_error", None) or any("fail" in status for status in status_values):
                        failed_count += 1
                    else:
                        completed_count += 1
                knowledge["file_size"] = format_file_size(file_sizes)
                knowledge["processing_count"] = processing_count
                knowledge["failed_count"] = failed_count
                knowledge["completed_count"] = completed_count
            return knowledges
        except Exception as err:
            raise ValueError(f"Select Knowledge By User Error: {err}")

    @classmethod
    async def _select_all_knowledge(cls):
        try:
            results = await KnowledgeDao.get_all_knowledge()
            return [cls._sanitize_knowledge_payload(res.to_dict()) for res in results]
        except Exception as err:
            raise ValueError(f"Delete Knowledge By ID Error: {err}")

    @classmethod
    async def delete_knowledge(cls, knowledge_id):
        try:
            await KnowledgeDao.delete_knowledge_by_id(knowledge_id)
        except Exception as err:
            raise ValueError(f"Delete Knowledge By ID Error: {err}")

    @classmethod
    async def verify_user_permission(cls, knowledge_id, user_id):
        knowledge_user_id = await cls.select_user_by_id(knowledge_id)
        if user_id != knowledge_user_id and user_id != AdminUser:
            raise ValueError("No permission for this knowledge")

    @classmethod
    async def update_knowledge(cls, knowledge_id, knowledge_name, knowledge_desc, knowledge_config=None):
        try:
            cls._validate_text_not_encoding_damaged("知识库名称", knowledge_name)
            cls._validate_text_not_encoding_damaged("知识库说明", knowledge_desc)
            normalized_config = None
            if knowledge_config is not None:
                current_knowledge = await KnowledgeDao.select_user_by_id(knowledge_id)
                current_payload = current_knowledge.to_dict() if current_knowledge else {}
                base_config = cls._normalize_knowledge_config(
                    current_payload.get("knowledge_config"),
                    current_payload.get("default_retrieval_mode"),
                )
                normalized_config = cls._normalize_knowledge_config(
                    cls._deep_merge(base_config, knowledge_config)
                )

            await KnowledgeDao.update_knowledge_by_id(
                knowledge_id,
                knowledge_desc,
                knowledge_name,
                default_retrieval_mode=(
                    normalized_config["retrieval_settings"]["default_mode"]
                    if normalized_config is not None
                    else None
                ),
                knowledge_config=normalized_config,
            )
        except Exception as err:
            raise ValueError(f"Update Knowledge Error: {err}")

    @classmethod
    async def get_knowledge_config(cls, knowledge_id: str) -> dict[str, Any]:
        try:
            knowledge = await KnowledgeDao.select_user_by_id(knowledge_id)
            if not knowledge:
                return deepcopy(DEFAULT_KNOWLEDGE_CONFIG)
            payload = knowledge.to_dict()
            return cls._normalize_knowledge_config(
                payload.get("knowledge_config"),
                payload.get("default_retrieval_mode"),
            )
        except Exception as err:
            raise ValueError(f"Get Knowledge Config Error: {err}")

    @classmethod
    async def get_knowledge_payload(cls, knowledge_id: str) -> dict[str, Any]:
        try:
            knowledge = await KnowledgeDao.select_user_by_id(knowledge_id)
            if not knowledge:
                raise ValueError("knowledge not found")
            return cls._sanitize_knowledge_payload(knowledge.to_dict())
        except Exception as err:
            raise ValueError(f"Get Knowledge Payload Error: {err}")

    @classmethod
    async def resolve_model_config_by_id(cls, llm_id: str | None):
        if not llm_id:
            return None
        llm = await LLMDao.get_llm_by_id(llm_id)
        if not llm:
            return None
        return {
            "model_name": llm.model,
            "api_key": llm.api_key,
            "base_url": llm.base_url,
            "provider": llm.provider,
            "llm_type": llm.llm_type,
            "llm_id": llm.llm_id,
        }

    @classmethod
    async def get_runtime_settings(cls, knowledge_id: str) -> dict[str, Any]:
        payload = await cls.get_knowledge_payload(knowledge_id)
        config = payload["knowledge_config"]
        model_refs = config.get("model_refs", {})

        return {
            "knowledge_id": knowledge_id,
            "knowledge_config": config,
            "text_embedding_config": await cls.resolve_model_config_by_id(model_refs.get("text_embedding_model_id")),
            "vl_embedding_config": await cls.resolve_model_config_by_id(model_refs.get("vl_embedding_model_id")),
            "rerank_config": await cls.resolve_model_config_by_id(model_refs.get("rerank_model_id")),
        }

    @classmethod
    async def select_user_by_id(cls, knowledge_id):
        try:
            knowledge = await KnowledgeDao.select_user_by_id(knowledge_id)
            return knowledge.user_id
        except Exception as err:
            raise ValueError(f"Select user id error :{err}")

    @classmethod
    async def get_knowledge_ids_from_name(cls, knowledges_name: List[str], user_id):
        try:
            knowledges = await KnowledgeDao.get_knowledge_ids_from_name(knowledges_name, user_id)
            return [knowledge.id for knowledge in knowledges]
        except Exception as err:
            raise ValueError(f"Get knowledges id form name error:{err}")
