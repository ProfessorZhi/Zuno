from copy import deepcopy
from typing import Any, List

from zuno.database.dao.knowledge import KnowledgeDao
from zuno.database.dao.knowledge_file import KnowledgeFileDao
from zuno.database.dao.llm import LLMDao
from zuno.database.models.user import AdminUser
from zuno.services.domain_pack.loader import DomainPackLoader
from zuno.services.runtime_registry import get_local_runtime_settings
from zuno.utils.file_utils import format_file_size

DEFAULT_KNOWLEDGE_CONFIG = {
    "index_capability": "rag",
    "domain_pack_id": None,
    "eval_profile_id": None,
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
        "vector_backend": "milvus",
        "index_version": "v1",
        "status": "active",
        "health_status": "ready",
        "text_index_status": "ready",
        "bm25_index_status": "ready",
        "last_build_time": None,
        "last_error": None,
    },
    "graph_index_settings": {
        "entity_extraction_mode": "rule_llm",
        "relation_schema": "open",
        "entity_normalization": True,
        "evidence_backlink": True,
        "use_rag_entry_chunk": True,
        "index_version": "v1",
        "health_status": "ready",
        "graph_index_status": "ready",
        "community_detection_status": "not_built",
        "community_report_status": "not_built",
        "community_version": "v0",
    },
    "retrieval_settings": {
        "default_mode": "rag",
        "profile": "auto",
        "refill_policy": "smart",
        "top_k": 5,
        "rerank_enabled": True,
        "rerank_top_k": 4,
        "score_threshold": None,
        "graph_hop_limit": 2,
        "max_paths_per_entity": 5,
    },
}


class KnowledgeService:
    @staticmethod
    def _get_nested_value(payload: dict[str, Any], path: str) -> Any:
        current: Any = payload
        for part in path.split("."):
            if not isinstance(current, dict):
                return None
            current = current.get(part)
        return current

    @classmethod
    def _collect_changed_fields(
        cls,
        previous_config: dict[str, Any],
        next_config: dict[str, Any],
        *,
        prefix: str = "",
    ) -> list[str]:
        changed_fields: list[str] = []
        keys = set(previous_config.keys()) | set(next_config.keys())
        for key in sorted(keys):
            previous_value = previous_config.get(key)
            next_value = next_config.get(key)
            field_name = f"{prefix}.{key}" if prefix else key
            if isinstance(previous_value, dict) and isinstance(next_value, dict):
                changed_fields.extend(
                    cls._collect_changed_fields(previous_value, next_value, prefix=field_name)
                )
                continue
            if previous_value != next_value:
                changed_fields.append(field_name)
        return changed_fields

    @classmethod
    def analyze_config_impact(
        cls,
        previous_config: dict[str, Any] | None,
        next_config: dict[str, Any] | None,
    ) -> dict[str, Any]:
        previous = cls._normalize_knowledge_config(previous_config)
        next_payload = cls._normalize_knowledge_config(next_config)
        changed_fields = cls._collect_changed_fields(previous, next_payload)

        immediate_effect_fields = sorted(
            field
            for field in changed_fields
            if field.startswith("retrieval_settings.")
            or field in {"eval_profile_id", "model_refs.rerank_model_id"}
        )

        text_reindex_fields = {
            "index_capability",
            "model_refs.text_embedding_model_id",
            "model_refs.vl_embedding_model_id",
            "index_settings.chunk_mode",
            "index_settings.chunk_size",
            "index_settings.overlap",
            "index_settings.separator",
            "index_settings.replace_consecutive_spaces",
            "index_settings.remove_urls_emails",
            "index_settings.image_indexing_mode",
            "index_settings.vector_backend",
        }
        bm25_reindex_fields = {
            "index_settings.chunk_mode",
            "index_settings.chunk_size",
            "index_settings.overlap",
            "index_settings.separator",
            "index_settings.replace_consecutive_spaces",
            "index_settings.remove_urls_emails",
        }
        graph_update_fields = {
            "index_capability",
            "domain_pack_id",
            "graph_index_settings.entity_extraction_mode",
            "graph_index_settings.relation_schema",
            "graph_index_settings.entity_normalization",
            "graph_index_settings.evidence_backlink",
            "graph_index_settings.use_rag_entry_chunk",
            "index_settings.chunk_mode",
            "index_settings.chunk_size",
            "index_settings.overlap",
            "index_settings.separator",
        }
        community_report_fields = {
            "domain_pack_id",
            "eval_profile_id",
        }

        text_reindex_required = any(field in text_reindex_fields for field in changed_fields)
        bm25_reindex_required = any(field in bm25_reindex_fields for field in changed_fields)
        graph_update_required = any(field in graph_update_fields for field in changed_fields)
        community_detection_required = graph_update_required and next_payload.get("index_capability") == "rag_graph"
        community_report_required = any(field in community_report_fields for field in changed_fields) and (
            next_payload.get("index_capability") == "rag_graph"
        )
        if community_detection_required:
            community_report_required = True

        full_rebuild_required = (
            "index_capability" in changed_fields
            and previous.get("index_capability") != next_payload.get("index_capability")
        )

        recommended_action = "save_only"
        if full_rebuild_required:
            recommended_action = "full_rebuild"
        elif community_report_required:
            recommended_action = "community_report"
        elif community_detection_required:
            recommended_action = "community_detection"
        elif graph_update_required:
            recommended_action = "graph_index"
        elif bm25_reindex_required:
            recommended_action = "bm25_index"
        elif text_reindex_required:
            recommended_action = "text_index"

        return {
            "changed_fields": changed_fields,
            "immediate_effect_fields": immediate_effect_fields,
            "text_reindex_required": text_reindex_required,
            "bm25_reindex_required": bm25_reindex_required,
            "graph_update_required": graph_update_required,
            "community_detection_required": community_detection_required,
            "community_report_required": community_report_required,
            "full_rebuild_required": full_rebuild_required,
            "recommended_action": recommended_action,
        }

    @staticmethod
    def _apply_domain_pack_defaults(
        config: dict[str, Any],
        domain_pack: dict[str, Any] | None,
    ) -> dict[str, Any]:
        normalized = deepcopy(config or {})
        retrieval_settings = dict(normalized.get("retrieval_settings") or {})
        current_profile = str(retrieval_settings.get("profile") or "").strip().lower()
        if domain_pack and domain_pack.get("default_retrieval_profile") and current_profile in {"", "auto", "default"}:
            retrieval_settings["profile"] = domain_pack.get("default_retrieval_profile")
        normalized["retrieval_settings"] = retrieval_settings
        if domain_pack and domain_pack.get("default_eval_profile_id") and not normalized.get("eval_profile_id"):
            normalized["eval_profile_id"] = domain_pack.get("default_eval_profile_id")
        return normalized

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

    @staticmethod
    def _normalize_retrieval_mode(mode: str | None, *, index_capability: str) -> str:
        normalized = str(mode or "").strip().lower()
        legacy_map = {
            "hybrid": "rag_graph",
            "graphrag": "rag_graph",
            "auto": "rag",
            "default": "rag",
        }
        normalized = legacy_map.get(normalized, normalized)
        if normalized not in {"rag", "rag_graph"}:
            normalized = "rag"
        if index_capability != "rag_graph":
            return "rag"
        return normalized

    @staticmethod
    def _normalize_index_capability(value: str | None, retrieval_mode: str | None = None) -> str:
        normalized = str(value or "").strip().lower()
        if normalized in {"rag", "rag_graph"}:
            return normalized
        if str(retrieval_mode or "").strip().lower() in {"hybrid", "graphrag", "rag_graph"}:
            return "rag_graph"
        return "rag"

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
        retrieval_mode = normalized.get("retrieval_settings", {}).get("default_mode")
        explicit_index_capability = (knowledge_config or {}).get("index_capability")
        normalized["index_capability"] = cls._normalize_index_capability(
            explicit_index_capability,
            retrieval_mode,
        )
        normalized["retrieval_settings"]["default_mode"] = cls._normalize_retrieval_mode(
            retrieval_mode,
            index_capability=normalized["index_capability"],
        )
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
            local_runtime = get_local_runtime_settings(knowledge_id)
            if local_runtime:
                return cls._normalize_knowledge_config(local_runtime.get("knowledge_config"))
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
        local_runtime = get_local_runtime_settings(knowledge_id)
        if local_runtime:
            runtime = dict(local_runtime)
            config = cls._normalize_knowledge_config(runtime.get("knowledge_config"))
            domain_pack_id = runtime.get("domain_pack_id") or config.get("domain_pack_id")
            domain_pack = runtime.get("domain_pack")
            if domain_pack_id and not domain_pack:
                loaded_pack = DomainPackLoader().load(domain_pack_id)
                domain_pack = loaded_pack.to_dict() if loaded_pack else None
            config = cls._apply_domain_pack_defaults(config, domain_pack)
            runtime["knowledge_id"] = knowledge_id
            runtime["knowledge_config"] = config
            runtime["domain_pack_id"] = domain_pack_id
            runtime["domain_pack"] = domain_pack
            runtime.setdefault("text_embedding_config", None)
            runtime.setdefault("vl_embedding_config", None)
            runtime.setdefault("rerank_config", None)
            return runtime
        payload = await cls.get_knowledge_payload(knowledge_id)
        config = payload["knowledge_config"]
        model_refs = config.get("model_refs", {})
        domain_pack_id = config.get("domain_pack_id")
        domain_pack = DomainPackLoader().load(domain_pack_id) if domain_pack_id else None
        config = cls._apply_domain_pack_defaults(
            config,
            domain_pack.to_dict() if domain_pack else None,
        )

        return {
            "knowledge_id": knowledge_id,
            "knowledge_config": config,
            "domain_pack_id": domain_pack_id,
            "domain_pack": domain_pack.to_dict() if domain_pack else None,
            "text_embedding_config": await cls.resolve_model_config_by_id(model_refs.get("text_embedding_model_id")),
            "vl_embedding_config": await cls.resolve_model_config_by_id(model_refs.get("vl_embedding_model_id")),
            "rerank_config": await cls.resolve_model_config_by_id(model_refs.get("rerank_model_id")),
        }

    @classmethod
    async def mark_community_stale(cls, knowledge_id: str) -> dict[str, Any]:
        knowledge = await KnowledgeDao.select_user_by_id(knowledge_id)
        if not knowledge:
            raise ValueError("knowledge not found")
        payload = knowledge.to_dict()
        normalized_config = cls._normalize_knowledge_config(
            payload.get("knowledge_config"),
            payload.get("default_retrieval_mode"),
        )
        graph_index_settings = dict(normalized_config.get("graph_index_settings") or {})
        graph_index_settings["community_detection_status"] = "stale"
        graph_index_settings["community_report_status"] = "stale"
        normalized_config["graph_index_settings"] = graph_index_settings
        await KnowledgeDao.update_knowledge_by_id(
            knowledge_id,
            payload.get("description"),
            payload.get("name"),
            default_retrieval_mode=normalized_config["retrieval_settings"]["default_mode"],
            knowledge_config=normalized_config,
        )
        return normalized_config

    @staticmethod
    async def list_eval_profiles() -> list[dict[str, Any]]:
        return [
            {
                "eval_profile_id": "general_local",
                "label": "通用本地评测",
                "scope": "knowledge",
            },
            {
                "eval_profile_id": "contract_review_local",
                "label": "合同本地评测",
                "scope": "domain_pack",
            },
        ]

    @classmethod
    async def run_reindex_action(cls, knowledge_id: str, action: str) -> dict[str, Any]:
        normalized_action = str(action or "").strip().lower()
        supported_actions = {
            "text_index",
            "bm25_index",
            "graph_index",
            "community_detection",
            "community_report",
            "full_rebuild",
        }
        if normalized_action not in supported_actions:
            raise ValueError(f"Unsupported reindex action: {action}")
        return {
            "knowledge_id": knowledge_id,
            "action": normalized_action,
            "status": "accepted",
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

    @classmethod
    async def search_knowledge(cls, *, knowledge_ids: List[str], query: str, top_k: int):
        from zuno.services.rag.handler import RagHandler

        return await RagHandler.retrieve_ranked_documents_with_metadata(
            query=query,
            collection_names=knowledge_ids,
            top_k=top_k,
        )


__all__ = ["DEFAULT_KNOWLEDGE_CONFIG", "KnowledgeService"]
