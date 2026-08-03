from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from tools.evals.zuno.synthetic_benchmark.fixtures import ALL_CASES
from tools.evals.zuno.synthetic_benchmark.spec import DirectedEdge, Fact, TemporalVersion
from zuno.knowledge.ingestion import PackageAUploadCommand


@dataclass(frozen=True, slots=True)
class AuroralisSourceUpload:
    case_id: str
    question_type: str
    source_hash: str
    source_object_id: str
    command: PackageAUploadCommand


def auroralis_representative_uploads(
    *,
    tenant_id: str,
    workspace_id: str,
    principal_id: str,
    bucket: str,
    classification_ref: str,
    security_epoch_ref: str,
    trace_prefix: str = "trace:phase22:auroralis",
) -> tuple[AuroralisSourceUpload, ...]:
    """Convert the three DerivationSpec cases into formal Package A upload commands."""

    uploads: list[AuroralisSourceUpload] = []
    for case in ALL_CASES:
        case_id = str(case["case_id"])
        content = _case_markdown(case).encode("utf-8")
        source_hash = hashlib.sha256(content).hexdigest()
        source_object_id = f"source:auroralis:{case_id}:{source_hash[:16]}"
        uploads.append(
            AuroralisSourceUpload(
                case_id=case_id,
                question_type=str(case["question_type"]),
                source_hash=source_hash,
                source_object_id=source_object_id,
                command=PackageAUploadCommand(
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    principal_id=principal_id,
                    filename=f"{case_id}.md",
                    mime_type="text/markdown",
                    content=content,
                    bucket=bucket,
                    source_object_id=source_object_id,
                    classification_ref=classification_ref,
                    security_epoch_ref=security_epoch_ref,
                    trace_id=f"{trace_prefix}:{case_id}",
                ),
            )
        )
    return tuple(uploads)


def _case_markdown(case: dict[str, Any]) -> str:
    inputs = case["build"]["inputs"]()
    lines = [
        f"# Auroralis case {case['case_id']}",
        "",
        f"Question type: {case['question_type']}",
        f"Question: {case['question']}",
        "",
    ]
    if inputs.facts:
        lines.append("## Facts")
        for fact in sorted(inputs.facts.values(), key=lambda item: item.fact_id):
            lines.extend(_fact_lines(fact))
    if inputs.graph:
        lines.append("## Directed graph")
        for edge in inputs.graph:
            lines.extend(_edge_lines(edge))
    if inputs.versions:
        lines.append("## Temporal versions")
        for version in inputs.versions:
            lines.extend(_version_lines(version))
    return "\n".join(lines).strip() + "\n"


def _fact_lines(fact: Fact) -> list[str]:
    return [
        f"- fact_id: {fact.fact_id}",
        f"  answer_field: {fact.answer_field}",
        f"  value: {fact.value}",
        f"  source_doc_id: {fact.span.doc_id}",
        f"  source_version: {fact.span.version}",
        f"  source_text: {fact.span.text}",
    ]


def _edge_lines(edge: DirectedEdge) -> list[str]:
    return [
        f"- kind: {edge.kind}",
        f"  from: {edge.from_id}",
        f"  to: {edge.to_id}",
        f"  direction: {edge.direction.value}",
    ]


def _version_lines(version: TemporalVersion) -> list[str]:
    return [
        f"- artifact_id: {version.artifact_id}",
        f"  version: {version.version}",
        f"  effective_at: {version.effective_at}",
        f"  superseded_by: {', '.join(version.superseded_by) or 'none'}",
        f"  source_doc_id: {version.span.doc_id}",
        f"  source_text: {version.span.text}",
    ]


__all__ = ["AuroralisSourceUpload", "auroralis_representative_uploads"]
