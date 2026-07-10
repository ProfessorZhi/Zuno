from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from zuno.agent.contracts import ContextPack, ReflexionLesson
from zuno.memory.retrieval import (
    DeterministicSemanticMemoryAdapter,
    SemanticMemorySearchResult,
)
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


@dataclass(frozen=True, slots=True)
class MemoryPrivacyDeleteReport:
    scope: MemoryScope
    actor_id: str
    reason: str
    deleted_counts: dict[str, int]
    ledger_entry_id: str
    status: str = "completed"
    report_version: str = "phase09-memory-privacy-delete-v1"

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_version": self.report_version,
            "status": self.status,
            "scope": self.scope.to_dict(),
            "actor_id": self.actor_id,
            "reason": self.reason,
            "deleted_counts": dict(self.deleted_counts),
            "ledger_entry_id": self.ledger_entry_id,
        }


@dataclass(frozen=True, slots=True)
class MemoryEvalBaselineResult:
    scope: MemoryScope
    query: str
    release_gate_status: str
    metrics: dict[str, dict[str, Any]]
    adapter: dict[str, Any]
    context_pack: dict[str, Any]
    result_version: str = "phase09-memory-eval-baseline-v1"

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_version": self.result_version,
            "scope": self.scope.to_dict(),
            "query": self.query,
            "release_gate_status": self.release_gate_status,
            "metrics": {name: dict(value) for name, value in self.metrics.items()},
            "adapter": dict(self.adapter),
            "context_pack": dict(self.context_pack),
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
    "session_memory": MemoryTaxonomyEntry(
        category="session_memory",
        storage_target="summary_store",
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
    "reflexion_memory_candidate": MemoryTaxonomyEntry(
        category="reflexion_memory_candidate",
        storage_target="review_queue",
        can_enter_context=False,
        requires_review=True,
    ),
    "governance_memory": MemoryTaxonomyEntry(
        category="governance_memory",
        storage_target="governance_ledger",
        can_enter_context=False,
        requires_review=False,
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
    semantic_adapter: DeterministicSemanticMemoryAdapter = field(
        default_factory=DeterministicSemanticMemoryAdapter
    )

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
        semantic_results = self.search_semantic_memory(scope=scope, query=query, limit=limit)
        if semantic_results:
            return tuple(result.candidate for result in semantic_results)
        return tuple(self._approved_memory_candidates(scope=scope)[:limit])

    def search_semantic_memory(
        self,
        *,
        scope: MemoryScope,
        query: str,
        limit: int = 5,
    ) -> tuple[SemanticMemorySearchResult, ...]:
        return self.semantic_adapter.search(
            scope=scope,
            query=query,
            candidates=self._approved_memory_candidates(scope=scope),
            limit=limit,
        )

    def privacy_delete_scope(
        self,
        *,
        scope: MemoryScope,
        actor_id: str,
        reason: str,
    ) -> MemoryPrivacyDeleteReport:
        if not hasattr(self.store, "delete_scope_memory"):
            raise RuntimeError("memory store does not support privacy delete")
        safe_reason = "privacy_delete_request"
        deleted_counts, ledger_entry = self.store.delete_scope_memory(
            scope=scope,
            actor_id=actor_id,
            reason=safe_reason,
        )
        return MemoryPrivacyDeleteReport(
            scope=scope,
            actor_id=actor_id,
            reason=safe_reason,
            deleted_counts=dict(deleted_counts),
            ledger_entry_id=ledger_entry.entry_id,
        )

    def evaluate_memory_baseline(
        self,
        *,
        scope: MemoryScope,
        query: str,
        task_id: str,
        trace_id: str,
        expected_source_event_ids: tuple[str, ...] = (),
        budget_tokens: int = 4000,
    ) -> MemoryEvalBaselineResult:
        context_pack = self.render_context_pack(
            scope=scope,
            task_id=task_id,
            trace_id=trace_id,
            query=query,
            budget_tokens=budget_tokens,
        )
        included_source_event_ids = {
            event_id
            for source_event_ids in context_pack["trace"]["source_event_ids_by_item"].values()
            for event_id in source_event_ids
        }
        expected_ids = {str(event_id) for event_id in expected_source_event_ids}
        retrieval_status = "pass" if expected_ids.issubset(included_source_event_ids) else "fail"
        sensitive_excluded_ids = {
            source_event_id
            for item in context_pack["context_policy"]["excluded_items"]
            if "sensitive" in str(item.get("reason", ""))
            for source_event_id in item.get("source_event_ids", [])
        }
        privacy_status = (
            "pass"
            if not sensitive_excluded_ids.intersection(included_source_event_ids)
            else "fail"
        )
        estimated_tokens = sum(
            max(1, len(str(item.get("content") or "")) // 4)
            for item in context_pack["items"]
        )
        compression_status = "pass" if estimated_tokens <= budget_tokens else "fail"
        metrics = {
            "retrieval_relevance": {
                "status": retrieval_status,
                "expected_source_event_ids": sorted(expected_ids),
                "included_source_event_ids": sorted(included_source_event_ids),
            },
            "privacy_safety": {
                "status": privacy_status,
                "sensitive_excluded_source_event_ids": sorted(sensitive_excluded_ids),
            },
            "context_compression_quality": {
                "status": compression_status,
                "estimated_tokens": estimated_tokens,
                "budget_tokens": budget_tokens,
            },
        }
        release_gate_status = (
            "pass"
            if all(metric["status"] == "pass" for metric in metrics.values())
            else "fail"
        )
        self._record_governance(
            action="memory_eval_baseline_recorded",
            scope=scope,
            trace_id=trace_id,
            task_id=task_id,
            reason=release_gate_status,
            metadata={
                "query": query,
                "metrics": metrics,
                "adapter": self.semantic_adapter.describe(),
            },
        )
        return MemoryEvalBaselineResult(
            scope=scope,
            query=query,
            release_gate_status=release_gate_status,
            metrics=metrics,
            adapter=self.semantic_adapter.describe(),
            context_pack=context_pack,
        )

    def build_context_pack(
        self,
        *,
        scope: MemoryScope,
        context_pack_id: str,
        user_goal: str,
        task_state: dict[str, Any],
        selected_evidence: list[dict[str, Any]] | tuple[dict[str, Any], ...],
        allowed_capabilities: list[str] | tuple[str, ...],
        safety_policy: dict[str, Any],
        output_contract: dict[str, Any],
        budget_tokens: int,
        task_id: str,
        trace_id: str,
        high_risk: bool = False,
    ) -> dict[str, Any]:
        rendered = self.render_context_pack(
            scope=scope,
            task_id=task_id,
            trace_id=trace_id,
            query=user_goal,
            budget_tokens=budget_tokens,
        )
        evidence_items = [dict(item) for item in selected_evidence]
        compression = self._compress_context(
            scope=scope,
            user_goal=user_goal,
            rendered_context=rendered,
            selected_evidence=evidence_items,
            budget_tokens=budget_tokens,
            high_risk=high_risk,
        )
        selected_memory_refs = [
            item["item_id"]
            for item in rendered["items"]
            if str(item.get("item_id", "")).startswith("memory:")
        ]
        selected_evidence_refs = _unique_strings(
            item.get("evidence_id")
            or item.get("citation_ref")
            or item.get("artifact_id")
            or item.get("source_event_id")
            for item in evidence_items
        )
        context_pack = ContextPack(
            context_pack_id=context_pack_id,
            user_goal=user_goal,
            task_state=dict(task_state),
            selected_memory_refs=selected_memory_refs,
            selected_evidence_refs=selected_evidence_refs,
            allowed_capabilities=list(allowed_capabilities),
            safety_policy={
                **dict(safety_policy),
                "excluded_items": list(rendered["context_policy"]["excluded_items"]),
            },
            output_contract={**dict(output_contract), "compression": compression},
            budget={
                "budget_tokens": budget_tokens,
                "estimated_tokens": compression["budget_policy"]["estimated_tokens"],
                "within_budget": compression["budget_policy"]["within_budget"],
            },
        )
        return {
            "context_pack": context_pack.model_dump(mode="json"),
            "items": rendered["items"],
            "compression": compression,
            "trace": rendered["trace"],
        }

    def submit_reflexion_lesson_candidate(
        self,
        *,
        scope: MemoryScope,
        lesson: ReflexionLesson,
        retention_policy: RetentionPolicy,
    ) -> MemoryCandidate:
        source_event_ids = tuple(str(ref) for ref in lesson.evidence_refs if str(ref).strip())
        if not source_event_ids:
            raise ValueError("ReflexionLesson candidate requires evidence_refs")
        candidate = MemoryCandidate(
            candidate_id=f"reflexion:{lesson.lesson_id}",
            scope=scope,
            layer=MemoryLayer.PROCEDURAL,
            content=lesson.lesson,
            confidence=0.7,
            source_event_ids=source_event_ids,
            dedupe_key=f"reflexion:{scope.user_id}:{lesson.task_type}:{lesson.failure_type}:{lesson.lesson_id}",
            retention_policy=retention_policy,
            review_status=MemoryReviewStatus.PENDING,
            requires_review=True,
            metadata={
                "memory_category": "reflexion_memory_candidate",
                "reflexion_lesson": lesson.model_dump(mode="json"),
                "failure_type": lesson.failure_type,
                "trigger_condition": lesson.trigger_condition,
                "hidden_cot": False,
            },
        )
        self.store.save_memory_candidate(candidate)
        self._record_governance(
            action="reflexion_lesson_candidate_created",
            scope=scope,
            source_event_ids=source_event_ids,
            reason=lesson.failure_type,
            metadata={"candidate_id": candidate.candidate_id, "lesson_id": lesson.lesson_id},
        )
        return candidate

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
        sensitive_source_event_ids = {
            event.event_id
            for event in self.store.raw_events(scope)
            if self._sensitivity_tags(event.metadata).intersection(
                self.memory_eval_policy.sensitive_tags_blocked
            )
        }

        for index, event in enumerate(self.build_recent_window(scope=scope, limit=5)):
            item_id = f"recent:{index}"
            if event.event_id in sensitive_source_event_ids:
                excluded_items.append(
                    {
                        "item_id": item_id,
                        "reason": "sensitive_raw_event_blocked",
                        "source_event_ids": [event.event_id],
                    }
                )
                continue
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
            summary_source_ids = set(summary.source_event_ids)
            if summary_source_ids.intersection(sensitive_source_event_ids):
                excluded_items.append(
                    {
                        "item_id": item_id,
                        "reason": "sensitive_source_summary_blocked",
                        "source_event_ids": list(summary.source_event_ids),
                    }
                )
                continue
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

        search_results = self.search_semantic_memory(scope=scope, query=query, limit=5)
        if not search_results:
            search_results = tuple(
                SemanticMemorySearchResult(
                    candidate=candidate,
                    score=0.0,
                    matched_terms=(),
                    adapter_id=self.semantic_adapter.adapter_id,
                    vector_ref=f"local-vector:{candidate.candidate_id}:fallback",
                    local_fallback=self.semantic_adapter.local_fallback,
                )
                for candidate in self._approved_memory_candidates(scope=scope)[:5]
            )
        for index, result in enumerate(search_results):
            candidate = result.candidate
            item_id = f"memory:{candidate.candidate_id or index}"
            exclusion_reason = self._memory_exclusion_reason(candidate)
            if exclusion_reason:
                excluded_items.append(
                    {
                        "item_id": item_id,
                        "reason": exclusion_reason,
                        "source_event_ids": list(candidate.source_event_ids),
                    }
                )
                continue
            items.append(
                {
                    "item_id": item_id,
                    "source": candidate.layer.value,
                    "content": candidate.content,
                    "source_event_ids": list(candidate.source_event_ids),
                    "confidence": candidate.confidence,
                    "semantic_score": result.score,
                    "semantic_adapter_id": result.adapter_id,
                    "vector_ref": result.vector_ref,
                }
            )
            source_event_ids_by_item[item_id] = list(candidate.source_event_ids)
            selection_reasons_by_item[item_id] = (
                "approved_semantic_memory_query_match"
                if result.score > 0
                else "approved_memory_fallback_no_query_match"
            )

        excluded_item_ids = {
            str(item.get("item_id"))
            for item in excluded_items
            if item.get("item_id")
        }
        for candidate in self.store.memory_candidates(scope):
            reason = self._memory_exclusion_reason(candidate)
            if not reason:
                continue
            item_id = f"memory:{candidate.candidate_id}"
            if item_id in excluded_item_ids:
                continue
            excluded_items.append(
                {
                    "item_id": item_id,
                    "reason": reason,
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
                "selection_reasons_by_item": selection_reasons_by_item,
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

    def _approved_memory_candidates(self, *, scope: MemoryScope) -> tuple[MemoryCandidate, ...]:
        return tuple(
            candidate
            for candidate in self.store.memory_candidates(scope)
            if self._memory_exclusion_reason(candidate) is None
        )

    @staticmethod
    def _sensitivity_tags(metadata: dict[str, Any]) -> set[str]:
        return {str(tag).lower() for tag in metadata.get("sensitivity_tags", [])}

    def _compress_context(
        self,
        *,
        scope: MemoryScope,
        user_goal: str,
        rendered_context: dict[str, Any],
        selected_evidence: list[dict[str, Any]],
        budget_tokens: int,
        high_risk: bool,
    ) -> dict[str, Any]:
        raw_events = self.build_recent_window(scope=scope, limit=5)
        task_summaries = self.store.task_summaries(scope)
        structured_fields = {
            "user_goal": user_goal,
            "decisions": [],
            "constraints": [],
            "entities": [],
            "open_issues": [],
            "tool_results": [],
            "evidence_refs": [],
            "safety_notes": [],
        }
        for event in raw_events:
            payload = event.payload
            for field in [
                "decisions",
                "constraints",
                "entities",
                "open_issues",
                "tool_results",
                "safety_notes",
            ]:
                structured_fields[field].extend(_list_payload(payload.get(field)))
        evidence_refs = _unique_strings(
            item.get("evidence_id") or item.get("citation_ref") for item in selected_evidence
        )
        artifact_refs = _unique_strings(item.get("artifact_id") for item in selected_evidence)
        source_event_ids = _unique_strings(
            [
                *(item.get("source_event_id") for item in selected_evidence),
                *(
                    event_id
                    for item in rendered_context["items"]
                    for event_id in item.get("source_event_ids", [])
                ),
            ]
        )
        structured_fields["evidence_refs"].extend(evidence_refs)
        if high_risk and not (source_event_ids or evidence_refs or artifact_refs):
            raise ValueError("high-risk summary requires source event, artifact, or evidence binding")
        item_contents = [str(item.get("content") or "") for item in rendered_context["items"]]
        evidence_contents = [str(item.get("content") or "") for item in selected_evidence]
        estimated_tokens = sum(
            max(1, len(content) // 4)
            for content in [user_goal, *item_contents, *evidence_contents]
            if content
        )
        return {
            "strategy": "structured_extraction_hierarchical_evidence_bound_budget_aware",
            "structured_fields": structured_fields,
            "hierarchical_summary": {
                "turn_summary": _first_nonempty(
                    (event.payload.get("task") or event.payload.get("text")) for event in raw_events
                )
                or user_goal,
                "task_summary": _first_nonempty(summary.content for summary in task_summaries)
                or user_goal,
                "session_summary": _first_nonempty(item_contents) or user_goal,
                "workspace_or_project_summary": (
                    f"{scope.project_id or 'workspace'} context pack includes "
                    f"{len(rendered_context['items'])} memory items and {len(selected_evidence)} evidence items."
                ),
            },
            "evidence_bound_summary": {
                "summary": _first_nonempty(evidence_contents)
                or _first_nonempty(item_contents)
                or user_goal,
                "source_event_ids": source_event_ids,
                "evidence_refs": evidence_refs,
                "artifact_refs": artifact_refs,
                "high_risk": high_risk,
            },
            "budget_policy": {
                "budget_tokens": budget_tokens,
                "estimated_tokens": estimated_tokens,
                "within_budget": estimated_tokens <= budget_tokens,
                "packing_order": [
                    "safety_policy",
                    "user_goal",
                    "task_state",
                    "selected_evidence",
                    "selected_memory",
                    "tool_and_capability_state",
                    "output_contract",
                ],
            },
        }

    def _memory_exclusion_reason(self, candidate: MemoryCandidate) -> str | None:
        if candidate.review_status is not MemoryReviewStatus.APPROVED:
            return f"{candidate.review_status.value}_review"
        memory_state = str(candidate.metadata.get("memory_state") or "").lower()
        if memory_state in {"stale", "conflict", "revoked"}:
            return f"{memory_state}_memory_excluded"
        if self._sensitivity_tags(candidate.metadata).intersection(
            self.memory_eval_policy.sensitive_tags_blocked
        ):
            return "sensitive_memory_excluded"
        return None


def _list_payload(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def _first_nonempty(values: Any) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def _unique_strings(values: Any) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


__all__ = [
    "InMemoryLayerStore",
    "DatabaseMemoryStore",
    "DeterministicSemanticMemoryAdapter",
    "DurableMemoryStore",
    "MEMORY_TAXONOMY",
    "MemoryEngine",
    "MemoryEvalBaselineResult",
    "MemoryEvalPolicy",
    "MemoryPrivacyDeleteReport",
    "MemoryTaxonomyEntry",
    "RawMemoryEvent",
    "SemanticMemorySearchResult",
    "TaskMemorySummary",
]
