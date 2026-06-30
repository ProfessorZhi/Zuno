from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from zuno.platform.services.memory.layers import (
    ExternalKnowledgeRecord,
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
from zuno.memory.store import DatabaseMemoryStore, DurableMemoryStore


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
    store: InMemoryLayerStore = field(default_factory=DurableMemoryStore)
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
        self._record_governance(
            action="raw_event_appended",
            scope=scope,
            trace_id=trace_id,
            task_id=task_id,
            source_event_ids=(event_id,),
            reason=event_type,
        )
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
        metadata: dict[str, Any] | None = None,
    ) -> TaskMemorySummary:
        summary = TaskMemorySummary(
            summary_id=summary_id,
            scope=scope,
            layer=MemoryLayer.TASK,
            content=content,
            source_event_ids=source_event_ids,
            token_count=token_count,
            metadata={"memory_category": "task_summary", **dict(metadata or {})},
        )
        self.store.save_task_summary(summary)
        self._record_governance(
            action="task_summary_saved",
            scope=scope,
            trace_id=str(summary.metadata.get("trace_id") or ""),
            task_id=str(summary.metadata.get("task_id") or ""),
            source_event_ids=source_event_ids,
            reason=summary_id,
        )
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
            self._record_governance(
                action="sensitive_candidate_blocked",
                scope=scope,
                trace_id=str(source_event.metadata.get("trace_id") or ""),
                task_id=str(source_event.metadata.get("task_id") or ""),
                source_event_ids=(source_event.event_id,),
                reason="sensitive_tags_blocked",
                metadata={
                    "blocked_tags": sorted(
                        sensitivity_tags.intersection(
                            self.memory_eval_policy.sensitive_tags_blocked
                        )
                    ),
                    "excluded_item": {
                        "item_id": f"event:{source_event.event_id}",
                        "reason": "sensitive_candidate_blocked",
                        "source_event_ids": [source_event.event_id],
                    },
                },
            )
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
        status: MemoryReviewStatus | str,
        reviewer_id: str,
        reason: str,
    ) -> MemoryReviewDecision:
        normalized_status = self._normalize_review_status(status)
        if normalized_status is MemoryReviewStatus.APPROVED:
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
            self._save_review_decision(decision)
            self._record_governance(
                action="memory_candidate_approved",
                scope=candidate.scope,
                trace_id=str(candidate.metadata.get("trace_id") or ""),
                task_id=str(candidate.metadata.get("task_id") or ""),
                source_event_ids=candidate.source_event_ids,
                reason=reason,
                metadata={"candidate_id": candidate.candidate_id, "dedupe_key": candidate.dedupe_key},
            )
            return decision
        if normalized_status is MemoryReviewStatus.REJECTED:
            decision = MemoryReviewDecision.reject(
                candidate=candidate,
                reviewer_id=reviewer_id,
                reason=reason,
            )
            self._save_review_decision(decision)
            self._record_governance(
                action="memory_candidate_rejected",
                scope=candidate.scope,
                trace_id=str(candidate.metadata.get("trace_id") or ""),
                task_id=str(candidate.metadata.get("task_id") or ""),
                source_event_ids=candidate.source_event_ids,
                reason=reason,
                metadata={"candidate_id": candidate.candidate_id, "dedupe_key": candidate.dedupe_key},
            )
            return decision
        return MemoryReviewDecision(
            candidate_id=candidate.candidate_id,
            status=normalized_status,
            reviewer_id=reviewer_id,
            reason=reason,
            source_event_ids=candidate.source_event_ids,
            metadata={"dedupe_key": candidate.dedupe_key, "layer": candidate.layer.value},
        )

    def promote_external_knowledge(
        self,
        knowledge: ExternalKnowledgeRecord,
        *,
        candidate_id: str,
        retention_policy: RetentionPolicy,
        reviewer_id: str,
        reason: str,
        auto_approve: bool = False,
    ) -> MemoryCandidate:
        promoted_knowledge = knowledge.mark_for_promotion(reason=reason)
        candidate = MemoryCandidate.from_external_knowledge(
            candidate_id=candidate_id,
            knowledge=promoted_knowledge,
            retention_policy=retention_policy,
            confidence=0.68,
        )
        self.store.save_memory_candidate(candidate)
        self._record_governance(
            action="external_knowledge_promoted",
            scope=knowledge.scope,
            source_event_ids=(knowledge.record_id,),
            reason=reason,
            metadata={
                "candidate_id": candidate_id,
                "reviewer_id": reviewer_id,
                "source_uri": knowledge.source_uri,
                "citation_ids": list(knowledge.citation_ids),
            },
        )
        if not auto_approve:
            return candidate
        decision = self.review_memory_candidate(
            candidate,
            status=MemoryReviewStatus.APPROVED,
            reviewer_id=reviewer_id,
            reason=reason,
        )
        _ = decision
        return replace(
            candidate,
            review_status=MemoryReviewStatus.APPROVED,
            requires_review=False,
        )

    def apply_decay(
        self,
        *,
        scope: MemoryScope,
        current_age_days_by_candidate: dict[str, int],
    ) -> tuple[MemoryCandidate, ...]:
        decayed: list[MemoryCandidate] = []
        for candidate in self.store.memory_candidates(scope):
            if candidate.review_status is not MemoryReviewStatus.APPROVED:
                continue
            age_days = int(current_age_days_by_candidate.get(candidate.candidate_id, 0))
            ttl_days = candidate.retention_policy.ttl_days
            if ttl_days is None or age_days <= ttl_days:
                continue
            updated = replace(
                candidate,
                confidence=max(round(candidate.confidence * 0.5, 4), 0.1),
                metadata={
                    **candidate.metadata,
                    "memory_state": "decayed",
                    "age_days": age_days,
                    "ttl_days": ttl_days,
                },
            )
            self.store.save_memory_candidate(updated)
            self._record_governance(
                action="memory_candidate_decayed",
                scope=scope,
                trace_id=str(candidate.metadata.get("trace_id") or ""),
                task_id=str(candidate.metadata.get("task_id") or ""),
                source_event_ids=candidate.source_event_ids,
                reason=f"age_days {age_days} exceeded ttl_days {ttl_days}",
                metadata={"candidate_id": candidate.candidate_id},
            )
            decayed.append(updated)
        return tuple(decayed)

    def consolidate_memories(
        self,
        *,
        scope: MemoryScope,
        candidate_ids: tuple[str, ...],
        consolidated_id: str,
        content: str,
        reviewer_id: str,
        reason: str,
        retention_policy: RetentionPolicy,
    ) -> MemoryCandidate:
        source_candidates = [
            candidate
            for candidate in self.store.memory_candidates(scope)
            if candidate.candidate_id in candidate_ids
            and candidate.review_status is MemoryReviewStatus.APPROVED
        ]
        source_event_ids: list[str] = []
        for candidate in source_candidates:
            for source_event_id in candidate.source_event_ids:
                if source_event_id not in source_event_ids:
                    source_event_ids.append(source_event_id)
        if not source_event_ids:
            raise ValueError("consolidation requires approved source memories")
        consolidated = MemoryCandidate(
            candidate_id=consolidated_id,
            scope=scope,
            layer=MemoryLayer.SEMANTIC,
            content=content,
            confidence=0.86,
            source_event_ids=tuple(source_event_ids),
            dedupe_key=f"consolidated:{scope.user_id}:{consolidated_id}",
            retention_policy=retention_policy,
            review_status=MemoryReviewStatus.APPROVED,
            requires_review=False,
            metadata={
                "memory_category": "semantic_memory",
                "consolidated_from": list(candidate_ids),
                "reviewer_id": reviewer_id,
                "consolidation_reason": reason,
            },
        )
        self.store.save_memory_candidate(consolidated)
        self._record_governance(
            action="memory_candidates_consolidated",
            scope=scope,
            source_event_ids=tuple(source_event_ids),
            reason=reason,
            metadata={
                "candidate_id": consolidated_id,
                "consolidated_from": list(candidate_ids),
                "reviewer_id": reviewer_id,
            },
        )
        return consolidated

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
        selection_reasons_by_item: dict[str, str] = {}
        excluded_items: list[dict[str, Any]] = []

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
            selection_reasons_by_item[item_id] = "recent_window_within_limit"

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
            selection_reasons_by_item[item_id] = "task_summary_available"

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
            selection_reasons_by_item[item_id] = "approved_memory_query_match"

        for candidate in self.store.memory_candidates(scope):
            if candidate.review_status is MemoryReviewStatus.APPROVED:
                continue
            excluded_items.append(
                {
                    "item_id": f"memory:{candidate.candidate_id}",
                    "reason": f"{candidate.review_status.value}_review",
                    "source_event_ids": list(candidate.source_event_ids),
                }
            )

        if hasattr(self.store, "governance_ledger"):
            for entry in self.store.governance_ledger(scope):
                excluded_item = entry.get("metadata", {}).get("excluded_item")
                if excluded_item:
                    excluded_items.append(dict(excluded_item))

        return {
            "category": "model_context_pack",
            "items": items,
            "context_policy": {
                "budget_tokens": budget_tokens,
                "taxonomy_version": "phase06-memory-v1",
                "selection_reasons_by_item": selection_reasons_by_item,
                "excluded_items": excluded_items,
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

    @staticmethod
    def _normalize_review_status(status: MemoryReviewStatus | str) -> MemoryReviewStatus:
        if isinstance(status, MemoryReviewStatus):
            return status
        return MemoryReviewStatus(str(status))

    def _save_review_decision(self, decision: MemoryReviewDecision) -> None:
        if hasattr(self.store, "save_review_decision"):
            self.store.save_review_decision(decision)

    def _record_governance(
        self,
        *,
        action: str,
        scope: MemoryScope,
        trace_id: str = "",
        task_id: str = "",
        source_event_ids: tuple[str, ...] = (),
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if hasattr(self.store, "append_governance_entry"):
            self.store.append_governance_entry(
                action=action,
                scope=scope,
                trace_id=trace_id,
                task_id=task_id,
                source_event_ids=source_event_ids,
                reason=reason,
                metadata=metadata,
            )


__all__ = [
    "InMemoryLayerStore",
    "DatabaseMemoryStore",
    "DurableMemoryStore",
    "MEMORY_TAXONOMY",
    "MemoryEngine",
    "MemoryEvalPolicy",
    "MemoryTaxonomyEntry",
    "RawMemoryEvent",
    "TaskMemorySummary",
]
