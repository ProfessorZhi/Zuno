from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from sqlmodel import Session, select

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
from zuno.platform.database.dao.memory_runtime import MemoryRuntimeDao
from zuno.platform.database.models.memory_runtime import (
    MemoryCandidateTable,
    MemoryGovernanceLedgerTable,
    MemoryRawEventTable,
    MemoryReviewDecisionTable,
    MemoryTaskSummaryTable,
)


@dataclass(frozen=True, slots=True)
class MemoryGovernanceLedgerEntry:
    entry_id: str
    action: str
    scope: MemoryScope
    trace_id: str = ""
    task_id: str = ""
    source_event_ids: tuple[str, ...] = ()
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "action": self.action,
            "scope": self.scope.to_dict(),
            "trace_id": self.trace_id,
            "task_id": self.task_id,
            "source_event_ids": list(self.source_event_ids),
            "reason": self.reason,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class MemoryStoreSnapshot:
    raw_events: tuple[dict[str, Any], ...] = ()
    task_summaries: tuple[dict[str, Any], ...] = ()
    memory_candidates: tuple[dict[str, Any], ...] = ()
    review_decisions: tuple[dict[str, Any], ...] = ()
    governance_ledger: tuple[dict[str, Any], ...] = ()
    snapshot_version: str = "phase07-memory-runtime-v1"

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_version": self.snapshot_version,
            "raw_events": [dict(item) for item in self.raw_events],
            "task_summaries": [dict(item) for item in self.task_summaries],
            "memory_candidates": [dict(item) for item in self.memory_candidates],
            "review_decisions": [dict(item) for item in self.review_decisions],
            "governance_ledger": [dict(item) for item in self.governance_ledger],
        }


class DurableMemoryStore(InMemoryLayerStore):
    """Snapshot-able PHASE07 local runtime store.

    This is a deterministic runtime surface for tests, local replay, and later
    storage adapters. It is not a production database.
    """

    def __init__(self) -> None:
        super().__init__()
        self._review_decisions: list[MemoryReviewDecision] = []
        self._governance_ledger: list[MemoryGovernanceLedgerEntry] = []

    def save_review_decision(self, decision: MemoryReviewDecision) -> None:
        self._review_decisions.append(decision)

    def review_decisions(self, scope: MemoryScope) -> tuple[MemoryReviewDecision, ...]:
        return tuple(
            decision
            for decision in self._review_decisions
            if any(
                candidate.candidate_id == decision.candidate_id and candidate.scope == scope
                for candidate in self._memory_candidates
            )
        )

    def append_governance_entry(
        self,
        *,
        action: str,
        scope: MemoryScope,
        trace_id: str = "",
        task_id: str = "",
        source_event_ids: tuple[str, ...] = (),
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> MemoryGovernanceLedgerEntry:
        entry = MemoryGovernanceLedgerEntry(
            entry_id=f"memory_ledger:{len(self._governance_ledger) + 1}",
            action=action,
            scope=scope,
            trace_id=trace_id,
            task_id=task_id,
            source_event_ids=source_event_ids,
            reason=reason,
            metadata=dict(metadata or {}),
        )
        self._governance_ledger.append(entry)
        return entry

    def governance_ledger(self, scope: MemoryScope) -> tuple[dict[str, Any], ...]:
        return tuple(
            entry.to_dict()
            for entry in self._governance_ledger
            if entry.scope == scope
        )

    def delete_scope_memory(
        self,
        *,
        scope: MemoryScope,
        actor_id: str,
        reason: str,
    ) -> tuple[dict[str, int], MemoryGovernanceLedgerEntry]:
        candidate_ids = {
            candidate.candidate_id
            for candidate in self._memory_candidates
            if candidate.scope == scope
        }
        counts = {
            "raw_events": sum(1 for event in self._raw_events if event.scope == scope),
            "task_summaries": sum(1 for summary in self._task_summaries if summary.scope == scope),
            "memory_candidates": len(candidate_ids),
            "review_decisions": sum(
                1
                for decision in self._review_decisions
                if decision.candidate_id in candidate_ids
            ),
            "governance_ledger": sum(1 for entry in self._governance_ledger if entry.scope == scope),
        }
        self._raw_events = [event for event in self._raw_events if event.scope != scope]
        self._task_summaries = [summary for summary in self._task_summaries if summary.scope != scope]
        self._memory_candidates = [
            candidate for candidate in self._memory_candidates if candidate.scope != scope
        ]
        self._review_decisions = [
            decision
            for decision in self._review_decisions
            if decision.candidate_id not in candidate_ids
        ]
        self._governance_ledger = [
            entry for entry in self._governance_ledger if entry.scope != scope
        ]
        ledger_entry = self.append_governance_entry(
            action="privacy_delete_applied",
            scope=scope,
            reason="privacy_delete_request",
            metadata={
                "actor_id": actor_id,
                "deleted_counts": dict(counts),
                "report_version": "phase09-memory-privacy-delete-v1",
            },
        )
        return counts, ledger_entry

    def export_snapshot(self) -> MemoryStoreSnapshot:
        return MemoryStoreSnapshot(
            raw_events=tuple(event.to_dict() for event in self._raw_events),
            task_summaries=tuple(summary.to_dict() for summary in self._task_summaries),
            memory_candidates=tuple(candidate.to_dict() for candidate in self._memory_candidates),
            review_decisions=tuple(decision.to_dict() for decision in self._review_decisions),
            governance_ledger=tuple(entry.to_dict() for entry in self._governance_ledger),
        )

    @classmethod
    def from_snapshot(
        cls,
        snapshot: MemoryStoreSnapshot | dict[str, Any],
    ) -> "DurableMemoryStore":
        payload = snapshot.to_dict() if isinstance(snapshot, MemoryStoreSnapshot) else dict(snapshot)
        store = cls()
        for event_payload in payload.get("raw_events", ()):
            store.append_raw_event(_raw_event_from_dict(dict(event_payload)))
        for summary_payload in payload.get("task_summaries", ()):
            store.save_task_summary(_task_summary_from_dict(dict(summary_payload)))
        for candidate_payload in payload.get("memory_candidates", ()):
            store.save_memory_candidate(_memory_candidate_from_dict(dict(candidate_payload)))
        for decision_payload in payload.get("review_decisions", ()):
            store.save_review_decision(_review_decision_from_dict(dict(decision_payload)))
        for entry_payload in payload.get("governance_ledger", ()):
            store._governance_ledger.append(_governance_entry_from_dict(dict(entry_payload)))
        return store


class DatabaseMemoryStore(InMemoryLayerStore):
    """SQLModel-backed PHASE07 memory runtime adapter."""

    def __init__(self, *, session_factory: Callable[[], Session] | None = None) -> None:
        self._session_factory = session_factory

    def append_raw_event(self, event: RawMemoryEvent) -> None:
        with MemoryRuntimeDao.session_scope(self._session_factory) as session:
            session.merge(_raw_event_to_table(event))

    def save_task_summary(self, summary: TaskMemorySummary) -> None:
        with MemoryRuntimeDao.session_scope(self._session_factory) as session:
            session.merge(_task_summary_to_table(summary))

    def save_memory_candidate(self, candidate: MemoryCandidate) -> None:
        with MemoryRuntimeDao.session_scope(self._session_factory) as session:
            existing = session.get(MemoryCandidateTable, candidate.candidate_id)
            if existing is None:
                session.add(_memory_candidate_to_table(candidate))
                return
            updated = _memory_candidate_to_table(candidate)
            for field_name in [
                "user_id",
                "agent_id",
                "project_id",
                "thread_id",
                "layer",
                "content",
                "confidence",
                "source_event_ids",
                "dedupe_key",
                "retention_policy",
                "review_status",
                "requires_review",
                "memory_metadata",
            ]:
                setattr(existing, field_name, getattr(updated, field_name))
            session.add(existing)

    def raw_events(self, scope: MemoryScope) -> tuple[RawMemoryEvent, ...]:
        with MemoryRuntimeDao.session_scope(self._session_factory) as session:
            rows = session.exec(
                _scope_select(MemoryRawEventTable, scope).order_by(MemoryRawEventTable.created_at)
            ).all()
            return tuple(_raw_event_from_table(row) for row in rows)

    def task_summaries(self, scope: MemoryScope) -> tuple[TaskMemorySummary, ...]:
        with MemoryRuntimeDao.session_scope(self._session_factory) as session:
            rows = session.exec(
                _scope_select(MemoryTaskSummaryTable, scope).order_by(
                    MemoryTaskSummaryTable.created_at
                )
            ).all()
            return tuple(_task_summary_from_table(row) for row in rows)

    def memory_candidates(self, scope: MemoryScope) -> tuple[MemoryCandidate, ...]:
        with MemoryRuntimeDao.session_scope(self._session_factory) as session:
            rows = session.exec(
                _scope_select(MemoryCandidateTable, scope).order_by(
                    MemoryCandidateTable.created_at
                )
            ).all()
            return tuple(_memory_candidate_from_table(row) for row in rows)

    def save_review_decision(self, decision: MemoryReviewDecision) -> None:
        with MemoryRuntimeDao.session_scope(self._session_factory) as session:
            session.add(_review_decision_to_table(decision))

    def review_decisions(self, scope: MemoryScope) -> tuple[MemoryReviewDecision, ...]:
        candidate_ids = {candidate.candidate_id for candidate in self.memory_candidates(scope)}
        with MemoryRuntimeDao.session_scope(self._session_factory) as session:
            rows = session.exec(select(MemoryReviewDecisionTable)).all()
            return tuple(
                _review_decision_from_table(row)
                for row in rows
                if row.candidate_id in candidate_ids
            )

    def append_governance_entry(
        self,
        *,
        action: str,
        scope: MemoryScope,
        trace_id: str = "",
        task_id: str = "",
        source_event_ids: tuple[str, ...] = (),
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> MemoryGovernanceLedgerEntry:
        entry = MemoryGovernanceLedgerEntry(
            entry_id=f"memory_ledger:{uuid4().hex}",
            action=action,
            scope=scope,
            trace_id=trace_id,
            task_id=task_id,
            source_event_ids=source_event_ids,
            reason=reason,
            metadata=dict(metadata or {}),
        )
        with MemoryRuntimeDao.session_scope(self._session_factory) as session:
            session.merge(_governance_entry_to_table(entry))
        return entry

    def governance_ledger(self, scope: MemoryScope) -> tuple[dict[str, Any], ...]:
        with MemoryRuntimeDao.session_scope(self._session_factory) as session:
            rows = session.exec(
                _scope_select(MemoryGovernanceLedgerTable, scope).order_by(
                    MemoryGovernanceLedgerTable.created_at
                )
            ).all()
            return tuple(_governance_entry_from_table(row).to_dict() for row in rows)

    def delete_scope_memory(
        self,
        *,
        scope: MemoryScope,
        actor_id: str,
        reason: str,
    ) -> tuple[dict[str, int], MemoryGovernanceLedgerEntry]:
        with MemoryRuntimeDao.session_scope(self._session_factory) as session:
            raw_events = session.exec(_scope_select(MemoryRawEventTable, scope)).all()
            task_summaries = session.exec(_scope_select(MemoryTaskSummaryTable, scope)).all()
            memory_candidates = session.exec(_scope_select(MemoryCandidateTable, scope)).all()
            governance_entries = session.exec(_scope_select(MemoryGovernanceLedgerTable, scope)).all()
            candidate_ids = {row.candidate_id for row in memory_candidates}
            review_decisions = (
                session.exec(select(MemoryReviewDecisionTable)).all()
                if candidate_ids
                else []
            )
            scoped_review_decisions = [
                row for row in review_decisions if row.candidate_id in candidate_ids
            ]
            counts = {
                "raw_events": len(raw_events),
                "task_summaries": len(task_summaries),
                "memory_candidates": len(memory_candidates),
                "review_decisions": len(scoped_review_decisions),
                "governance_ledger": len(governance_entries),
            }
            for row in (
                *raw_events,
                *task_summaries,
                *memory_candidates,
                *scoped_review_decisions,
                *governance_entries,
            ):
                session.delete(row)
            ledger_entry = MemoryGovernanceLedgerEntry(
                entry_id=f"memory_ledger:{uuid4().hex}",
                action="privacy_delete_applied",
                scope=scope,
                reason="privacy_delete_request",
                metadata={
                    "actor_id": actor_id,
                    "deleted_counts": dict(counts),
                    "report_version": "phase09-memory-privacy-delete-v1",
                },
            )
            session.add(_governance_entry_to_table(ledger_entry))
            return counts, ledger_entry

    def export_snapshot(self) -> MemoryStoreSnapshot:
        scopes = self._scopes()
        return MemoryStoreSnapshot(
            raw_events=tuple(
                event.to_dict()
                for scope in scopes
                for event in self.raw_events(scope)
            ),
            task_summaries=tuple(
                summary.to_dict()
                for scope in scopes
                for summary in self.task_summaries(scope)
            ),
            memory_candidates=tuple(
                candidate.to_dict()
                for scope in scopes
                for candidate in self.memory_candidates(scope)
            ),
            review_decisions=tuple(
                decision.to_dict()
                for scope in scopes
                for decision in self.review_decisions(scope)
            ),
            governance_ledger=tuple(
                entry
                for scope in scopes
                for entry in self.governance_ledger(scope)
            ),
        )

    def _scopes(self) -> tuple[MemoryScope, ...]:
        seen: set[tuple[str, str | None, str | None, str | None]] = set()
        scopes: list[MemoryScope] = []
        with MemoryRuntimeDao.session_scope(self._session_factory) as session:
            rows = session.exec(select(MemoryRawEventTable)).all()
            for row in rows:
                key = (row.user_id, row.agent_id, row.project_id, row.thread_id)
                if key in seen:
                    continue
                seen.add(key)
                scopes.append(
                    MemoryScope(
                        user_id=row.user_id,
                        agent_id=row.agent_id,
                        project_id=row.project_id,
                        thread_id=row.thread_id,
                    )
                )
        return tuple(scopes)


def _scope_select(table: Any, scope: MemoryScope):
    return select(table).where(
        table.user_id == scope.user_id,
        table.agent_id == scope.agent_id,
        table.project_id == scope.project_id,
        table.thread_id == scope.thread_id,
    )


def _scope_columns(scope: MemoryScope) -> dict[str, Any]:
    return {
        "user_id": scope.user_id,
        "agent_id": scope.agent_id,
        "project_id": scope.project_id,
        "thread_id": scope.thread_id,
    }


def _raw_event_to_table(event: RawMemoryEvent) -> MemoryRawEventTable:
    return MemoryRawEventTable(
        event_id=event.event_id,
        **_scope_columns(event.scope),
        trace_id=str(event.metadata.get("trace_id") or ""),
        task_id=str(event.metadata.get("task_id") or ""),
        event_type=event.event_type,
        layer=event.layer.value,
        payload=dict(event.payload),
        memory_metadata=dict(event.metadata),
    )


def _task_summary_to_table(summary: TaskMemorySummary) -> MemoryTaskSummaryTable:
    return MemoryTaskSummaryTable(
        summary_id=summary.summary_id,
        **_scope_columns(summary.scope),
        layer=summary.layer.value,
        content=summary.content,
        source_event_ids=list(summary.source_event_ids),
        token_count=summary.token_count,
        memory_metadata=dict(summary.metadata),
    )


def _memory_candidate_to_table(candidate: MemoryCandidate) -> MemoryCandidateTable:
    return MemoryCandidateTable(
        candidate_id=candidate.candidate_id,
        **_scope_columns(candidate.scope),
        layer=candidate.layer.value,
        content=candidate.content,
        confidence=candidate.confidence,
        source_event_ids=list(candidate.source_event_ids),
        dedupe_key=candidate.dedupe_key,
        retention_policy=candidate.retention_policy.to_dict(),
        review_status=candidate.review_status.value,
        requires_review=candidate.requires_review,
        memory_metadata=dict(candidate.metadata),
    )


def _review_decision_to_table(decision: MemoryReviewDecision) -> MemoryReviewDecisionTable:
    return MemoryReviewDecisionTable(
        candidate_id=decision.candidate_id,
        status=decision.status.value,
        reviewer_id=decision.reviewer_id,
        reason=decision.reason,
        source_event_ids=list(decision.source_event_ids),
        memory_metadata=dict(decision.metadata),
    )


def _governance_entry_to_table(
    entry: MemoryGovernanceLedgerEntry,
) -> MemoryGovernanceLedgerTable:
    return MemoryGovernanceLedgerTable(
        entry_id=entry.entry_id,
        action=entry.action,
        **_scope_columns(entry.scope),
        trace_id=entry.trace_id,
        task_id=entry.task_id,
        source_event_ids=list(entry.source_event_ids),
        reason=entry.reason,
        memory_metadata=dict(entry.metadata),
    )


def _raw_event_from_table(row: MemoryRawEventTable) -> RawMemoryEvent:
    return RawMemoryEvent(
        event_id=row.event_id,
        scope=MemoryScope(
            user_id=row.user_id,
            agent_id=row.agent_id,
            project_id=row.project_id,
            thread_id=row.thread_id,
        ),
        event_type=row.event_type,
        payload=dict(row.payload or {}),
        layer=MemoryLayer(row.layer),
        metadata=dict(row.memory_metadata or {}),
    )


def _task_summary_from_table(row: MemoryTaskSummaryTable) -> TaskMemorySummary:
    return TaskMemorySummary(
        summary_id=row.summary_id,
        scope=MemoryScope(
            user_id=row.user_id,
            agent_id=row.agent_id,
            project_id=row.project_id,
            thread_id=row.thread_id,
        ),
        layer=MemoryLayer(row.layer),
        content=row.content,
        source_event_ids=tuple(str(item) for item in row.source_event_ids or ()),
        token_count=row.token_count,
        metadata=dict(row.memory_metadata or {}),
    )


def _memory_candidate_from_table(row: MemoryCandidateTable) -> MemoryCandidate:
    return MemoryCandidate(
        candidate_id=row.candidate_id,
        scope=MemoryScope(
            user_id=row.user_id,
            agent_id=row.agent_id,
            project_id=row.project_id,
            thread_id=row.thread_id,
        ),
        layer=MemoryLayer(row.layer),
        content=row.content,
        confidence=row.confidence,
        source_event_ids=tuple(str(item) for item in row.source_event_ids or ()),
        dedupe_key=row.dedupe_key,
        retention_policy=_retention_policy_from_dict(dict(row.retention_policy or {})),
        review_status=MemoryReviewStatus(row.review_status),
        requires_review=row.requires_review,
        metadata=dict(row.memory_metadata or {}),
    )


def _review_decision_from_table(row: MemoryReviewDecisionTable) -> MemoryReviewDecision:
    return MemoryReviewDecision(
        candidate_id=row.candidate_id,
        status=MemoryReviewStatus(row.status),
        reviewer_id=row.reviewer_id,
        reason=row.reason,
        source_event_ids=tuple(str(item) for item in row.source_event_ids or ()),
        metadata=dict(row.memory_metadata or {}),
    )


def _governance_entry_from_table(
    row: MemoryGovernanceLedgerTable,
) -> MemoryGovernanceLedgerEntry:
    return MemoryGovernanceLedgerEntry(
        entry_id=row.entry_id,
        action=row.action,
        scope=MemoryScope(
            user_id=row.user_id,
            agent_id=row.agent_id,
            project_id=row.project_id,
            thread_id=row.thread_id,
        ),
        trace_id=row.trace_id,
        task_id=row.task_id,
        source_event_ids=tuple(str(item) for item in row.source_event_ids or ()),
        reason=row.reason,
        metadata=dict(row.memory_metadata or {}),
    )


def _scope_from_dict(payload: dict[str, Any]) -> MemoryScope:
    return MemoryScope(
        user_id=str(payload.get("user_id") or ""),
        agent_id=payload.get("agent_id"),
        project_id=payload.get("project_id"),
        thread_id=payload.get("thread_id"),
    )


def _retention_policy_from_dict(payload: dict[str, Any]) -> RetentionPolicy:
    return RetentionPolicy(
        ttl_days=payload.get("ttl_days"),
        allow_privacy_delete=bool(payload.get("allow_privacy_delete", True)),
    )


def _raw_event_from_dict(payload: dict[str, Any]) -> RawMemoryEvent:
    return RawMemoryEvent(
        event_id=str(payload["event_id"]),
        scope=_scope_from_dict(dict(payload["scope"])),
        event_type=str(payload["event_type"]),
        payload=dict(payload.get("payload") or {}),
        layer=MemoryLayer(str(payload.get("layer") or MemoryLayer.WORKING.value)),
        metadata=dict(payload.get("metadata") or {}),
    )


def _task_summary_from_dict(payload: dict[str, Any]) -> TaskMemorySummary:
    return TaskMemorySummary(
        summary_id=str(payload["summary_id"]),
        scope=_scope_from_dict(dict(payload["scope"])),
        layer=MemoryLayer(str(payload.get("layer") or MemoryLayer.TASK.value)),
        content=str(payload.get("content") or ""),
        source_event_ids=tuple(str(item) for item in payload.get("source_event_ids") or ()),
        token_count=int(payload.get("token_count") or 0),
        metadata=dict(payload.get("metadata") or {}),
    )


def _memory_candidate_from_dict(payload: dict[str, Any]) -> MemoryCandidate:
    return MemoryCandidate(
        candidate_id=str(payload["candidate_id"]),
        scope=_scope_from_dict(dict(payload["scope"])),
        layer=MemoryLayer(str(payload["layer"])),
        content=str(payload.get("content") or ""),
        confidence=float(payload.get("confidence") or 0),
        source_event_ids=tuple(str(item) for item in payload.get("source_event_ids") or ()),
        dedupe_key=str(payload.get("dedupe_key") or ""),
        retention_policy=_retention_policy_from_dict(dict(payload.get("retention_policy") or {})),
        review_status=MemoryReviewStatus(str(payload.get("review_status") or "pending")),
        requires_review=bool(payload.get("requires_review", True)),
        metadata=dict(payload.get("metadata") or {}),
    )


def _review_decision_from_dict(payload: dict[str, Any]) -> MemoryReviewDecision:
    return MemoryReviewDecision(
        candidate_id=str(payload["candidate_id"]),
        status=MemoryReviewStatus(str(payload["status"])),
        reviewer_id=str(payload.get("reviewer_id") or ""),
        reason=str(payload.get("reason") or ""),
        source_event_ids=tuple(str(item) for item in payload.get("source_event_ids") or ()),
        metadata=dict(payload.get("metadata") or {}),
    )


def _governance_entry_from_dict(payload: dict[str, Any]) -> MemoryGovernanceLedgerEntry:
    return MemoryGovernanceLedgerEntry(
        entry_id=str(payload["entry_id"]),
        action=str(payload["action"]),
        scope=_scope_from_dict(dict(payload["scope"])),
        trace_id=str(payload.get("trace_id") or ""),
        task_id=str(payload.get("task_id") or ""),
        source_event_ids=tuple(str(item) for item in payload.get("source_event_ids") or ()),
        reason=str(payload.get("reason") or ""),
        metadata=dict(payload.get("metadata") or {}),
    )


__all__ = [
    "DatabaseMemoryStore",
    "DurableMemoryStore",
    "InMemoryLayerStore",
    "MemoryGovernanceLedgerEntry",
    "MemoryStoreSnapshot",
]
