from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class MemoryLayer(StrEnum):
    WORKING = "working_context"
    SHORT_TERM_STATE = "short_term_state"
    SHORT_TERM = "short_term"
    TASK = "task_memory"
    LONG_TERM = "long_term"
    SEMANTIC = "semantic_memory"
    EPISODIC = "episodic_memory"
    PROCEDURAL = "procedural_memory"
    EXTERNAL_KNOWLEDGE = "external_knowledge"


class MemoryReviewStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class MemoryProcessingPolicy:
    summary_strategy: str = "summary_compression"
    extraction_strategy: str = "structured_extraction"
    review_required: bool = True
    preserve_raw_event_ids: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary_strategy": self.summary_strategy,
            "extraction_strategy": self.extraction_strategy,
            "review_required": self.review_required,
            "preserve_raw_event_ids": self.preserve_raw_event_ids,
        }


@dataclass(frozen=True, slots=True)
class MemoryScope:
    user_id: str
    agent_id: str | None = None
    project_id: str | None = None
    thread_id: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "project_id": self.project_id,
            "thread_id": self.thread_id,
        }


@dataclass(frozen=True, slots=True)
class RetentionPolicy:
    ttl_days: int | None = None
    allow_privacy_delete: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "ttl_days": self.ttl_days,
            "allow_privacy_delete": self.allow_privacy_delete,
        }


@dataclass(frozen=True, slots=True)
class RawMemoryEvent:
    event_id: str
    scope: MemoryScope
    event_type: str
    payload: dict[str, Any]
    layer: MemoryLayer = MemoryLayer.WORKING
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "scope": self.scope.to_dict(),
            "event_type": self.event_type,
            "payload": dict(self.payload),
            "layer": self.layer.value,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class TaskMemorySummary:
    summary_id: str
    scope: MemoryScope
    layer: MemoryLayer
    content: str
    source_event_ids: tuple[str, ...]
    token_count: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.layer is not MemoryLayer.TASK:
            raise ValueError("TaskMemorySummary must use MemoryLayer.TASK")
        if not self.source_event_ids:
            raise ValueError("TaskMemorySummary requires source_event_ids")

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary_id": self.summary_id,
            "scope": self.scope.to_dict(),
            "layer": self.layer.value,
            "content": self.content,
            "source_event_ids": list(self.source_event_ids),
            "token_count": self.token_count,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class ExternalKnowledgeRecord:
    record_id: str
    scope: MemoryScope
    content: str
    source_uri: str
    citation_ids: tuple[str, ...] = ()
    can_promote_to_memory: bool = False
    promotion_reason: str | None = None
    layer: MemoryLayer = MemoryLayer.EXTERNAL_KNOWLEDGE
    metadata: dict[str, Any] = field(default_factory=dict)

    def mark_for_promotion(self, *, reason: str) -> ExternalKnowledgeRecord:
        return ExternalKnowledgeRecord(
            record_id=self.record_id,
            scope=self.scope,
            content=self.content,
            source_uri=self.source_uri,
            citation_ids=self.citation_ids,
            can_promote_to_memory=True,
            promotion_reason=reason,
            metadata=dict(self.metadata),
        )


@dataclass(frozen=True, slots=True)
class MemoryCandidate:
    candidate_id: str
    scope: MemoryScope
    layer: MemoryLayer
    content: str
    confidence: float
    source_event_ids: tuple[str, ...]
    dedupe_key: str
    retention_policy: RetentionPolicy
    review_status: MemoryReviewStatus = MemoryReviewStatus.PENDING
    requires_review: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.layer not in {
            MemoryLayer.LONG_TERM,
            MemoryLayer.SEMANTIC,
            MemoryLayer.EPISODIC,
            MemoryLayer.PROCEDURAL,
        }:
            raise ValueError("MemoryCandidate must use a long-term memory layer")
        if not 0 <= self.confidence <= 1:
            raise ValueError("MemoryCandidate confidence must be between 0 and 1")
        if not self.source_event_ids:
            raise ValueError("MemoryCandidate requires source_event_ids")
        if not self.dedupe_key:
            raise ValueError("MemoryCandidate requires dedupe_key")

    @classmethod
    def from_external_knowledge(
        cls,
        *,
        candidate_id: str,
        knowledge: ExternalKnowledgeRecord,
        retention_policy: RetentionPolicy,
        confidence: float = 0.5,
    ) -> MemoryCandidate:
        if not knowledge.can_promote_to_memory:
            raise ValueError("external knowledge requires explicit promotion before memory candidate creation")
        return cls(
            candidate_id=candidate_id,
            scope=knowledge.scope,
            layer=MemoryLayer.LONG_TERM,
            content=knowledge.content,
            confidence=confidence,
            source_event_ids=(knowledge.record_id,),
            dedupe_key=f"external:{knowledge.source_uri}",
            retention_policy=retention_policy,
            metadata={
                "source_uri": knowledge.source_uri,
                "citation_ids": list(knowledge.citation_ids),
                "promotion_reason": knowledge.promotion_reason,
            },
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "scope": self.scope.to_dict(),
            "layer": self.layer.value,
            "content": self.content,
            "confidence": self.confidence,
            "source_event_ids": list(self.source_event_ids),
            "dedupe_key": self.dedupe_key,
            "retention_policy": self.retention_policy.to_dict(),
            "review_status": self.review_status.value,
            "requires_review": self.requires_review,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class MemoryReviewDecision:
    candidate_id: str
    status: MemoryReviewStatus
    reviewer_id: str
    reason: str
    source_event_ids: tuple[str, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def approve(
        cls,
        *,
        candidate: MemoryCandidate,
        reviewer_id: str,
        reason: str,
    ) -> MemoryReviewDecision:
        return cls(
            candidate_id=candidate.candidate_id,
            status=MemoryReviewStatus.APPROVED,
            reviewer_id=reviewer_id,
            reason=reason,
            source_event_ids=candidate.source_event_ids,
            metadata={"dedupe_key": candidate.dedupe_key, "layer": candidate.layer.value},
        )

    @classmethod
    def reject(
        cls,
        *,
        candidate: MemoryCandidate,
        reviewer_id: str,
        reason: str,
    ) -> MemoryReviewDecision:
        return cls(
            candidate_id=candidate.candidate_id,
            status=MemoryReviewStatus.REJECTED,
            reviewer_id=reviewer_id,
            reason=reason,
            source_event_ids=candidate.source_event_ids,
            metadata={"dedupe_key": candidate.dedupe_key, "layer": candidate.layer.value},
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "status": self.status.value,
            "reviewer_id": self.reviewer_id,
            "reason": self.reason,
            "source_event_ids": list(self.source_event_ids),
            "metadata": dict(self.metadata),
        }


class InMemoryLayerStore:
    def __init__(self) -> None:
        self._raw_events: list[RawMemoryEvent] = []
        self._task_summaries: list[TaskMemorySummary] = []
        self._memory_candidates: list[MemoryCandidate] = []

    def append_raw_event(self, event: RawMemoryEvent) -> None:
        self._raw_events.append(event)

    def save_task_summary(self, summary: TaskMemorySummary) -> None:
        self._task_summaries.append(summary)

    def save_memory_candidate(self, candidate: MemoryCandidate) -> None:
        self._memory_candidates.append(candidate)

    def raw_events(self, scope: MemoryScope) -> tuple[RawMemoryEvent, ...]:
        return tuple(event for event in self._raw_events if event.scope == scope)

    def task_summaries(self, scope: MemoryScope) -> tuple[TaskMemorySummary, ...]:
        return tuple(summary for summary in self._task_summaries if summary.scope == scope)

    def memory_candidates(self, scope: MemoryScope) -> tuple[MemoryCandidate, ...]:
        return tuple(candidate for candidate in self._memory_candidates if candidate.scope == scope)


__all__ = [
    "ExternalKnowledgeRecord",
    "InMemoryLayerStore",
    "MemoryCandidate",
    "MemoryLayer",
    "MemoryProcessingPolicy",
    "MemoryReviewDecision",
    "MemoryReviewStatus",
    "MemoryScope",
    "RawMemoryEvent",
    "RetentionPolicy",
    "TaskMemorySummary",
]
