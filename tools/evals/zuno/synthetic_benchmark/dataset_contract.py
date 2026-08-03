from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


REQUIRED_CASE_FIELDS = frozenset(
    {
        "case_id",
        "question",
        "question_type",
        "expected_answer",
        "derivation_spec",
        "source_document_refs",
        "source_span_refs",
        "security_principal",
        "tenant_id",
        "workspace_id",
        "security_epoch_ref",
        "expected_behavior",
        "failure_expectation",
        "generation_seed",
        "input_hash",
        "case_hash",
    }
)

EXPECTED_DISTRIBUTION = {
    "single_doc_fact": 20,
    "multi_hop": 20,
    "graph_reasoning": 15,
    "temporal_version": 10,
    "abstain_no_answer": 5,
    "security_scope": 5,
    "fault_recovery": 5,
}

GOLD_RUNTIME_FORBIDDEN_FIELDS = frozenset(
    {
        "gold_document_ids",
        "gold_source_spans",
        "gold_citations",
        "gold_document_refs",
        "gold_evidence_refs",
        "citation_ground_truth",
        "expected_path",
    }
)


@dataclass
class DatasetValidationResult:
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    case_count: int = 0
    distribution: dict[str, int] = field(default_factory=dict)
    dataset_hash: str | None = None
    duplicate_case_id_count: int = 0
    duplicate_question_count: int = 0
    gold_leakage_count: int = 0


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


def sha256_json(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def compute_input_hash(case: dict[str, Any]) -> str:
    payload = {
        "case_id": case.get("case_id"),
        "question": case.get("question"),
        "question_type": case.get("question_type"),
        "derivation_spec": case.get("derivation_spec"),
        "source_document_refs": case.get("source_document_refs"),
        "source_span_refs": case.get("source_span_refs"),
        "security_principal": case.get("security_principal"),
        "tenant_id": case.get("tenant_id"),
        "workspace_id": case.get("workspace_id"),
        "security_epoch_ref": case.get("security_epoch_ref"),
        "generation_seed": case.get("generation_seed"),
    }
    return sha256_json(payload)


def compute_case_hash(case: dict[str, Any]) -> str:
    payload = dict(case)
    payload.pop("case_hash", None)
    return sha256_json(payload)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_corpus(corpus_root: Path) -> dict[str, str]:
    docs: dict[str, str] = {}
    for path in sorted(corpus_root.glob("*.md")):
        docs[path.stem] = path.read_text(encoding="utf-8")
    return docs


def validate_cases(
    cases: list[dict[str, Any]],
    corpus_docs: dict[str, str],
    *,
    require_full_80: bool = True,
) -> DatasetValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    questions: set[str] = set()
    case_ids: set[str] = set()
    duplicate_case_id_count = 0
    duplicate_question_count = 0
    gold_leakage_count = 0
    distribution = Counter(case.get("question_type", "<missing>") for case in cases)

    if require_full_80 and len(cases) != 80:
        errors.append(f"expected 80 cases, got {len(cases)}")
    if require_full_80 and dict(distribution) != EXPECTED_DISTRIBUTION:
        errors.append(
            f"case distribution mismatch: expected {EXPECTED_DISTRIBUTION}, got {dict(distribution)}"
        )

    for index, case in enumerate(cases, start=1):
        label = case.get("case_id", f"<case-{index}>")
        missing = sorted(REQUIRED_CASE_FIELDS - set(case))
        if missing:
            errors.append(f"{label}: missing required fields {missing}")
            continue

        forbidden = sorted(GOLD_RUNTIME_FORBIDDEN_FIELDS & set(case))
        if forbidden:
            gold_leakage_count += 1
            errors.append(f"{label}: contains runtime-forbidden gold fields {forbidden}")

        if case["case_id"] in case_ids:
            duplicate_case_id_count += 1
            errors.append(f"{label}: duplicate case_id")
        case_ids.add(case["case_id"])

        normalized_question = " ".join(str(case["question"]).lower().split())
        if normalized_question in questions:
            duplicate_question_count += 1
            errors.append(f"{label}: duplicate question")
        questions.add(normalized_question)

        if case["input_hash"] != compute_input_hash(case):
            errors.append(f"{label}: input_hash mismatch")
        if case["case_hash"] != compute_case_hash(case):
            errors.append(f"{label}: case_hash mismatch")

        source_docs = case.get("source_document_refs")
        source_spans = case.get("source_span_refs")
        if not isinstance(source_docs, list) or not isinstance(source_spans, list):
            errors.append(f"{label}: source refs and spans must be lists")
            continue
        if case["question_type"] != "abstain_no_answer" and not source_docs:
            errors.append(f"{label}: answerable case must have source_document_refs")
        for doc_id in source_docs:
            if doc_id not in corpus_docs:
                errors.append(f"{label}: source document not found: {doc_id}")
        for span_ref in source_spans:
            doc_id = span_ref.get("document_id") if isinstance(span_ref, dict) else None
            text = span_ref.get("text") if isinstance(span_ref, dict) else None
            if not doc_id or not text:
                errors.append(f"{label}: malformed source_span_ref {span_ref!r}")
                continue
            body = corpus_docs.get(doc_id)
            if body is None:
                errors.append(f"{label}: span document not found: {doc_id}")
                continue
            if str(text) not in body:
                errors.append(f"{label}: source span text not found in {doc_id}: {text!r}")

        derivation = case.get("derivation_spec")
        if not isinstance(derivation, dict):
            errors.append(f"{label}: derivation_spec must be an object")
        else:
            method = derivation.get("method")
            if method not in {
                "single_doc_fact",
                "multi_hop",
                "graph_relation",
                "temporal_version",
                "abstain_scan",
                "security_scope",
                "fault_recovery",
            }:
                errors.append(f"{label}: unsupported derivation method {method!r}")
            if case["question_type"] == "multi_hop" and len(set(source_docs)) < 2:
                errors.append(f"{label}: multi_hop case must cite at least two documents")
            if case["question_type"] == "graph_reasoning":
                relations = derivation.get("relations")
                if not isinstance(relations, list) or not relations:
                    errors.append(f"{label}: graph_reasoning requires relation derivation")
                else:
                    for relation in relations:
                        for field_name in ["kind", "from", "to", "direction"]:
                            if field_name not in relation:
                                errors.append(f"{label}: relation missing {field_name}")
            if case["question_type"] == "temporal_version" and "effective_at" not in derivation:
                errors.append(f"{label}: temporal_version requires effective_at")
            if case["question_type"] == "abstain_no_answer" and source_docs:
                errors.append(f"{label}: abstain_no_answer must not include source documents")

        if case["expected_answer"] and case["expected_answer"] in case["question"]:
            gold_leakage_count += 1
            errors.append(f"{label}: expected_answer leaks into question")

    dataset_hash = sha256_json(cases)
    return DatasetValidationResult(
        passed=not errors,
        errors=errors,
        warnings=warnings,
        case_count=len(cases),
        distribution=dict(distribution),
        dataset_hash=dataset_hash,
        duplicate_case_id_count=duplicate_case_id_count,
        duplicate_question_count=duplicate_question_count,
        gold_leakage_count=gold_leakage_count,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--corpus-root", required=True, type=Path)
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()

    result = validate_cases(
        load_jsonl(args.cases),
        load_corpus(args.corpus_root),
        require_full_80=not args.allow_partial,
    )
    print(
        json.dumps(
            {
                "passed": result.passed,
                "case_count": result.case_count,
                "distribution": result.distribution,
                "dataset_hash": result.dataset_hash,
                "errors": result.errors,
                "warnings": result.warnings,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
