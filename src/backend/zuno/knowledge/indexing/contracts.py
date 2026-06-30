from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


IndexTarget = Literal["bm25", "vector", "graph"]


class KnowledgeSpaceManifest(BaseModel):
    knowledge_space_id: str
    workspace_id: str
    graph_project_id: str | None = None
    index_version: str
    status: Literal["created", "ready", "failed"] = "created"


class IndexJobManifest(BaseModel):
    job_id: str
    knowledge_space_id: str
    workspace_id: str
    document_id: str
    source_uri: str
    index_version: str
    targets: list[IndexTarget] = Field(default_factory=list)
    target_status: dict[str, str] = Field(default_factory=dict)
    status: Literal["succeeded", "failed"]
    error: str | None = None
    retry_count: int = 0
    previous_job_id: str | None = None
    graph_project_ref: str | None = None
    source_block_ids: list[str] = Field(default_factory=list)


class IndexQueryResult(BaseModel):
    knowledge_space_id: str
    index_version: str
    query: str
    documents_by_source: dict[str, list[dict]] = Field(default_factory=dict)
    manifest: IndexJobManifest


__all__ = [
    "IndexJobManifest",
    "IndexQueryResult",
    "IndexTarget",
    "KnowledgeSpaceManifest",
]
