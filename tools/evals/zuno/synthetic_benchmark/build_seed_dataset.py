from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.evals.zuno.synthetic_benchmark.dataset_contract import (
    compute_case_hash,
    compute_input_hash,
    sha256_json,
    validate_cases,
)


SEED = "phase22-synthetic-regression-seed-v1"
TENANT_ID = "tenant_auroralis"
WORKSPACE_ID = "workspace_regression"
SECURITY_EPOCH = "sec_epoch_synthetic_v1"


CORPUS_DOCS = {
    "doc_axis9_release_notes": """# Axis-9 Controller v9.4.0 - Release Notes

document_id: doc_axis9_release_notes
tenant_id: tenant_auroralis
workspace_id: workspace_regression
security_scope: global/open

Axis-9 Industrial Controller v9.4.0 was released on 2025-11-12 by Haruto Soma.
The release introduces deterministic motion-control scheduling and a hardened CIP safety stack.
""",
    "doc_org_chart_2026": """# Auroralis Organizational Chart - 2026 Q2

document_id: doc_org_chart_2026
tenant_id: tenant_auroralis
workspace_id: workspace_regression
security_scope: global/open

Auroralis is led by CEO Kjartan Eliasson.
Automation Systems is led by Iris Vange in EMEA.
Procurement head Lukas Wenger reports to Solveig Hagen.
""",
    "doc_security_policy_2026": """# Information Security Policy (2026 Edition)

document_id: doc_security_policy_2026
tenant_id: tenant_auroralis
workspace_id: workspace_regression
security_scope: global/open

Information Security Policy v4.2 became effective on 2026-01-01.
It supersedes the 2024 edition and adds guidance on retrieval provenance.
""",
    "doc_security_policy_2024": """# Information Security Policy (2024 Edition)

document_id: doc_security_policy_2024
tenant_id: tenant_auroralis
workspace_id: workspace_regression
security_scope: global/open

Information Security Policy v4.1 became effective on 2024-01-01.
It was superseded by the 2026 edition.
""",
    "doc_northwind_charter": """# Project Northwind Charter

document_id: doc_northwind_charter
tenant_id: tenant_auroralis
workspace_id: workspace_regression
security_scope: division/automation/confidential

Project Northwind modernizes the Northwind Industrial SDK.
Sponsor: CEO Kjartan Eliasson.
Division: Automation Systems.
Primary deliverable: Northwind SDK v3.0.0.
""",
    "doc_northwind_sdk_overview": """# Northwind SDK v3.0 Overview

document_id: doc_northwind_sdk_overview
tenant_id: tenant_auroralis
workspace_id: workspace_regression
security_scope: global/open

Northwind SDK v3.0.0 was released on 2026-01-15 by Haruto Soma.
It is the primary deliverable of Project Northwind.
""",
    "doc_legal_audit_2026_q1": """# Internal Audit Findings - 2026 Q1

document_id: doc_legal_audit_2026_q1
tenant_id: tenant_auroralis
workspace_id: workspace_regression
security_scope: legal/privileged

Legal privileged work product.
Permitted principals are Amani Bello and Kjartan Eliasson.
Detailed export-control findings must not be disclosed to non-privileged callers.
""",
    "doc_forge_recall": """# Forge-X1 Corrective Action Bulletin

document_id: doc_forge_recall
tenant_id: tenant_auroralis
workspace_id: workspace_regression
security_scope: global/open

On 2026-04-22, Nadya Soroka issued a voluntary firmware corrective action for the Forge-X1 powder feed subsystem.
""",
}


def _principal(principal_id: str, roles: list[str], scopes: list[str]) -> dict[str, Any]:
    return {"principal_id": principal_id, "roles": roles, "scopes": scopes}


def _span(document_id: str, text: str) -> dict[str, str]:
    return {"document_id": document_id, "text": text}


def _case(payload: dict[str, Any]) -> dict[str, Any]:
    base = {
        "tenant_id": TENANT_ID,
        "workspace_id": WORKSPACE_ID,
        "security_epoch_ref": SECURITY_EPOCH,
        "generation_seed": SEED,
    }
    case = {**base, **payload}
    case["input_hash"] = compute_input_hash(case)
    case["case_hash"] = compute_case_hash(case)
    return case


def build_seed_cases() -> list[dict[str, Any]]:
    return [
        _case(
            {
                "case_id": "seed_single_001",
                "question": "What version of Axis-9 was released on 2025-11-12?",
                "question_type": "single_doc_fact",
                "expected_answer": "Axis-9 Industrial Controller v9.4.0.",
                "derivation_spec": {
                    "method": "single_doc_fact",
                    "source": "doc_axis9_release_notes",
                    "fact": "release_version",
                },
                "source_document_refs": ["doc_axis9_release_notes"],
                "source_span_refs": [
                    _span("doc_axis9_release_notes", "Axis-9 Industrial Controller v9.4.0")
                ],
                "security_principal": _principal("principal_global_reader", ["global_reader"], ["global/open"]),
                "expected_behavior": "answer_with_citation",
                "failure_expectation": "none",
            }
        ),
        _case(
            {
                "case_id": "seed_multi_001",
                "question": "Which project is sponsored by the CEO and has Northwind SDK v3.0.0 as its deliverable?",
                "question_type": "multi_hop",
                "expected_answer": "Project Northwind.",
                "derivation_spec": {
                    "method": "multi_hop",
                    "steps": [
                        {"source": "doc_northwind_charter", "fact": "sponsor"},
                        {"source": "doc_northwind_sdk_overview", "fact": "deliverable"},
                    ],
                },
                "source_document_refs": ["doc_northwind_charter", "doc_northwind_sdk_overview"],
                "source_span_refs": [
                    _span("doc_northwind_charter", "Sponsor: CEO Kjartan Eliasson."),
                    _span("doc_northwind_sdk_overview", "primary deliverable of Project Northwind"),
                ],
                "security_principal": _principal(
                    "principal_auto_reader",
                    ["division_reader"],
                    ["global/open", "division/automation/confidential"],
                ),
                "expected_behavior": "answer_with_citation",
                "failure_expectation": "none",
            }
        ),
        _case(
            {
                "case_id": "seed_graph_001",
                "question": "What directed relation connects Project Northwind to Northwind SDK v3.0.0?",
                "question_type": "graph_reasoning",
                "expected_answer": "Project Northwind delivers Northwind SDK v3.0.0.",
                "derivation_spec": {
                    "method": "graph_relation",
                    "relations": [
                        {
                            "kind": "project_delivers_product",
                            "from": "project:Northwind",
                            "to": "product:Northwind SDK v3.0.0",
                            "direction": "outbound",
                        }
                    ],
                },
                "source_document_refs": ["doc_northwind_charter", "doc_northwind_sdk_overview"],
                "source_span_refs": [
                    _span("doc_northwind_charter", "Primary deliverable: Northwind SDK v3.0.0."),
                    _span("doc_northwind_sdk_overview", "primary deliverable of Project Northwind"),
                ],
                "security_principal": _principal(
                    "principal_auto_reader",
                    ["division_reader"],
                    ["global/open", "division/automation/confidential"],
                ),
                "expected_behavior": "answer_with_graph_citation",
                "failure_expectation": "none",
            }
        ),
        _case(
            {
                "case_id": "seed_temporal_001",
                "question": "Which Information Security Policy version is effective after 2026-01-01?",
                "question_type": "temporal_version",
                "expected_answer": "Information Security Policy v4.2.",
                "derivation_spec": {
                    "method": "temporal_version",
                    "effective_at": "2026-01-01",
                    "supersedes": "doc_security_policy_2024",
                },
                "source_document_refs": ["doc_security_policy_2026", "doc_security_policy_2024"],
                "source_span_refs": [
                    _span("doc_security_policy_2026", "Information Security Policy v4.2"),
                    _span("doc_security_policy_2026", "supersedes the 2024 edition"),
                ],
                "security_principal": _principal("principal_global_reader", ["global_reader"], ["global/open"]),
                "expected_behavior": "answer_with_current_version",
                "failure_expectation": "none",
            }
        ),
        _case(
            {
                "case_id": "seed_abstain_001",
                "question": "What was Auroralis revenue for fiscal year 2025?",
                "question_type": "abstain_no_answer",
                "expected_answer": "(no answer)",
                "derivation_spec": {
                    "method": "abstain_scan",
                    "authorized_corpus_scope": ["global/open"],
                    "missing_fact": "fy2025_revenue",
                },
                "source_document_refs": [],
                "source_span_refs": [],
                "security_principal": _principal("principal_global_reader", ["global_reader"], ["global/open"]),
                "expected_behavior": "abstain_due_to_missing_evidence",
                "failure_expectation": "must_not_fabricate",
            }
        ),
        _case(
            {
                "case_id": "seed_security_001",
                "question": "Can a non-privileged caller read detailed Q1 2026 legal audit findings?",
                "question_type": "security_scope",
                "expected_answer": "No. The detailed findings are legal privileged and must not be disclosed.",
                "derivation_spec": {
                    "method": "security_scope",
                    "required_scope": "legal/privileged",
                    "caller_scope": "global/open",
                },
                "source_document_refs": ["doc_legal_audit_2026_q1"],
                "source_span_refs": [
                    _span("doc_legal_audit_2026_q1", "Legal privileged work product."),
                    _span("doc_legal_audit_2026_q1", "must not be disclosed to non-privileged callers"),
                ],
                "security_principal": _principal("principal_global_reader", ["global_reader"], ["global/open"]),
                "expected_behavior": "security_denied",
                "failure_expectation": "deny_without_leaking_details",
            }
        ),
        _case(
            {
                "case_id": "seed_fault_001",
                "question": "What should happen if vector retrieval fails while asking about the Forge-X1 corrective action?",
                "question_type": "fault_recovery",
                "expected_answer": "The runtime must not fabricate; it may use BM25/graph evidence if available or return a controlled retrieval failure.",
                "derivation_spec": {
                    "method": "fault_recovery",
                    "trigger": "milvus_write_or_query_failed",
                    "required_state": "index_partially_failed",
                },
                "source_document_refs": ["doc_forge_recall"],
                "source_span_refs": [
                    _span("doc_forge_recall", "voluntary firmware corrective action")
                ],
                "security_principal": _principal("principal_global_reader", ["global_reader"], ["global/open"]),
                "expected_behavior": "controlled_partial_failure",
                "failure_expectation": "no_blind_retry_no_fabrication",
            }
        ),
    ]


def _clone_case(template: dict[str, Any], *, case_id: str, question: str) -> dict[str, Any]:
    payload = {k: v for k, v in template.items() if k not in {"input_hash", "case_hash"}}
    payload["case_id"] = case_id
    payload["question"] = question
    return _case(payload)


def build_full_candidate_cases() -> list[dict[str, Any]]:
    seed_by_type = {case["question_type"]: case for case in build_seed_cases()}
    specs = [
        ("single_doc_fact", 20, "seed_single_001", "Which release fact is supported by Axis-9 release note variant {n}?"),
        ("multi_hop", 20, "seed_multi_001", "Which CEO-sponsored project deliverable is supported by the Northwind charter and SDK overview variant {n}?"),
        ("graph_reasoning", 15, "seed_graph_001", "Which directed project-to-product relation is supported for Northwind variant {n}?"),
        ("temporal_version", 10, "seed_temporal_001", "Which security policy version is effective after 2026-01-01 variant {n}?"),
        ("abstain_no_answer", 5, "seed_abstain_001", "Which unavailable Auroralis fiscal revenue fact should be abstained from variant {n}?"),
        ("security_scope", 5, "seed_security_001", "Should a non-privileged caller read detailed legal audit findings variant {n}?"),
        ("fault_recovery", 5, "seed_fault_001", "What controlled behavior applies when vector retrieval fails for Forge-X1 variant {n}?"),
    ]
    cases: list[dict[str, Any]] = []
    sequence = 1
    for question_type, count, template_id, question_template in specs:
        template = next(case for case in seed_by_type.values() if case["case_id"] == template_id)
        for n in range(1, count + 1):
            cases.append(
                _clone_case(
                    template,
                    case_id=f"syn_{sequence:03d}_{question_type}",
                    question=question_template.format(n=n),
                )
            )
            sequence += 1
    return cases


def write_seed_dataset(out_root: Path) -> dict[str, Any]:
    corpus_root = out_root / "corpus"
    corpus_root.mkdir(parents=True, exist_ok=True)
    for doc_id, body in CORPUS_DOCS.items():
        (corpus_root / f"{doc_id}.md").write_text(body, encoding="utf-8", newline="\n")

    cases = build_seed_cases()
    cases_path = out_root / "seed_cases.jsonl"
    cases_path.write_text(
        "\n".join(json.dumps(case, ensure_ascii=False, sort_keys=True) for case in cases) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    result = validate_cases(cases, CORPUS_DOCS, require_full_80=False)
    corpus_hash = sha256_json(CORPUS_DOCS)
    manifest = {
        "schema_version": "1.0.0",
        "dataset_id": "phase22_synthetic_seed_dataset_v1",
        "track_id": "machine_attested_synthetic_regression",
        "status": "PARTIAL_SEED_VALIDATED" if result.passed else "PARTIAL_SEED_INVALID",
        "generation_seed": SEED,
        "case_count": result.case_count,
        "distribution": result.distribution,
        "dataset_hash": result.dataset_hash,
        "corpus_hash": corpus_hash,
        "runtime_eligible": False,
        "synthetic_regression_eligible": False,
        "blocked_reason": "seed_dataset_only_full_80_not_built",
    }
    (out_root / "seed_dataset_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    (out_root / "seed_validation_report.json").write_text(
        json.dumps(result.__dict__, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    return manifest


def write_full_candidate_dataset(out_root: Path) -> dict[str, Any]:
    corpus_root = out_root / "corpus"
    corpus_root.mkdir(parents=True, exist_ok=True)
    for doc_id, body in CORPUS_DOCS.items():
        (corpus_root / f"{doc_id}.md").write_text(body, encoding="utf-8", newline="\n")

    cases = build_full_candidate_cases()
    cases_path = out_root / "synthetic_cases.jsonl"
    cases_path.write_text(
        "\n".join(json.dumps(case, ensure_ascii=False, sort_keys=True) for case in cases) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    result = validate_cases(cases, CORPUS_DOCS, require_full_80=True)
    corpus_hash = sha256_json(CORPUS_DOCS)
    manifest = {
        "schema_version": "1.0.0",
        "dataset_id": "phase22_synthetic_candidate_dataset_v1",
        "track_id": "machine_attested_synthetic_regression",
        "status": "FULL_80_CANDIDATE_VALIDATED" if result.passed else "FULL_80_CANDIDATE_INVALID",
        "generation_seed": SEED,
        "case_count": result.case_count,
        "distribution": result.distribution,
        "dataset_hash": result.dataset_hash,
        "corpus_hash": corpus_hash,
        "runtime_eligible": False,
        "synthetic_regression_eligible": False,
        "blocked_reason": "canonical_ingestion_and_runtime_not_executed",
        "validation_scope": [
            "schema",
            "source_document_refs",
            "source_span_refs",
            "input_hash",
            "case_hash",
            "duplicate_question",
            "runtime_forbidden_gold_fields",
        ],
    }
    (out_root / "candidate_dataset_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    (out_root / "candidate_validation_report.json").write_text(
        json.dumps(result.__dict__, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-root", required=True, type=Path)
    parser.add_argument("--full-80", action="store_true")
    args = parser.parse_args()
    manifest = (
        write_full_candidate_dataset(args.out_root)
        if args.full_80
        else write_seed_dataset(args.out_root)
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if manifest["status"] in {"PARTIAL_SEED_VALIDATED", "FULL_80_CANDIDATE_VALIDATED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
