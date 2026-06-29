from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator

from zuno.services.graphrag.models import GraphRAGProjectContract


def _with_legacy_project_id(data: Any) -> Any:
    if isinstance(data, dict) and not data.get("graphrag_project_id") and data.get("domain_pack_id"):
        next_data = dict(data)
        next_data["graphrag_project_id"] = next_data.get("domain_pack_id")
        return next_data
    return data


class KnowledgeModelRefs(BaseModel):
    text_embedding_model_id: Optional[str] = Field(default=None, min_length=1)
    vl_embedding_model_id: Optional[str] = Field(default=None, min_length=1)
    rerank_model_id: Optional[str] = Field(default=None, min_length=1)
    entity_extraction_llm_id: Optional[str] = Field(default=None, min_length=1)
    graph_extraction_llm_id: Optional[str] = Field(default=None, min_length=1)


class KnowledgeModelRefsPatch(BaseModel):
    text_embedding_model_id: Optional[str] = Field(default=None, min_length=1)
    vl_embedding_model_id: Optional[str] = Field(default=None, min_length=1)
    rerank_model_id: Optional[str] = Field(default=None, min_length=1)
    entity_extraction_llm_id: Optional[str] = Field(default=None, min_length=1)
    graph_extraction_llm_id: Optional[str] = Field(default=None, min_length=1)


class KnowledgePromptRefs(BaseModel):
    entity_extraction_prompt_id: Optional[str] = Field(default=None, min_length=1, max_length=128)
    extract_graph: Optional[str] = Field(default=None, min_length=1, max_length=512)


class KnowledgePromptRefsPatch(BaseModel):
    entity_extraction_prompt_id: Optional[str] = Field(default=None, min_length=1, max_length=128)
    extract_graph: Optional[str] = Field(default=None, min_length=1, max_length=512)


class KnowledgeSchemaRefs(BaseModel):
    entity_extraction_schema_version: Optional[str] = Field(default=None, min_length=1, max_length=128)
    graph_schema_version: Optional[str] = Field(default=None, min_length=1, max_length=128)


class KnowledgeSchemaRefsPatch(BaseModel):
    entity_extraction_schema_version: Optional[str] = Field(default=None, min_length=1, max_length=128)
    graph_schema_version: Optional[str] = Field(default=None, min_length=1, max_length=128)


class KnowledgePolicyRefs(BaseModel):
    entity_extraction_cost_latency_profile: Optional[str] = Field(default=None, min_length=1, max_length=64)


class KnowledgePolicyRefsPatch(BaseModel):
    entity_extraction_cost_latency_profile: Optional[str] = Field(default=None, min_length=1, max_length=64)


class KnowledgeEvalRefs(BaseModel):
    entity_extraction_eval_profile: Optional[str] = Field(default=None, min_length=1, max_length=128)


class KnowledgeEvalRefsPatch(BaseModel):
    entity_extraction_eval_profile: Optional[str] = Field(default=None, min_length=1, max_length=128)


class KnowledgeIndexSettings(BaseModel):
    chunk_mode: str = Field(default="general", pattern="^(general|parent_child|qa)$")
    chunk_size: int = Field(default=1024, ge=1, le=8192)
    overlap: int = Field(default=120, ge=0, le=4096)
    separator: str = Field(default="\n\n", max_length=64)
    replace_consecutive_spaces: bool = Field(default=True)
    remove_urls_emails: bool = Field(default=False)
    image_indexing_mode: str = Field(default="dual", pattern="^(text_only|vl_only|dual)$")
    vector_backend: str = Field(default="milvus", pattern="^(milvus|chroma|milvus_lite)$")
    index_version: str = Field(default="v1", min_length=1, max_length=64)
    status: str = Field(default="active", pattern="^(active|disabled|archived)$")
    health_status: str = Field(default="ready", pattern="^(ready|degraded|stale|failed|unavailable)$")
    text_index_status: str = Field(default="ready", pattern="^(ready|queued|running|stale|failed|unavailable|not_built)$")
    bm25_index_status: str = Field(default="ready", pattern="^(ready|queued|running|stale|failed|unavailable|not_built)$")
    last_build_time: Optional[str] = Field(default=None)
    last_error: Optional[str] = Field(default=None)


class KnowledgeIndexSettingsPatch(BaseModel):
    chunk_mode: Optional[str] = Field(default=None, pattern="^(general|parent_child|qa)$")
    chunk_size: Optional[int] = Field(default=None, ge=1, le=8192)
    overlap: Optional[int] = Field(default=None, ge=0, le=4096)
    separator: Optional[str] = Field(default=None, max_length=64)
    replace_consecutive_spaces: Optional[bool] = Field(default=None)
    remove_urls_emails: Optional[bool] = Field(default=None)
    image_indexing_mode: Optional[str] = Field(default=None, pattern="^(text_only|vl_only|dual)$")
    vector_backend: Optional[str] = Field(default=None, pattern="^(milvus|chroma|milvus_lite)$")
    index_version: Optional[str] = Field(default=None, min_length=1, max_length=64)
    status: Optional[str] = Field(default=None, pattern="^(active|disabled|archived)$")
    health_status: Optional[str] = Field(default=None, pattern="^(ready|degraded|stale|failed|unavailable)$")
    text_index_status: Optional[str] = Field(default=None, pattern="^(ready|queued|running|stale|failed|unavailable|not_built)$")
    bm25_index_status: Optional[str] = Field(default=None, pattern="^(ready|queued|running|stale|failed|unavailable|not_built)$")
    last_build_time: Optional[str] = Field(default=None)
    last_error: Optional[str] = Field(default=None)


class KnowledgeGraphIndexSettings(BaseModel):
    entity_extraction_mode: str = Field(default="rule_llm", pattern="^(rule|llm|rule_llm)$")
    entity_extraction_fallback_mode: Optional[str] = Field(default="rule", pattern="^(rule|structured|fixture)$")
    entity_extraction_llm_id: Optional[str] = Field(default=None, min_length=1)
    entity_extraction_prompt_id: Optional[str] = Field(default=None, min_length=1, max_length=128)
    entity_extraction_schema_version: Optional[str] = Field(default=None, min_length=1, max_length=128)
    entity_extraction_cost_latency_profile: Optional[str] = Field(default=None, min_length=1, max_length=64)
    entity_extraction_eval_profile: Optional[str] = Field(default=None, min_length=1, max_length=128)
    relation_schema: str = Field(default="open", pattern="^(open|typed)$")
    entity_normalization: bool = Field(default=True)
    evidence_backlink: bool = Field(default=True)
    use_rag_entry_chunk: bool = Field(default=True)
    community_report_prompt_id: Optional[str] = Field(default=None, min_length=1, max_length=128)
    index_version: str = Field(default="v1", min_length=1, max_length=64)
    health_status: str = Field(default="ready", pattern="^(ready|degraded|stale|failed|unavailable)$")
    graph_index_status: str = Field(default="ready", pattern="^(ready|queued|running|stale|failed|unavailable|not_built)$")
    community_detection_status: str = Field(default="not_built", pattern="^(ready|queued|running|stale|failed|unavailable|not_built)$")
    community_report_status: str = Field(default="not_built", pattern="^(ready|queued|running|stale|failed|unavailable|not_built)$")
    community_version: str = Field(default="v0", min_length=1, max_length=64)


class KnowledgeGraphIndexSettingsPatch(BaseModel):
    entity_extraction_mode: Optional[str] = Field(default=None, pattern="^(rule|llm|rule_llm)$")
    entity_extraction_fallback_mode: Optional[str] = Field(default=None, pattern="^(rule|structured|fixture)$")
    entity_extraction_llm_id: Optional[str] = Field(default=None, min_length=1)
    entity_extraction_prompt_id: Optional[str] = Field(default=None, min_length=1, max_length=128)
    entity_extraction_schema_version: Optional[str] = Field(default=None, min_length=1, max_length=128)
    entity_extraction_cost_latency_profile: Optional[str] = Field(default=None, min_length=1, max_length=64)
    entity_extraction_eval_profile: Optional[str] = Field(default=None, min_length=1, max_length=128)
    relation_schema: Optional[str] = Field(default=None, pattern="^(open|typed)$")
    entity_normalization: Optional[bool] = Field(default=None)
    evidence_backlink: Optional[bool] = Field(default=None)
    use_rag_entry_chunk: Optional[bool] = Field(default=None)
    community_report_prompt_id: Optional[str] = Field(default=None, min_length=1, max_length=128)
    index_version: Optional[str] = Field(default=None, min_length=1, max_length=64)
    health_status: Optional[str] = Field(default=None, pattern="^(ready|degraded|stale|failed|unavailable)$")
    graph_index_status: Optional[str] = Field(default=None, pattern="^(ready|queued|running|stale|failed|unavailable|not_built)$")
    community_detection_status: Optional[str] = Field(default=None, pattern="^(ready|queued|running|stale|failed|unavailable|not_built)$")
    community_report_status: Optional[str] = Field(default=None, pattern="^(ready|queued|running|stale|failed|unavailable|not_built)$")
    community_version: Optional[str] = Field(default=None, min_length=1, max_length=64)


class KnowledgeRetrievalSettings(BaseModel):
    default_mode: str = Field(default="rag", pattern="^(auto|hybrid|rag|graphrag|rag_graph|rag_graph_deep)$")
    profile: str = Field(default="auto", min_length=1, max_length=64)
    refill_policy: str = Field(default="smart", pattern="^(none|auto|smart)$")
    top_k: int = Field(default=5, ge=1, le=50)
    rerank_enabled: bool = Field(default=True)
    rerank_top_k: int = Field(default=4, ge=1, le=50)
    score_threshold: Optional[float] = Field(default=None, ge=0, le=1)
    graph_hop_limit: int = Field(default=2, ge=1, le=3)
    max_paths_per_entity: int = Field(default=5, ge=1, le=20)


class KnowledgeRetrievalSettingsPatch(BaseModel):
    default_mode: Optional[str] = Field(default=None, pattern="^(auto|hybrid|rag|graphrag|rag_graph|rag_graph_deep)$")
    profile: Optional[str] = Field(default=None, min_length=1, max_length=64)
    refill_policy: Optional[str] = Field(default=None, pattern="^(none|auto|smart)$")
    top_k: Optional[int] = Field(default=None, ge=1, le=50)
    rerank_enabled: Optional[bool] = Field(default=None)
    rerank_top_k: Optional[int] = Field(default=None, ge=1, le=50)
    score_threshold: Optional[float] = Field(default=None, ge=0, le=1)
    graph_hop_limit: Optional[int] = Field(default=None, ge=1, le=3)
    max_paths_per_entity: Optional[int] = Field(default=None, ge=1, le=20)


class KnowledgeConfig(BaseModel):
    index_capability: str = Field(default="rag", pattern="^(rag|rag_graph)$")
    graphrag_project_id: Optional[str] = Field(default=None, min_length=1, max_length=64)
    graphrag_project: Optional[GraphRAGProjectContract] = Field(default=None)
    eval_profile_id: Optional[str] = Field(default=None, min_length=1, max_length=64)
    model_refs: KnowledgeModelRefs = Field(default_factory=KnowledgeModelRefs)
    prompt_refs: KnowledgePromptRefs = Field(default_factory=KnowledgePromptRefs)
    schema_refs: KnowledgeSchemaRefs = Field(default_factory=KnowledgeSchemaRefs)
    policy_refs: KnowledgePolicyRefs = Field(default_factory=KnowledgePolicyRefs)
    eval_refs: KnowledgeEvalRefs = Field(default_factory=KnowledgeEvalRefs)
    index_settings: KnowledgeIndexSettings = Field(default_factory=KnowledgeIndexSettings)
    graph_index_settings: KnowledgeGraphIndexSettings = Field(default_factory=KnowledgeGraphIndexSettings)
    retrieval_settings: KnowledgeRetrievalSettings = Field(default_factory=KnowledgeRetrievalSettings)

    @model_validator(mode="before")
    @classmethod
    def accept_legacy_domain_pack_id(cls, data: Any) -> Any:
        return _with_legacy_project_id(data)


class KnowledgeConfigPatch(BaseModel):
    index_capability: Optional[str] = Field(default=None, pattern="^(rag|rag_graph)$")
    graphrag_project_id: Optional[str] = Field(default=None, min_length=1, max_length=64)
    graphrag_project: Optional[GraphRAGProjectContract] = Field(default=None)
    eval_profile_id: Optional[str] = Field(default=None, min_length=1, max_length=64)
    model_refs: Optional[KnowledgeModelRefsPatch] = Field(default=None)
    prompt_refs: Optional[KnowledgePromptRefsPatch] = Field(default=None)
    schema_refs: Optional[KnowledgeSchemaRefsPatch] = Field(default=None)
    policy_refs: Optional[KnowledgePolicyRefsPatch] = Field(default=None)
    eval_refs: Optional[KnowledgeEvalRefsPatch] = Field(default=None)
    index_settings: Optional[KnowledgeIndexSettingsPatch] = Field(default=None)
    graph_index_settings: Optional[KnowledgeGraphIndexSettingsPatch] = Field(default=None)
    retrieval_settings: Optional[KnowledgeRetrievalSettingsPatch] = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def accept_legacy_domain_pack_id(cls, data: Any) -> Any:
        return _with_legacy_project_id(data)


class KnowledgeCreateRequest(BaseModel):
    knowledge_name: str = Field(description="knowledge name", min_length=2, max_length=10)
    knowledge_desc: Optional[str] = Field(
        description="knowledge description",
        min_length=10,
        max_length=200,
        default=None,
    )
    knowledge_config: Optional[KnowledgeConfig] = Field(default=None)


class KnowledgeUpdateRequest(BaseModel):
    knowledge_id: str = Field(description="knowledge id")
    knowledge_name: Optional[str] = Field(default=None, description="knowledge name", min_length=2, max_length=10)
    knowledge_desc: Optional[str] = Field(
        default=None,
        description="knowledge description",
        min_length=10,
        max_length=200,
    )
    knowledge_config: Optional[KnowledgeConfigPatch] = Field(default=None)


__all__ = [
    "KnowledgeConfig",
    "KnowledgeConfigPatch",
    "KnowledgeCreateRequest",
    "GraphRAGProjectContract",
    "KnowledgeGraphIndexSettings",
    "KnowledgeGraphIndexSettingsPatch",
    "KnowledgeIndexSettings",
    "KnowledgeIndexSettingsPatch",
    "KnowledgeModelRefs",
    "KnowledgeModelRefsPatch",
    "KnowledgePromptRefs",
    "KnowledgePromptRefsPatch",
    "KnowledgeSchemaRefs",
    "KnowledgeSchemaRefsPatch",
    "KnowledgePolicyRefs",
    "KnowledgePolicyRefsPatch",
    "KnowledgeEvalRefs",
    "KnowledgeEvalRefsPatch",
    "KnowledgeRetrievalSettings",
    "KnowledgeRetrievalSettingsPatch",
    "KnowledgeUpdateRequest",
]
