from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.evals.zuno.synthetic_benchmark.dataset_contract import (
    load_corpus,
    load_jsonl,
    sha256_json,
)


@dataclass
class DerivationValidationResult:
    passed: bool
    case_count: int
    derivation_valid_count: int
    source_evidence_valid_count: int
    unsupported_answer_count: int
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    method_counts: dict[str, int] = field(default_factory=dict)
    report_hash: str | None = None


def _span_texts(case: dict[str, Any], corpus_docs: dict[str, str]) -> list[str]:
    texts: list[str] = []
    for span in case.get("source_span_refs", []):
        if not isinstance(span, dict):
            continue
        doc_id = span.get("document_id")
        text = span.get("text")
        if doc_id in corpus_docs and isinstance(text, str) and text in corpus_docs[doc_id]:
            texts.append(text)
    return texts


def _validate_case(case: dict[str, Any], corpus_docs: dict[str, str]) -> tuple[bool, bool, list[str]]:
    errors: list[str] = []
    derivation = case.get("derivation_spec")
    if not isinstance(derivation, dict):
        return False, False, ["derivation_spec must be an object"]

    method = derivation.get("method")
    source_docs = case.get("source_document_refs", [])
    source_spans = case.get("source_span_refs", [])
    span_texts = _span_texts(case, corpus_docs)
    source_evidence_valid = len(span_texts) == len(source_spans)

    if method == "single_doc_fact":
        if len(source_docs) != 1:
            errors.append("single_doc_fact requires exactly one source document")
        if not span_texts:
            errors.append("single_doc_fact requires at least one supported source span")
        if not derivation.get("fact"):
            errors.append("single_doc_fact requires fact")
    elif method == "multi_hop":
        if len(set(source_docs)) < 2:
            errors.append("multi_hop requires at least two source documents")
        steps = derivation.get("steps")
        if not isinstance(steps, list) or len(steps) < 2:
            errors.append("multi_hop requires at least two derivation steps")
        if not span_texts:
            errors.append("multi_hop requires supported source spans")
    elif method == "graph_relation":
        relations = derivation.get("relations")
        if not isinstance(relations, list) or not relations:
            errors.append("graph_relation requires relations")
        else:
            for relation in relations:
                if not isinstance(relation, dict):
                    errors.append("graph relation must be an object")
                    continue
                for field_name in ["kind", "from", "to", "direction"]:
                    if not relation.get(field_name):
                        errors.append(f"graph relation missing {field_name}")
                if relation.get("direction") not in {"outbound", "inbound"}:
                    errors.append("graph relation direction must be outbound or inbound")
        if not span_texts:
            errors.append("graph_relation requires source span support")
    elif method == "temporal_version":
        if not derivation.get("effective_at"):
            errors.append("temporal_version requires effective_at")
        if not derivation.get("supersedes"):
            errors.append("temporal_version requires supersedes")
        if len(set(source_docs)) < 2:
            errors.append("temporal_version requires current and superseded sources")
        if not span_texts:
            errors.append("temporal_version requires source span support")
    elif method == "abstain_scan":
        if source_docs or source_spans:
            errors.append("abstain_scan must not include positive source evidence")
        if not derivation.get("missing_fact"):
            errors.append("abstain_scan requires missing_fact")
        if not derivation.get("authorized_corpus_scope"):
            errors.append("abstain_scan requires authorized_corpus_scope")
    elif method == "security_scope":
        required_scope = derivation.get("required_scope")
        caller_scope = derivation.get("caller_scope")
        if not required_scope or not caller_scope:
            errors.append("security_scope requires required_scope and caller_scope")
        if required_scope == caller_scope:
            errors.append("security_scope deny case requires caller_scope to differ")
        if not span_texts:
            errors.append("security_scope requires source span support")
    elif method == "fault_recovery":
        if not derivation.get("trigger"):
            errors.append("fault_recovery requires trigger")
        if not derivation.get("required_state"):
            errors.append("fault_recovery requires required_state")
        if not span_texts:
            errors.append("fault_recovery requires source span support")
    else:
        errors.append(f"unsupported derivation method {method!r}")

    if not source_evidence_valid:
        errors.append("source evidence does not match corpus")
    return not errors, source_evidence_valid, errors


def validate_derivations(
    cases: list[dict[str, Any]],
    corpus_docs: dict[str, str],
) -> DerivationValidationResult:
    errors: list[str] = []
    derivation_valid = 0
    source_valid = 0
    method_counts = Counter()
    unsupported_answer_count = 0

    for case in cases:
        case_id = case.get("case_id", "<unknown>")
        method = (case.get("derivation_spec") or {}).get("method", "<missing>")
        method_counts[method] += 1
        passed, source_evidence_valid, case_errors = _validate_case(case, corpus_docs)
        if passed:
            derivation_valid += 1
        if source_evidence_valid:
            source_valid += 1
        if case_errors:
            unsupported_answer_count += 1
            errors.extend(f"{case_id}: {error}" for error in case_errors)

    payload = {
        "case_count": len(cases),
        "derivation_valid_count": derivation_valid,
        "source_evidence_valid_count": source_valid,
        "unsupported_answer_count": unsupported_answer_count,
        "method_counts": dict(method_counts),
        "errors": errors,
    }
    return DerivationValidationResult(
        passed=not errors,
        case_count=len(cases),
        derivation_valid_count=derivation_valid,
        source_evidence_valid_count=source_valid,
        unsupported_answer_count=unsupported_answer_count,
        errors=errors,
        method_counts=dict(method_counts),
        report_hash=sha256_json(payload),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--corpus-root", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()

    result = validate_derivations(load_jsonl(args.cases), load_corpus(args.corpus_root))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(result.__dict__, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result.__dict__, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
