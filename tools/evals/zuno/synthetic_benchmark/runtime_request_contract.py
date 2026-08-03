from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.evals.zuno.synthetic_benchmark.dataset_contract import (
    GOLD_RUNTIME_FORBIDDEN_FIELDS,
    load_jsonl,
    sha256_json,
)


GOLD_RUNTIME_FORBIDDEN_FIELDS_EXTENDED = frozenset(
    {
        *GOLD_RUNTIME_FORBIDDEN_FIELDS,
        "expected_answer",
        "expected_behavior",
        "failure_expectation",
        "source_span_refs",
        "derivation_spec",
        "world_model",
        "world_model_ref",
    }
)

RUNTIME_REQUEST_ALLOWED_FIELDS = frozenset(
    {
        "request_id",
        "case_id",
        "question",
        "question_type",
        "tenant_id",
        "workspace_id",
        "security_principal",
        "security_epoch_ref",
        "dataset_hash",
        "corpus_hash",
        "knowledge_version_id",
        "snapshot_id",
        "profile_id",
        "retrieval_policy",
        "answer_policy",
        "budget_policy",
    }
)

REQUIRED_PROFILES = (
    "standard_rag",
    "local_graphrag",
    "deep_graphrag",
    "agentic_graphrag",
)


@dataclass
class RuntimeIsolationValidation:
    passed: bool
    errors: list[str] = field(default_factory=list)
    case_count: int = 0
    request_count: int = 0
    forbidden_field_count: int = 0
    runtime_request_hash: str | None = None


def build_runtime_requests(
    cases: list[dict[str, Any]],
    *,
    dataset_hash: str,
    corpus_hash: str,
    knowledge_version_id: str | None = None,
    snapshot_id: str | None = None,
) -> list[dict[str, Any]]:
    requests: list[dict[str, Any]] = []
    for case in cases:
        for profile_id in REQUIRED_PROFILES:
            request = {
                "request_id": f"{case['case_id']}::{profile_id}",
                "case_id": case["case_id"],
                "question": case["question"],
                "question_type": case["question_type"],
                "tenant_id": case["tenant_id"],
                "workspace_id": case["workspace_id"],
                "security_principal": case["security_principal"],
                "security_epoch_ref": case["security_epoch_ref"],
                "dataset_hash": dataset_hash,
                "corpus_hash": corpus_hash,
                "knowledge_version_id": knowledge_version_id,
                "snapshot_id": snapshot_id,
                "profile_id": profile_id,
                "retrieval_policy": {
                    "runtime_may_read_case_file": False,
                    "runtime_may_read_gold": False,
                    "runtime_may_read_world_model": False,
                },
                "answer_policy": {
                    "require_citation_from_runtime_evidence": True,
                    "allow_direct_expected_answer": False,
                },
                "budget_policy": {
                    "budget_class": "phase22_synthetic_regression_default",
                },
            }
            requests.append(request)
    return requests


def validate_runtime_isolation(requests: list[dict[str, Any]]) -> RuntimeIsolationValidation:
    errors: list[str] = []
    forbidden_field_count = 0
    request_ids: set[str] = set()
    case_ids: set[str] = set()
    for request in requests:
        request_id = request.get("request_id", "<missing>")
        case_ids.add(str(request.get("case_id", "<missing>")))
        unknown = sorted(set(request) - RUNTIME_REQUEST_ALLOWED_FIELDS)
        if unknown:
            errors.append(f"{request_id}: runtime request contains unknown fields {unknown}")
        forbidden = sorted(GOLD_RUNTIME_FORBIDDEN_FIELDS_EXTENDED & set(request))
        if forbidden:
            forbidden_field_count += len(forbidden)
            errors.append(f"{request_id}: runtime request contains forbidden gold fields {forbidden}")
        if request_id in request_ids:
            errors.append(f"{request_id}: duplicate runtime request")
        request_ids.add(str(request_id))
        retrieval_policy = request.get("retrieval_policy")
        if not isinstance(retrieval_policy, dict):
            errors.append(f"{request_id}: retrieval_policy must be an object")
        else:
            for field_name in [
                "runtime_may_read_case_file",
                "runtime_may_read_gold",
                "runtime_may_read_world_model",
            ]:
                if retrieval_policy.get(field_name) is not False:
                    errors.append(f"{request_id}: {field_name} must be false")
        answer_policy = request.get("answer_policy")
        if not isinstance(answer_policy, dict):
            errors.append(f"{request_id}: answer_policy must be an object")
        else:
            if answer_policy.get("require_citation_from_runtime_evidence") is not True:
                errors.append(f"{request_id}: citations must come from runtime evidence")
            if answer_policy.get("allow_direct_expected_answer") is not False:
                errors.append(f"{request_id}: direct expected_answer must be disabled")
    return RuntimeIsolationValidation(
        passed=not errors,
        errors=errors,
        case_count=len(case_ids),
        request_count=len(requests),
        forbidden_field_count=forbidden_field_count,
        runtime_request_hash=sha256_json(requests),
    )


def write_runtime_isolation_report(
    out_root: Path,
    *,
    cases_path: Path,
    dataset_hash: str,
    corpus_hash: str,
) -> dict[str, Any]:
    cases = load_jsonl(cases_path)
    requests = build_runtime_requests(cases, dataset_hash=dataset_hash, corpus_hash=corpus_hash)
    validation = validate_runtime_isolation(requests)
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "runtime_request_manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "track_id": "machine_attested_synthetic_regression",
                "status": "RUNTIME_INPUT_GOLD_ISOLATED",
                "runtime_request_hash": validation.runtime_request_hash,
                "case_count": validation.case_count,
                "request_count": validation.request_count,
                "profiles": list(REQUIRED_PROFILES),
                "dataset_hash": dataset_hash,
                "corpus_hash": corpus_hash,
                "knowledge_version_id": None,
                "snapshot_id": None,
                "runtime_may_read_case_file": False,
                "runtime_may_read_gold": False,
                "runtime_may_read_world_model": False,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
        newline="\n",
    )
    (out_root / "runtime_gold_isolation_report.json").write_text(
        json.dumps(validation.__dict__, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    return validation.__dict__


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-root", required=True, type=Path)
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--dataset-hash", required=True)
    parser.add_argument("--corpus-hash", required=True)
    args = parser.parse_args()
    result = write_runtime_isolation_report(
        args.out_root,
        cases_path=args.cases,
        dataset_hash=args.dataset_hash,
        corpus_hash=args.corpus_hash,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
