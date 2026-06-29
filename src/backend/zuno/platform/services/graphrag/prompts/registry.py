from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

PromptCategory = Literal[
    "extract_graph",
    "summarize",
    "community_report",
    "local_query",
    "global_query",
    "drift_query",
]

PROMPT_CATEGORIES = {
    "extract_graph",
    "summarize",
    "community_report",
    "local_query",
    "global_query",
    "drift_query",
}
QUERY_PROMPT_CATEGORIES = {"local_query", "global_query", "drift_query"}
COMMUNITY_PROMPT_CATEGORIES = {"community_report"}


@dataclass(frozen=True, slots=True)
class PromptSpec:
    category: PromptCategory
    version: str
    path: str
    text: str
    scope: Literal["indexing", "query"]

    def to_dict(self) -> dict[str, str]:
        return {
            "category": self.category,
            "version": self.version,
            "path": self.path,
            "text": self.text,
            "scope": self.scope,
        }


class GraphRAGPromptRegistry:
    def __init__(self, *, graphrag_project_id: str, prompts: dict[str, PromptSpec]):
        self.graphrag_project_id = graphrag_project_id
        self._prompts = dict(prompts)

    @classmethod
    def from_project(cls, project) -> "GraphRAGPromptRegistry":
        return cls.from_prompt_texts(
            graphrag_project_id=project.contract.graphrag_project_id,
            prompt_version=project.contract.prompt_version,
            query_prompt_version=project.contract.query_prompt_version,
            prompt_texts=project.prompt_texts,
            prompt_paths=project.prompt_paths,
        )

    @classmethod
    def from_prompt_texts(
        cls,
        *,
        graphrag_project_id: str,
        prompt_version: str,
        query_prompt_version: str,
        prompt_texts: dict[str, str],
        prompt_paths: dict[str, str] | None = None,
    ) -> "GraphRAGPromptRegistry":
        prompts: dict[str, PromptSpec] = {}
        for category, text in prompt_texts.items():
            if category not in PROMPT_CATEGORIES:
                raise ValueError(f"unknown prompt category: {category}")
            scope = "query" if category in QUERY_PROMPT_CATEGORIES else "indexing"
            version = query_prompt_version if scope == "query" else prompt_version
            prompts[category] = PromptSpec(
                category=category,  # type: ignore[arg-type]
                version=version,
                path=(prompt_paths or {}).get(category, ""),
                text=text,
                scope=scope,
            )
        return cls(graphrag_project_id=graphrag_project_id, prompts=prompts)

    def categories(self) -> list[str]:
        return sorted(self._prompts)

    def get(self, category: PromptCategory) -> PromptSpec:
        if category not in self._prompts:
            raise KeyError(category)
        return self._prompts[category]

    @staticmethod
    def impact_for_change(category: PromptCategory) -> dict[str, object]:
        if category not in PROMPT_CATEGORIES:
            raise ValueError(f"unknown prompt category: {category}")
        scope = "query" if category in QUERY_PROMPT_CATEGORIES else "indexing"
        return {
            "category": category,
            "scope": scope,
            "requires_graph_rebuild": category == "extract_graph",
            "requires_community_refresh": scope == "indexing",
        }


__all__ = [
    "GraphRAGPromptRegistry",
    "PromptCategory",
    "PromptSpec",
]
