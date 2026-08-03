from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.evals.zuno.synthetic_benchmark.dataset_contract import (
    GOLD_RUNTIME_FORBIDDEN_FIELDS,
    compute_case_hash,
    compute_input_hash,
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
    duplicate_question_count: int = 0
    gold_leakage_count: int = 0
    hard_negative_valid_count: int = 0
    hash_valid_count: int = 0
    answer_derivation_valid_count: int = 0
    world_model_valid_count: int = 0
    world_model_hash: str | None = None
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


def _doc_security_scope(body: str) -> str | None:
    for line in body.splitlines():
        if line.startswith("security_scope:"):
            return line.split(":", 1)[1].strip()
    return None


def _authorized_corpus_text(corpus_docs: dict[str, str], scopes: list[str]) -> str:
    allowed = set(scopes)
    bodies = [
        body
        for body in corpus_docs.values()
        if (scope := _doc_security_scope(body)) is not None and scope in allowed
    ]
    return "\n".join(bodies).lower()


def _gold_leakage_errors(case: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    forbidden = sorted(GOLD_RUNTIME_FORBIDDEN_FIELDS & set(case))
    if forbidden:
        errors.append(f"contains runtime-forbidden gold fields {forbidden}")
    expected_answer = case.get("expected_answer")
    question = case.get("question")
    if isinstance(expected_answer, str) and expected_answer and isinstance(question, str):
        if expected_answer.lower() in question.lower():
            errors.append("expected_answer leaks into question")
    return errors


def _multi_hop_key(steps: list[dict[str, Any]]) -> str:
    return "+".join(f"{step.get('source')}|{step.get('fact')}" for step in steps)


def _derive_answer(derivation: dict[str, Any], world_model: dict[str, Any]) -> str | None:
    method = derivation.get("method")
    if method == "single_doc_fact":
        fact = world_model.get("facts", {}).get(derivation.get("fact"), {})
        if fact.get("source") == derivation.get("source"):
            return fact.get("answer")
    if method == "multi_hop":
        steps = derivation.get("steps", [])
        if isinstance(steps, list):
            return world_model.get("multi_hop_answers", {}).get(_multi_hop_key(steps))
    if method == "graph_relation":
        expected_relations = derivation.get("relations", [])
        for relation in world_model.get("relations", []):
            projection = {
                "kind": relation.get("kind"),
                "from": relation.get("from"),
                "to": relation.get("to"),
                "direction": relation.get("direction"),
            }
            if projection in expected_relations:
                return relation.get("answer")
    if method == "temporal_version":
        key = f"{derivation.get('effective_at')}|{derivation.get('supersedes')}"
        return world_model.get("temporal_versions", {}).get(key)
    if method == "abstain_scan":
        missing = world_model.get("absent_facts", {}).get(derivation.get("missing_fact"), {})
        if missing.get("authorized_corpus_scope") == derivation.get("authorized_corpus_scope"):
            return missing.get("answer")
    if method == "security_scope":
        key = f"{derivation.get('required_scope')}|{derivation.get('caller_scope')}"
        return world_model.get("security_rules", {}).get(key)
    if method == "fault_recovery":
        key = f"{derivation.get('trigger')}|{derivation.get('required_state')}"
        return world_model.get("fault_rules", {}).get(key)
    return None


def _same_answer(left: str, right: str) -> bool:
    return " ".join(left.lower().split()).rstrip(".") == " ".join(right.lower().split()).rstrip(".")


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
        missing_fact = derivation.get("missing_fact")
        if not missing_fact:
            errors.append("abstain_scan requires missing_fact")
        authorized_scope = derivation.get("authorized_corpus_scope")
        if not authorized_scope:
            errors.append("abstain_scan requires authorized_corpus_scope")
        elif isinstance(authorized_scope, list) and isinstance(missing_fact, str):
            authorized_text = _authorized_corpus_text(corpus_docs, authorized_scope)
            if missing_fact.replace("_", " ").lower() in authorized_text:
                errors.append("abstain_scan missing_fact is present in authorized corpus")
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
    world_model: dict[str, Any] | None = None,
) -> DerivationValidationResult:
    errors: list[str] = []
    derivation_valid = 0
    source_valid = 0
    method_counts = Counter()
    unsupported_answer_count = 0
    duplicate_question_count = 0
    gold_leakage_count = 0
    hard_negative_valid_count = 0
    hash_valid_count = 0
    answer_derivation_valid_count = 0
    world_model_valid_count = 0
    questions: set[str] = set()
    model = world_model or {}
    world_model_hash = sha256_json(model) if model else None

    for case in cases:
        case_id = case.get("case_id", "<unknown>")
        method = (case.get("derivation_spec") or {}).get("method", "<missing>")
        method_counts[method] += 1
        normalized_question = " ".join(str(case.get("question", "")).lower().split())
        if normalized_question in questions:
            duplicate_question_count += 1
            errors.append(f"{case_id}: duplicate question")
        questions.add(normalized_question)

        leakage_errors = _gold_leakage_errors(case)
        if leakage_errors:
            gold_leakage_count += 1
            errors.extend(f"{case_id}: {error}" for error in leakage_errors)

        if "input_hash" in case and "case_hash" in case and "expected_answer" in case:
            if (
                case.get("input_hash") == compute_input_hash(case)
                and case.get("case_hash") == compute_case_hash(case)
            ):
                hash_valid_count += 1
            else:
                errors.append(f"{case_id}: input_hash or case_hash mismatch")

        passed, source_evidence_valid, case_errors = _validate_case(case, corpus_docs)
        derived_answer = _derive_answer(case.get("derivation_spec") or {}, model) if model else None
        if derived_answer is not None:
            world_model_valid_count += 1
            expected_answer = case.get("expected_answer")
            if expected_answer is None or (
                isinstance(expected_answer, str) and _same_answer(derived_answer, expected_answer)
            ):
                answer_derivation_valid_count += 1
            else:
                errors.append(f"{case_id}: derived answer does not match expected_answer")
        elif model:
            errors.append(f"{case_id}: world model could not derive answer")

        if passed:
            derivation_valid += 1
        if source_evidence_valid:
            source_valid += 1
        if passed and method == "abstain_scan":
            hard_negative_valid_count += 1
        if case_errors:
            unsupported_answer_count += 1
            errors.extend(f"{case_id}: {error}" for error in case_errors)

    payload = {
        "case_count": len(cases),
        "derivation_valid_count": derivation_valid,
        "source_evidence_valid_count": source_valid,
        "unsupported_answer_count": unsupported_answer_count,
        "duplicate_question_count": duplicate_question_count,
        "gold_leakage_count": gold_leakage_count,
        "hard_negative_valid_count": hard_negative_valid_count,
        "hash_valid_count": hash_valid_count,
        "answer_derivation_valid_count": answer_derivation_valid_count,
        "world_model_valid_count": world_model_valid_count,
        "world_model_hash": world_model_hash,
        "method_counts": dict(method_counts),
        "errors": errors,
    }
    return DerivationValidationResult(
        passed=not errors,
        case_count=len(cases),
        derivation_valid_count=derivation_valid,
        source_evidence_valid_count=source_valid,
        unsupported_answer_count=unsupported_answer_count,
        duplicate_question_count=duplicate_question_count,
        gold_leakage_count=gold_leakage_count,
        hard_negative_valid_count=hard_negative_valid_count,
        hash_valid_count=hash_valid_count,
        answer_derivation_valid_count=answer_derivation_valid_count,
        world_model_valid_count=world_model_valid_count,
        world_model_hash=world_model_hash,
        errors=errors,
        method_counts=dict(method_counts),
        report_hash=sha256_json(payload),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--corpus-root", required=True, type=Path)
    parser.add_argument("--world-model", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()

    world_model = json.loads(args.world_model.read_text(encoding="utf-8"))
    result = validate_derivations(load_jsonl(args.cases), load_corpus(args.corpus_root), world_model)
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
