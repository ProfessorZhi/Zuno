from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Iterable


class HookPoint(StrEnum):
    PRE_RETRIEVAL = "pre_retrieval"
    POST_RETRIEVAL = "post_retrieval"
    PRE_TOOL = "pre_tool"
    POST_TOOL = "post_tool"
    POST_ANSWER = "post_answer"


@dataclass(frozen=True, slots=True)
class RuntimeTraceEvent:
    event_id: str
    trace_id: str
    sequence: int
    kind: HookPoint
    status: str
    refs: dict[str, tuple[str, ...]] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "trace_id": self.trace_id,
            "sequence": self.sequence,
            "kind": self.kind.value,
            "status": self.status,
            "refs": {name: list(values) for name, values in self.refs.items()},
            "metadata": dict(self.metadata),
        }


class RuntimeTraceBuilder:
    def __init__(self, *, trace_id: str, product_mode: str | None = None):
        self.trace_id = str(trace_id or "trace")
        self.product_mode = str(product_mode or "auto").strip().lower() or "auto"
        self._events: list[RuntimeTraceEvent] = []

    @property
    def events(self) -> tuple[RuntimeTraceEvent, ...]:
        return tuple(self._events)

    def record(
        self,
        kind: HookPoint | str,
        *,
        status: str,
        refs: dict[str, Iterable[str]] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RuntimeTraceEvent:
        hook_point = HookPoint(kind)
        sequence = len(self._events) + 1
        event = RuntimeTraceEvent(
            event_id=f"{self.trace_id}:{sequence:04d}:{hook_point.value}",
            trace_id=self.trace_id,
            sequence=sequence,
            kind=hook_point,
            status=str(status or "unknown"),
            refs={
                name: tuple(_ordered_unique(values))
                for name, values in dict(refs or {}).items()
            },
            metadata=dict(metadata or {}),
        )
        self._events.append(event)
        return event

    def to_dicts(self) -> list[dict[str, Any]]:
        return [event.to_dict() for event in self._events]


@dataclass(frozen=True, slots=True)
class EvidenceVerdict:
    status: str
    citation_coverage: float
    document_count: int
    cited_document_count: int
    fallback_reason: str | None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "citation_coverage": self.citation_coverage,
            "document_count": self.document_count,
            "cited_document_count": self.cited_document_count,
            "fallback_reason": self.fallback_reason,
            "details": dict(self.details),
        }


class EvidenceChecker:
    def __init__(self, *, citation_coverage_threshold: float = 0.8):
        self.citation_coverage_threshold = max(0.0, min(float(citation_coverage_threshold), 1.0))

    def evaluate(
        self,
        *,
        product_mode: str | None,
        evidence_bundle: dict[str, Any] | None,
        citations: Iterable[str] | None,
        fallback_reason: str | None,
    ) -> EvidenceVerdict:
        bundle = dict(evidence_bundle or {})
        document_count = int(bundle.get("document_count") or len(bundle.get("chunk_ids") or []))
        cited_chunks = _ordered_unique(bundle.get("citation_chunks") or citations or [])
        cited_document_count = int(bundle.get("cited_document_count") or len(cited_chunks))
        coverage = bundle.get("citation_coverage")
        if coverage is None:
            coverage = cited_document_count / document_count if document_count else 0.0
        coverage = max(0.0, min(float(coverage), 1.0))
        mode = str(product_mode or "auto").strip().lower() or "auto"
        threshold = self.citation_coverage_threshold

        status = "pass"
        reason = fallback_reason
        if mode == "enhanced" and document_count <= 0:
            status = "low_confidence"
            reason = reason or "evidence_missing"
        elif mode == "enhanced" and coverage < threshold:
            status = "low_confidence"
            reason = reason or "citation_coverage_below_threshold"

        return EvidenceVerdict(
            status=status,
            citation_coverage=coverage,
            document_count=document_count,
            cited_document_count=cited_document_count,
            fallback_reason=reason,
            details={
                "product_mode": mode,
                "threshold": threshold,
                "citation_count": len(cited_chunks),
            },
        )


@dataclass(frozen=True, slots=True)
class TraceArtifactManifest:
    trace_id: str
    input_refs: tuple[str, ...]
    retrieval_refs: tuple[str, ...]
    tool_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    output_refs: tuple[str, ...]
    event_ids: tuple[str, ...]
    evidence_verdict: EvidenceVerdict
    fallback_reason: str | None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_trace(
        cls,
        *,
        trace_id: str,
        query: str,
        answer: str,
        documents: list[dict[str, Any]],
        evidence_bundle: dict[str, Any],
        citations: Iterable[str],
        events: Iterable[RuntimeTraceEvent],
        evidence_verdict: EvidenceVerdict,
        fallback_reason: str | None,
    ) -> TraceArtifactManifest:
        event_list = list(events)
        input_refs = _ordered_unique(
            _refs_from_events(event_list, "input")
            or [f"query:{_stable_ref_text(query)}"]
        )
        retrieval_refs = _ordered_unique(
            _document_refs(documents)
            or evidence_bundle.get("chunk_ids")
            or _refs_from_events(event_list, "retrieval")
        )
        tool_refs = _ordered_unique(_refs_from_events(event_list, "tool"))
        evidence_refs = _ordered_unique(
            evidence_bundle.get("citation_chunks")
            or citations
            or _refs_from_events(event_list, "evidence")
        )
        output_refs = _ordered_unique(
            _refs_from_events(event_list, "output")
            or [f"answer:{trace_id}"]
        )
        return cls(
            trace_id=str(trace_id or "trace"),
            input_refs=tuple(input_refs),
            retrieval_refs=tuple(retrieval_refs),
            tool_refs=tuple(tool_refs),
            evidence_refs=tuple(evidence_refs),
            output_refs=tuple(output_refs),
            event_ids=tuple(event.event_id for event in event_list),
            evidence_verdict=evidence_verdict,
            fallback_reason=fallback_reason or evidence_verdict.fallback_reason,
            metadata={
                "answer_present": bool(str(answer or "").strip()),
                "document_count": len(documents or []),
            },
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "input_refs": list(self.input_refs),
            "retrieval_refs": list(self.retrieval_refs),
            "tool_refs": list(self.tool_refs),
            "evidence_refs": list(self.evidence_refs),
            "output_refs": list(self.output_refs),
            "event_ids": list(self.event_ids),
            "evidence_verdict": self.evidence_verdict.to_dict(),
            "fallback_reason": self.fallback_reason,
            "metadata": dict(self.metadata),
        }


def enrich_trace_metadata_with_artifacts(
    *,
    trace_metadata: dict[str, Any],
    query: str,
    answer: str,
    documents: list[dict[str, Any]],
    evidence_bundle: dict[str, Any],
    citations: Iterable[str],
    fallback_reason: str | None,
) -> dict[str, Any]:
    metadata = dict(trace_metadata or {})
    product_mode = metadata.get("resolved_product_mode") or metadata.get("requested_product_mode")
    trace_id = str(metadata.get("trace_id") or "retrieval-trace")
    checker = EvidenceChecker()
    verdict = checker.evaluate(
        product_mode=str(product_mode or "auto"),
        evidence_bundle=evidence_bundle,
        citations=citations,
        fallback_reason=fallback_reason,
    )
    builder = RuntimeTraceBuilder(trace_id=trace_id, product_mode=str(product_mode or "auto"))
    builder.record(
        HookPoint.PRE_RETRIEVAL,
        status="started",
        refs={"input": [f"query:{_stable_ref_text(query)}"]},
        metadata={
            "requested_product_mode": metadata.get("requested_product_mode"),
            "requested_query_method": metadata.get("requested_query_method"),
        },
    )
    builder.record(
        HookPoint.POST_RETRIEVAL,
        status="completed" if documents else "empty",
        refs={"retrieval": _document_refs(documents)},
        metadata={
            "retrievers_used": list(metadata.get("retrievers_used") or []),
            "resolved_query_method": metadata.get("resolved_query_method"),
        },
    )
    builder.record(
        HookPoint.POST_ANSWER,
        status="completed" if verdict.status == "pass" else verdict.status,
        refs={
            "evidence": evidence_bundle.get("citation_chunks") or list(citations or []),
            "output": [f"answer:{trace_id}"],
        },
        metadata={"evidence_verdict": verdict.to_dict()},
    )
    manifest = TraceArtifactManifest.from_trace(
        trace_id=trace_id,
        query=query,
        answer=answer,
        documents=documents,
        evidence_bundle=evidence_bundle,
        citations=citations,
        events=builder.events,
        evidence_verdict=verdict,
        fallback_reason=fallback_reason,
    )
    metadata["runtime_trace_events"] = builder.to_dicts()
    metadata["evidence_verdict"] = verdict.to_dict()
    metadata["artifact_manifest"] = manifest.to_dict()
    metadata["fallback_reason"] = metadata.get("fallback_reason") or verdict.fallback_reason
    metadata["pipeline_trace"] = _append_pipeline_artifact_step(
        metadata.get("pipeline_trace"),
        manifest=manifest,
        verdict=verdict,
    )
    return metadata


def _append_pipeline_artifact_step(
    pipeline_trace: Any,
    *,
    manifest: TraceArtifactManifest,
    verdict: EvidenceVerdict,
) -> dict[str, Any]:
    trace = dict(pipeline_trace or {})
    steps = list(trace.get("steps") or [])
    if not any(dict(step).get("name") == "evidence_verdict" for step in steps):
        steps.append(
            {
                "name": "evidence_verdict",
                "status": verdict.status,
                "detail": {
                    "citation_coverage": verdict.citation_coverage,
                    "fallback_reason": verdict.fallback_reason,
                },
            }
        )
    if not any(dict(step).get("name") == "artifact_manifest" for step in steps):
        steps.append(
            {
                "name": "artifact_manifest",
                "status": "created",
                "detail": {
                    "trace_id": manifest.trace_id,
                    "event_count": len(manifest.event_ids),
                },
            }
        )
    trace["steps"] = steps
    return trace


def _ordered_unique(values: Iterable[Any]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for value in values or []:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        ordered.append(text)
    return ordered


def _document_refs(documents: Iterable[dict[str, Any]]) -> list[str]:
    refs: list[str] = []
    for document in documents or []:
        ref = document.get("chunk_id") or document.get("id") or document.get("document_id")
        if ref:
            refs.append(str(ref))
    return _ordered_unique(refs)


def _refs_from_events(events: Iterable[RuntimeTraceEvent], ref_name: str) -> list[str]:
    refs: list[str] = []
    for event in events:
        refs.extend(event.refs.get(ref_name, ()))
    return _ordered_unique(refs)


def _stable_ref_text(value: str) -> str:
    text = str(value or "").strip()
    return text[:80] if text else "empty"


__all__ = [
    "EvidenceChecker",
    "EvidenceVerdict",
    "HookPoint",
    "RuntimeTraceBuilder",
    "RuntimeTraceEvent",
    "TraceArtifactManifest",
    "enrich_trace_metadata_with_artifacts",
]
