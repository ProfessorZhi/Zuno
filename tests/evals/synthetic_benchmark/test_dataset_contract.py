from __future__ import annotations

from tools.evals.zuno.synthetic_benchmark.dataset_contract import (
    compute_case_hash,
    compute_input_hash,
    validate_cases,
)


def _case(**overrides):
    case = {
        "case_id": "syn_contract_001",
        "question": "Who owns the Axis-9 release note?",
        "question_type": "single_doc_fact",
        "expected_answer": "Haruto Soma",
        "derivation_spec": {
            "method": "single_doc_fact",
            "source": "doc_axis9_release_notes",
            "fact": "owner_employee",
        },
        "source_document_refs": ["doc_axis9_release_notes"],
        "source_span_refs": [
            {"document_id": "doc_axis9_release_notes", "text": "Haruto Soma"}
        ],
        "security_principal": {
            "principal_id": "principal_global_reader",
            "roles": ["global_reader"],
        },
        "tenant_id": "tenant_auroralis",
        "workspace_id": "workspace_regression",
        "security_epoch_ref": "sec_epoch_synthetic_v1",
        "expected_behavior": "answer_with_citation",
        "failure_expectation": "none",
        "generation_seed": "seed-v1",
    }
    case.update(overrides)
    case["input_hash"] = compute_input_hash(case)
    case["case_hash"] = compute_case_hash(case)
    return case


def test_dataset_contract_accepts_runtime_isolated_case_schema() -> None:
    corpus = {"doc_axis9_release_notes": "Axis-9 was signed off by Haruto Soma."}
    result = validate_cases([_case()], corpus, require_full_80=False)

    assert result.passed
    assert result.case_count == 1
    assert result.distribution == {"single_doc_fact": 1}


def test_dataset_contract_rejects_pr100_gold_runtime_fields() -> None:
    corpus = {"doc_axis9_release_notes": "Axis-9 was signed off by Haruto Soma."}
    case = _case(gold_document_refs=["doc_axis9_release_notes"])

    result = validate_cases([case], corpus, require_full_80=False)

    assert not result.passed
    assert any("runtime-forbidden gold fields" in error for error in result.errors)


def test_dataset_contract_rejects_hash_drift_and_missing_span() -> None:
    corpus = {"doc_axis9_release_notes": "Axis-9 was signed off by Haruto Soma."}
    case = _case(
        source_span_refs=[
            {"document_id": "doc_axis9_release_notes", "text": "Marcus Tien"}
        ]
    )
    case["case_hash"] = "0" * 64

    result = validate_cases([case], corpus, require_full_80=False)

    assert not result.passed
    assert any("case_hash mismatch" in error for error in result.errors)
    assert any("source span text not found" in error for error in result.errors)
