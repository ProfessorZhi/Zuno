from typing import Optional

from pydantic import BaseModel, Field


class KnowledgeModelRefs(BaseModel):
    text_embedding_model_id: Optional[str] = Field(default=None, min_length=1)
    vl_embedding_model_id: Optional[str] = Field(default=None, min_length=1)
    rerank_model_id: Optional[str] = Field(default=None, min_length=1)


class KnowledgeModelRefsPatch(BaseModel):
    text_embedding_model_id: Optional[str] = Field(default=None, min_length=1)
    vl_embedding_model_id: Optional[str] = Field(default=None, min_length=1)
    rerank_model_id: Optional[str] = Field(default=None, min_length=1)


class KnowledgeIndexSettings(BaseModel):
    chunk_mode: str = Field(default="general", pattern="^(general|parent_child|qa)$")
    chunk_size: int = Field(default=1024, ge=1, le=8192)
    overlap: int = Field(default=120, ge=0, le=4096)
    separator: str = Field(default="\n\n", max_length=64)
    replace_consecutive_spaces: bool = Field(default=True)
    remove_urls_emails: bool = Field(default=False)
    image_indexing_mode: str = Field(default="dual", pattern="^(text_only|vl_only|dual)$")


class KnowledgeIndexSettingsPatch(BaseModel):
    chunk_mode: Optional[str] = Field(default=None, pattern="^(general|parent_child|qa)$")
    chunk_size: Optional[int] = Field(default=None, ge=1, le=8192)
    overlap: Optional[int] = Field(default=None, ge=0, le=4096)
    separator: Optional[str] = Field(default=None, max_length=64)
    replace_consecutive_spaces: Optional[bool] = Field(default=None)
    remove_urls_emails: Optional[bool] = Field(default=None)
    image_indexing_mode: Optional[str] = Field(default=None, pattern="^(text_only|vl_only|dual)$")


class KnowledgeRetrievalSettings(BaseModel):
    default_mode: str = Field(default="hybrid", pattern="^(auto|hybrid|rag|graphrag)$")
    top_k: int = Field(default=5, ge=1, le=50)
    rerank_enabled: bool = Field(default=True)
    rerank_top_k: int = Field(default=4, ge=1, le=50)
    score_threshold: Optional[float] = Field(default=None, ge=0, le=1)


class KnowledgeRetrievalSettingsPatch(BaseModel):
    default_mode: Optional[str] = Field(default=None, pattern="^(auto|hybrid|rag|graphrag)$")
    top_k: Optional[int] = Field(default=None, ge=1, le=50)
    rerank_enabled: Optional[bool] = Field(default=None)
    rerank_top_k: Optional[int] = Field(default=None, ge=1, le=50)
    score_threshold: Optional[float] = Field(default=None, ge=0, le=1)


class KnowledgeConfig(BaseModel):
    model_refs: KnowledgeModelRefs = Field(default_factory=KnowledgeModelRefs)
    index_settings: KnowledgeIndexSettings = Field(default_factory=KnowledgeIndexSettings)
    retrieval_settings: KnowledgeRetrievalSettings = Field(default_factory=KnowledgeRetrievalSettings)


class KnowledgeConfigPatch(BaseModel):
    model_refs: Optional[KnowledgeModelRefsPatch] = Field(default=None)
    index_settings: Optional[KnowledgeIndexSettingsPatch] = Field(default=None)
    retrieval_settings: Optional[KnowledgeRetrievalSettingsPatch] = Field(default=None)


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
