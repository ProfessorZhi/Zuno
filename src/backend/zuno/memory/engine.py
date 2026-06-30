from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from zuno.platform.services.memory.layers import (
    InMemoryLayerStore,
    MemoryCandidate,
    MemoryLayer,
    MemoryReviewDecision,
    MemoryReviewStatus,
    MemoryScope,
    RawMemoryEvent,
    RetentionPolicy,
    TaskMemorySummary,
)


@dataclass(frozen=True, slots=True)
class MemoryTaxonomyEntry:
    category: str
    storage_target: str
    can_enter_context: bool
    requires_review: bool
    source_binding: str = "trace_id/task_id/source_event_ids"

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "storage_target": self.storage_target,
            "can_enter_context": self.can_enter_context,
            "requires_review": self.requires_review,
            "source_binding": self.source_binding,
        }


@dataclass(frozen=True, slots=True)
class MemoryEvalPolicy:
    metrics: tuple[str, ...] = (
        "relevance",
        "over_retention",
        "redaction",
        "stale_suppression",
        "conflict_detection",
    )
    sensitive_tags_blocked: tuple[str, ...] = ("credential", "pii", "secret")

    def to_dict(self) -> dict[str, Any]:
        return {
            "metrics": list(self.metrics),
            "sensitive_tags_blocked": list(self.sensitive_tags_blocked),
        }


MEMORY_TAXONOMY = {
    "raw_event_log": MemoryTaxonomyEntry(
        category="raw_event_log",
        storage_target="event_log",
        can_enter_context=False,
        requires_review=False,
    ),
    "working_memory": MemoryTaxonomyEntry(
        category="working_memory",
        storage_target="context_only",
        can_enter_context=True,
        requires_review=False,
    ),
    "recent_window": MemoryTaxonomyEntry(
        category="recent_window",
        storage_target="context_only",
        can_enter_context=True,
        requires_review=False,
    ),
    "task_summary": MemoryTaxonomyEntry(
        category="task_summary",
        storage_target="summary_store",
        can_enter_context=True,
        requires_review=False,
    ),
    "episodic_memory": MemoryTaxonomyEntry(
        category="episodic_memory",
        storage_target="searchable_store",
        can_enter_context=True,
        requires_review=True,
    ),
    "semantic_memory": MemoryTaxonomyEntry(
        category="semantic_memory",
        storage_target="searchable_store",
        can_enter_context=True,
        requires_review=True,
    ),
    "procedural_memory": MemoryTaxonomyEntry(
        category="procedural_memory",
        storage_target="searchable_store",
        can_enter_context=True,
        requires_review=True,
    ),
    "graph_memory_candidate": MemoryTaxonomyEntry(
        category="graph_memory_candidate",
        storage_target="review_queue",
        can_enter_context=False,
        requires_review=True,
    ),
    "model_context_pack": MemoryTaxonomyEntry(
        category="model_context_pack",
        storage_target="rendered_context",
        can_enter_context=True,
        requires_review=False,
    ),
}


@dataclass(slots=True)
class MemoryEngine:
    store: InMemoryLayerStore = field(default_factory=InMemoryLayerStore)
    memory_eval_policy: MemoryEvalPolicy = field(default_factory=MemoryEvalPolicy)

    def append_event(
        self,
        *,
        scope: MemoryScope,
        event_id: str,
        event_type: str,
        payload: dict[str, Any],
        trace_id: str,
        task_id: str,
        sensitivity_tags: tuple[str, ...] | list[str] = (),
    ) -> RawMemoryEvent:
        event = RawMemoryEvent(
            event_id=event_id,
            scope=scope,
            event_type=event_type,
            payload=dict(payload),
            layer=MemoryLayer.WORKING,
            metadata={
                "trace_id": trace_id,
                "task_id": task_id,
                "sensitivity_tags": list(sensitivity_tags),
                "memory_category": "raw_event_log",
            },
        )
        self.store.append_raw_event(event)
        return event

    def build_recent_window(self, *, scope: MemoryScope, limit: int = 10) -> tuple[RawMemoryEvent, ...]:
        if limit <= 0:
            return ()
        return self.store.raw_events(scope)[-limit:]

    def summarize_task(
        self,
        *,
        scope: MemoryScope,
        summary_id: str,
        content: str,
        source_event_ids: tuple[str, ...],
        token_count: int,
    ) -> TaskMemorySummary:
        summary = TaskMemorySummary(
            summary_id=summary_id,
            scope=scope,
            layer=MemoryLayer.TASK,
            content=content,
            source_event_ids=source_event_ids,
            token_count=token_count,
            metadata={"memory_category": "task_summary"},
        )
        self.store.save_task_summary(summary)
        return summary

    def extract_memory_candidates(
        self,
        *,
        scope: MemoryScope,
        source_event: RawMemoryEvent,
        retention_policy: RetentionPolicy,
    ) -> tuple[MemoryCandidate, ...]:
        sensitivity_tags = {
            str(tag).lower()
            for tag in source_event.metadata.get("sensitivity_tags", [])
        }
        if sensitivity_tags.intersection(self.memory_eval_policy.sensitive_tags_blocked):
            return ()

        facts = tuple(str(item).strip() for item in source_event.payload.get("durable_facts", ()) if str(item).strip())
        candidates: list[MemoryCandidate] = []
        for index, fact in enumerate(facts):
            candidates.append(
                MemoryCandidate(
                    candidate_id=f"semantic_{index}",
                    scope=scope,
                    layer=MemoryLayer.SEMANTIC,
                    content=fact,
                    confidence=0.72,
                    source_event_ids=(source_event.event_id,),
                    dedupe_key=f"semantic:{scope.user_id}:{fact.lower()}",
                    retention_policy=retention_policy,
                    metadata={
                        "trace_id": source_event.metadata.get("trace_id", ""),
                        "task_id": source_event.metadata.get("task_id", ""),
                        "memory_category": "semantic_memory",
                    },
                )
            )
        return tuple(candidates)

    def review_memory_candidate(
        self,
        candidate: MemoryCandidate,
        *,
        status: MemoryReviewStatus,
        reviewer_id: str,
        reason: str,
    ) -> MemoryReviewDecision:
        if status is MemoryReviewStatus.APPROVED:
            decision = MemoryReviewDecision.approve(
                candidate=candidate,
                reviewer_id=reviewer_id,
                reason=reason,
            )
            self.store.save_memory_candidate(
                replace(
                    candidate,
                    review_status=MemoryReviewStatus.APPROVED,
                    requires_review=False,
                )
            )
            return decision
        if status is MemoryReviewStatus.REJECTED:
            return MemoryReviewDecision.reject(
                candidate=candidate,
                reviewer_id=reviewer_id,
                reason=reason,
            )
        return MemoryReviewDecision(
            candidate_id=candidate.candidate_id,
            status=status,
            reviewer_id=reviewer_id,
            reason=reason,
            source_event_ids=candidate.source_event_ids,
            metadata={"dedupe_key": candidate.dedupe_key, "layer": candidate.layer.value},
        )

    def retrieve_memory(
        self,
        *,
        scope: MemoryScope,
        query: str,
        limit: int = 5,
    ) -> tuple[MemoryCandidate, ...]:
        if limit <= 0:
            return ()
        normalized_query = str(query or "").lower()
        results = []
        for candidate in self.store.memory_candidates(scope):
            if candidate.review_status is not MemoryReviewStatus.APPROVED:
                continue
            if normalized_query and normalized_query not in candidate.content.lower():
                query_terms = {term for term in normalized_query.split() if term}
                if not query_terms.intersection(candidate.content.lower().split()):
                    continue
            results.append(candidate)
            if len(results) >= limit:
                break
        return tuple(results)

    def render_context_pack(
        self,
        *,
        scope: MemoryScope,
        task_id: str,
        trace_id: str,
        query: str,
        budget_tokens: int,
    ) -> dict[str, Any]:
        items: list[dict[str, Any]] = []
        source_event_ids_by_item: dict[str, list[str]] = {}

        for index, event in enumerate(self.build_recent_window(scope=scope, limit=5)):
            item_id = f"recent:{index}"
            items.append(
                {
                    "item_id": item_id,
                    "source": "recent_window",
                    "content": event.payload.get("task") or event.payload.get("text") or str(event.payload),
                    "source_event_ids": [event.event_id],
                }
            )
            source_event_ids_by_item[item_id] = [event.event_id]

        for index, summary in enumerate(self.store.task_summaries(scope)):
            item_id = f"summary:{index}"
            items.append(
                {
                    "item_id": item_id,
                    "source": "task_summary",
                    "content": summary.content,
                    "source_event_ids": list(summary.source_event_ids),
                }
            )
            source_event_ids_by_item[item_id] = list(summary.source_event_ids)

        for index, candidate in enumerate(self.retrieve_memory(scope=scope, query=query, limit=5)):
            item_id = f"memory:{candidate.candidate_id or index}"
            items.append(
                {
                    "item_id": item_id,
                    "source": candidate.layer.value,
                    "content": candidate.content,
                    "source_event_ids": list(candidate.source_event_ids),
                    "confidence": candidate.confidence,
                }
            )
            source_event_ids_by_item[item_id] = list(candidate.source_event_ids)

        return {
            "category": "model_context_pack",
            "items": items,
            "context_policy": {
                "budget_tokens": budget_tokens,
                "taxonomy_version": "phase06-memory-v1",
            },
            "trace": {
                "trace_id": trace_id,
                "task_id": task_id,
                "source_event_ids_by_item": source_event_ids_by_item,
                "memory_read_span": {
                    "trace_id": trace_id,
                    "task_id": task_id,
                    "query": query,
                    "item_count": len(items),
                },
            },
        }


__all__ = [
    "InMemoryLayerStore",
    "MEMORY_TAXONOMY",
    "MemoryEngine",
    "MemoryEvalPolicy",
    "MemoryTaxonomyEntry",
    "RawMemoryEvent",
    "TaskMemorySummary",
]
