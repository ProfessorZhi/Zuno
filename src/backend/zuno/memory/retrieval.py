from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import re
from typing import Any

from zuno.platform.services.memory.layers import InMemoryLayerStore, MemoryCandidate, MemoryScope


@dataclass(frozen=True, slots=True)
class SemanticMemorySearchResult:
    candidate: MemoryCandidate
    score: float
    matched_terms: tuple[str, ...]
    adapter_id: str
    vector_ref: str
    local_fallback: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate.candidate_id,
            "scope": self.candidate.scope.to_dict(),
            "layer": self.candidate.layer.value,
            "content": self.candidate.content,
            "confidence": self.candidate.confidence,
            "source_event_ids": list(self.candidate.source_event_ids),
            "score": self.score,
            "matched_terms": list(self.matched_terms),
            "adapter_id": self.adapter_id,
            "vector_ref": self.vector_ref,
            "local_fallback": self.local_fallback,
        }


class DeterministicSemanticMemoryAdapter:
    """Local semantic fallback that uses deterministic token overlap, not an external vector DB."""

    adapter_id = "local_deterministic_semantic_v1"
    embedding_provider = "local_token_hash_v1"
    local_fallback = True

    def describe(self) -> dict[str, Any]:
        return {
            "adapter_id": self.adapter_id,
            "embedding_provider": self.embedding_provider,
            "local_fallback": self.local_fallback,
            "external_vector_store": None,
        }

    def search(
        self,
        *,
        scope: MemoryScope,
        query: str,
        candidates: tuple[MemoryCandidate, ...] | list[MemoryCandidate],
        limit: int = 5,
    ) -> tuple[SemanticMemorySearchResult, ...]:
        if limit <= 0:
            return ()
        query_terms = _tokenize(query)
        results: list[SemanticMemorySearchResult] = []
        for candidate in candidates:
            if candidate.scope != scope:
                continue
            candidate_terms = _tokenize(candidate.content)
            matched_terms = tuple(sorted(query_terms.intersection(candidate_terms)))
            if query_terms and not matched_terms:
                continue
            if query_terms:
                match_ratio = len(matched_terms) / max(len(query_terms), 1)
                density = len(matched_terms) / max(len(candidate_terms), 1)
                score = round((match_ratio * 0.65) + (density * 0.15) + (candidate.confidence * 0.2), 4)
            else:
                score = round(candidate.confidence, 4)
            results.append(
                SemanticMemorySearchResult(
                    candidate=candidate,
                    score=score,
                    matched_terms=matched_terms,
                    adapter_id=self.adapter_id,
                    vector_ref=_vector_ref(candidate),
                    local_fallback=self.local_fallback,
                )
            )
        results.sort(key=lambda result: (result.score, result.candidate.confidence, result.candidate.candidate_id), reverse=True)
        return tuple(results[:limit])


def _tokenize(text: str) -> set[str]:
    return {term for term in re.findall(r"[a-z0-9\u4e00-\u9fff]+", str(text).lower()) if term}


def _vector_ref(candidate: MemoryCandidate) -> str:
    digest = sha256(candidate.content.encode("utf-8")).hexdigest()[:12]
    return f"local-vector:{candidate.candidate_id}:{digest}"


__all__ = [
    "DeterministicSemanticMemoryAdapter",
    "InMemoryLayerStore",
    "MemoryCandidate",
    "MemoryScope",
    "SemanticMemorySearchResult",
]
