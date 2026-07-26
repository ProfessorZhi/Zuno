from __future__ import annotations

from dataclasses import replace
from typing import Any, Protocol

from zuno.platform.contracts import canonical_sha256

from .contracts import EvidenceLedgerRecord
from .runtime import CorrectiveRetrievalRequest, CorrectiveRetrievalResult


class KnowledgeRepositoryProtocol(Protocol):
    def active_snapshot_id(self, *, tenant_id: str, knowledge_space_id: str) -> str | None: ...

    def start_query_run(
        self,
        *,
        query_run_id: str,
        tenant_id: str,
        workspace_id: str,
        agent_core_decision_ref: str,
        snapshot_id: str,
        request_payload: dict[str, Any],
    ) -> None: ...

    def start_retrieval_round(
        self,
        *,
        round_id: str,
        query_run_id: str,
        round_no: int,
        retriever_set: dict[str, Any],
        status: str = "RUNNING",
    ) -> None: ...

    def commit_evidence(
        self,
        *,
        evidence_id: str,
        query_run_id: str,
        round_id: str,
        chunk_id: str,
        source_span_ref: str,
        evidence_payload: dict[str, Any],
        authority_ref: str,
    ) -> None: ...

    def commit_citation_lineage(
        self,
        *,
        citation_lineage_id: str,
        evidence_id: str,
        document_version_id: str,
        source_span_ref: str,
        span_text: str,
        authorization_ref: str,
    ) -> None: ...

    def mark_query_run_status(self, *, query_run_id: str, status: str) -> None: ...


class KnowledgeUnitOfWorkProtocol(Protocol):
    def __enter__(self) -> KnowledgeRepositoryProtocol: ...
    def __exit__(self, exc_type: object, exc: object, tb: object) -> None: ...


class KnowledgeRuntimeProtocol(Protocol):
    def retrieve(self, request: CorrectiveRetrievalRequest) -> CorrectiveRetrievalResult: ...


class DurableKnowledgeRetrievalPort:
    def __init__(
        self,
        *,
        runtime: KnowledgeRuntimeProtocol,
        unit_of_work_factory: Any,
    ) -> None:
        self._runtime = runtime
        self._unit_of_work_factory = unit_of_work_factory

    def retrieve(self, request: CorrectiveRetrievalRequest) -> CorrectiveRetrievalResult:
        result = self._runtime.retrieve(request)
        persistence_trace = self._persist(request, result)
        trace = dict(result.trace)
        trace["durable_knowledge_port"] = persistence_trace
        return replace(result, trace=trace)

    def _persist(self, request: CorrectiveRetrievalRequest, result: CorrectiveRetrievalResult) -> dict[str, Any]:
        if not request.knowledge_space_ids:
            return {"status": "skipped", "reason": "knowledge_scope_empty"}
        with self._unit_of_work_factory() as repo:
            snapshot_id = request.snapshot_id or repo.active_snapshot_id(
                tenant_id=request.tenant_id,
                knowledge_space_id=request.knowledge_space_ids[0],
            )
            if not snapshot_id:
                return {"status": "skipped", "reason": "active_snapshot_unavailable"}

            query_run_id = _stable_ref("knowledge-query-run", request.trace_id, request.task_id, snapshot_id)
            repo.start_query_run(
                query_run_id=query_run_id,
                tenant_id=request.tenant_id,
                workspace_id=request.workspace_id,
                agent_core_decision_ref=request.agent_core_decision_ref,
                snapshot_id=snapshot_id,
                request_payload={
                    "query": request.query,
                    "claims": request.claims,
                    "retrieval_profile": str(request.retrieval_profile),
                    "knowledge_space_ids": request.knowledge_space_ids,
                },
            )
            committed = 0
            skipped: list[dict[str, str]] = []
            for round_payload in result.rounds:
                round_no = int(round_payload["round"])
                round_id = _stable_ref("knowledge-round", query_run_id, str(round_no))
                repo.start_retrieval_round(
                    round_id=round_id,
                    query_run_id=query_run_id,
                    round_no=round_no,
                    retriever_set={
                        "query_strategy": round_payload.get("query_strategy"),
                        "corrective_action": round_payload.get("corrective_action"),
                    },
                    status="COMPLETED",
                )
                for record in result.ledger.by_round(round_no):
                    if not _is_strict_persistable(record):
                        skipped.append({"evidence_id": record.evidence_id, "reason": _skip_reason(record)})
                        continue
                    repo.commit_evidence(
                        evidence_id=record.evidence_id,
                        query_run_id=query_run_id,
                        round_id=round_id,
                        chunk_id=record.chunk_id,
                        source_span_ref=_source_span_ref(record),
                        evidence_payload=record.model_dump(mode="json"),
                        authority_ref=record.freshness_version or "authority:unavailable",
                    )
                    repo.commit_citation_lineage(
                        citation_lineage_id=_stable_ref("citation-lineage", record.evidence_id),
                        evidence_id=record.evidence_id,
                        document_version_id=record.document_version,
                        source_span_ref=_source_span_ref(record),
                        span_text=record.text,
                        authorization_ref=request.authorization_ref,
                    )
                    committed += 1
            repo.mark_query_run_status(
                query_run_id=query_run_id,
                status="SUFFICIENT_EVIDENCE" if committed else "PARTIAL_EVIDENCE",
            )
            return {
                "status": "committed",
                "query_run_id": query_run_id,
                "snapshot_id": snapshot_id,
                "evidence_committed": committed,
                "evidence_skipped": skipped,
            }


def _is_strict_persistable(record: EvidenceLedgerRecord) -> bool:
    return bool(record.chunk_id and record.document_version and record.source_span and record.strict_citation_allowed)


def _skip_reason(record: EvidenceLedgerRecord) -> str:
    if not record.strict_citation_allowed:
        return "strict_citation_not_allowed"
    if not record.chunk_id:
        return "chunk_id_missing"
    if not record.document_version:
        return "document_version_missing"
    if not record.source_span:
        return "source_span_missing"
    return "unknown"


def _source_span_ref(record: EvidenceLedgerRecord) -> str:
    explicit = record.source_span.get("source_span_ref")
    if explicit:
        return str(explicit)
    return _stable_ref("source-span", record.document_id, record.document_version, canonical_sha256(record.source_span))


def _stable_ref(prefix: str, *parts: str) -> str:
    return f"{prefix}:{canonical_sha256({'parts': parts})[:24]}"


__all__ = ["DurableKnowledgeRetrievalPort"]
