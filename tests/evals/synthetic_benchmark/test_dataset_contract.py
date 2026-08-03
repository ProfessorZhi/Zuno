from __future__ import annotations

from tools.evals.zuno.synthetic_benchmark.dataset_contract import (
    compute_case_hash,
    compute_input_hash,
    validate_cases,
)
from tools.evals.zuno.synthetic_benchmark.derivation_validator import validate_derivations
from tools.evals.zuno.synthetic_benchmark.release_contract import (
    REQUIRED_SYNTHETIC_METRICS,
    build_blocked_release_decision,
    build_threshold_set,
    validate_release_contract,
    write_release_contract,
)
from tools.evals.zuno.synthetic_benchmark.runtime_request_contract import (
    build_runtime_requests,
    validate_runtime_isolation,
    write_runtime_isolation_report,
)
from tools.evals.zuno.synthetic_benchmark.source_upload_manifest import (
    build_source_upload_manifest,
    validate_source_upload_manifest,
    write_source_upload_manifest,
)
from tools.evals.zuno.synthetic_benchmark.canonical_ir_manifest import (
    build_canonical_ir_manifest,
    validate_canonical_ir_manifest,
    write_canonical_ir_manifest,
)
from tools.evals.zuno.synthetic_benchmark.index_job_manifest import (
    build_index_job_manifest,
    validate_index_job_manifest,
    write_index_job_manifest,
)
from tools.evals.zuno.synthetic_benchmark.snapshot_activation_manifest import (
    build_snapshot_activation_manifest,
    validate_snapshot_activation_manifest,
    write_snapshot_activation_manifest,
)
from tools.evals.zuno.synthetic_benchmark.build_seed_dataset import (
    build_seed_cases,
    build_full_candidate_cases,
    write_seed_dataset,
    write_full_candidate_dataset,
    CORPUS_DOCS,
    WORLD_MODEL,
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
    assert result.duplicate_case_id_count == 0
    assert result.duplicate_question_count == 0
    assert result.gold_leakage_count == 0


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


def test_seed_dataset_covers_each_target_bucket_without_gold_runtime_fields() -> None:
    cases = build_seed_cases()

    result = validate_cases(cases, CORPUS_DOCS, require_full_80=False)

    assert result.passed
    assert result.distribution == {
        "single_doc_fact": 1,
        "multi_hop": 1,
        "graph_reasoning": 1,
        "temporal_version": 1,
        "abstain_no_answer": 1,
        "security_scope": 1,
        "fault_recovery": 1,
    }
    forbidden = {"gold_document_refs", "gold_source_spans", "gold_citations"}
    assert all(forbidden.isdisjoint(case) for case in cases)


def test_seed_dataset_writer_emits_partial_not_runtime_eligible_manifest(tmp_path) -> None:
    manifest = write_seed_dataset(tmp_path)

    assert manifest["status"] == "PARTIAL_SEED_VALIDATED"
    assert manifest["case_count"] == 7
    assert manifest["runtime_eligible"] is False
    assert manifest["synthetic_regression_eligible"] is False
    assert (tmp_path / "seed_cases.jsonl").exists()
    assert (tmp_path / "seed_validation_report.json").exists()


def test_full_candidate_dataset_has_required_80_case_distribution_without_runtime_eligibility(tmp_path) -> None:
    cases = build_full_candidate_cases()
    result = validate_cases(cases, CORPUS_DOCS, require_full_80=True)

    assert result.passed
    assert result.case_count == 80
    assert result.distribution == {
        "single_doc_fact": 20,
        "multi_hop": 20,
        "graph_reasoning": 15,
        "temporal_version": 10,
        "abstain_no_answer": 5,
        "security_scope": 5,
        "fault_recovery": 5,
    }

    manifest = write_full_candidate_dataset(tmp_path)
    assert manifest["status"] == "FULL_80_CANDIDATE_VALIDATED"
    assert manifest["runtime_eligible"] is False
    assert manifest["synthetic_regression_eligible"] is False
    assert (tmp_path / "synthetic_cases.jsonl").exists()
    assert (tmp_path / "candidate_validation_report.json").exists()


def test_derivation_validator_validates_candidate_without_expected_answer() -> None:
    cases = build_full_candidate_cases()
    stripped = [{k: v for k, v in case.items() if k != "expected_answer"} for case in cases]

    result = validate_derivations(stripped, CORPUS_DOCS, WORLD_MODEL)

    assert result.passed
    assert result.case_count == 80
    assert result.derivation_valid_count == 80
    assert result.source_evidence_valid_count == 80
    assert result.answer_derivation_valid_count == 80
    assert result.world_model_valid_count == 80
    assert result.unsupported_answer_count == 0


def test_derivation_validator_reports_wp1_quality_counts() -> None:
    cases = build_full_candidate_cases()

    result = validate_derivations(cases, CORPUS_DOCS, WORLD_MODEL)

    assert result.passed
    assert result.duplicate_question_count == 0
    assert result.gold_leakage_count == 0
    assert result.hard_negative_valid_count == 5
    assert result.hash_valid_count == 80
    assert result.answer_derivation_valid_count == 80
    assert result.world_model_valid_count == 80


def test_derivation_validator_rejects_unclosed_graph_relation() -> None:
    case = build_full_candidate_cases()[40]
    case["derivation_spec"] = {"method": "graph_relation", "relations": []}

    result = validate_derivations([case], CORPUS_DOCS, WORLD_MODEL)

    assert not result.passed
    assert any("graph_relation requires relations" in error for error in result.errors)


def test_derivation_validator_rejects_hard_negative_present_in_authorized_corpus() -> None:
    case = build_full_candidate_cases()[65]
    corpus = dict(CORPUS_DOCS)
    corpus["doc_fake_revenue"] = (
        "document_id: doc_fake_revenue\n"
        "security_scope: global/open\n"
        "fy2025 revenue is intentionally present for a negative test.\n"
    )

    result = validate_derivations([case], corpus, WORLD_MODEL)

    assert not result.passed
    assert any("missing_fact is present in authorized corpus" in error for error in result.errors)


def test_derivation_validator_rejects_expected_answer_drift_after_world_model_derivation() -> None:
    case = build_full_candidate_cases()[0]
    case["expected_answer"] = "A made-up answer."
    case["case_hash"] = compute_case_hash(case)

    result = validate_derivations([case], CORPUS_DOCS, WORLD_MODEL)

    assert not result.passed
    assert any("derived answer does not match expected_answer" in error for error in result.errors)


def test_synthetic_release_contract_freezes_non_zero_thresholds_before_runtime() -> None:
    thresholds = build_threshold_set()
    decision = build_blocked_release_decision(thresholds)

    result = validate_release_contract(thresholds, decision)

    assert result.passed
    assert set(thresholds["metrics"]) == set(REQUIRED_SYNTHETIC_METRICS)
    assert any(spec["threshold"] > 0 for spec in thresholds["metrics"].values())
    assert decision["status"] == "BLOCKED"
    assert decision["runtime_metrics_ref"] is None
    assert decision["public_benchmark_claim"] is False
    assert decision["production_release_claim"] is False


def test_synthetic_release_contract_rejects_all_zero_thresholds() -> None:
    thresholds = build_threshold_set()
    for spec in thresholds["metrics"].values():
        spec["threshold"] = 0
    decision = build_blocked_release_decision(thresholds)

    result = validate_release_contract(thresholds, decision)

    assert not result.passed
    assert any("must not be all zero" in error for error in result.errors)


def test_synthetic_release_contract_writer_emits_blocked_evidence(tmp_path) -> None:
    result = write_release_contract(tmp_path)

    assert result["passed"]
    assert (tmp_path / "synthetic_threshold_set.json").exists()
    assert (tmp_path / "synthetic_release_decision.json").exists()
    assert (tmp_path / "synthetic_release_contract_report.json").exists()


def test_runtime_requests_strip_gold_fields_for_all_four_profiles() -> None:
    cases = build_full_candidate_cases()
    requests = build_runtime_requests(
        cases,
        dataset_hash="dataset-hash",
        corpus_hash="corpus-hash",
    )

    result = validate_runtime_isolation(requests)

    assert result.passed
    assert result.case_count == 80
    assert result.request_count == 320
    assert result.forbidden_field_count == 0
    assert all("expected_answer" not in request for request in requests)
    assert all("source_span_refs" not in request for request in requests)
    assert {request["profile_id"] for request in requests} == {
        "standard_rag",
        "local_graphrag",
        "deep_graphrag",
        "agentic_graphrag",
    }


def test_runtime_isolation_rejects_expected_answer_leak() -> None:
    requests = build_runtime_requests(
        build_full_candidate_cases()[:1],
        dataset_hash="dataset-hash",
        corpus_hash="corpus-hash",
    )
    requests[0]["expected_answer"] = "leaked gold"

    result = validate_runtime_isolation(requests)

    assert not result.passed
    assert result.forbidden_field_count == 1
    assert any("forbidden gold fields" in error for error in result.errors)


def test_runtime_isolation_writer_emits_manifest_and_report(tmp_path) -> None:
    dataset_root = tmp_path / "dataset"
    write_full_candidate_dataset(dataset_root)

    result = write_runtime_isolation_report(
        tmp_path,
        cases_path=dataset_root / "synthetic_cases.jsonl",
        dataset_hash="dataset-hash",
        corpus_hash="corpus-hash",
    )

    assert result["passed"]
    assert result["case_count"] == 80
    assert result["request_count"] == 320
    assert (tmp_path / "runtime_request_manifest.json").exists()
    assert (tmp_path / "runtime_gold_isolation_report.json").exists()


def test_source_upload_manifest_prepares_all_corpus_sources_without_claiming_ingestion(tmp_path) -> None:
    dataset_root = tmp_path / "dataset"
    write_full_candidate_dataset(dataset_root)

    manifest = build_source_upload_manifest(dataset_root / "corpus")
    result = validate_source_upload_manifest(manifest)

    assert result.passed
    assert manifest["source_count"] == 8
    assert manifest["runtime_ingested"] is False
    assert manifest["object_store_verified"] is False
    assert manifest["postgres_facts_verified"] is False
    assert all(source["initial_state"] == "accepted" for source in manifest["sources"])
    assert all(source["idempotency_key"].startswith("phase22-source-upload::") for source in manifest["sources"])


def test_source_upload_manifest_rejects_preclaimed_runtime_ingestion(tmp_path) -> None:
    dataset_root = tmp_path / "dataset"
    write_full_candidate_dataset(dataset_root)
    manifest = build_source_upload_manifest(dataset_root / "corpus")
    manifest["runtime_ingested"] = True

    result = validate_source_upload_manifest(manifest)

    assert not result.passed
    assert any("runtime_ingested must remain false" in error for error in result.errors)


def test_source_upload_manifest_writer_emits_evidence(tmp_path) -> None:
    dataset_root = tmp_path / "dataset"
    write_full_candidate_dataset(dataset_root)

    result = write_source_upload_manifest(tmp_path, corpus_root=dataset_root / "corpus")

    assert result["passed"]
    assert result["source_count"] == 8
    assert (tmp_path / "source_upload_manifest.json").exists()
    assert (tmp_path / "source_upload_manifest_report.json").exists()


def test_canonical_ir_manifest_prepares_documents_chunks_entities_and_relations(tmp_path) -> None:
    dataset_root = tmp_path / "dataset"
    write_full_candidate_dataset(dataset_root)

    manifest = build_canonical_ir_manifest(dataset_root / "corpus")
    result = validate_canonical_ir_manifest(manifest)

    assert result.passed
    assert result.document_count == 8
    assert result.chunk_count >= 8
    assert result.entity_count > 0
    assert result.relation_count > 0
    assert manifest["parser_runtime_executed"] is False
    assert manifest["postgres_facts_verified"] is False
    assert manifest["knowledge_version_created"] is False
    assert all(relation["direction"] == "outbound" for relation in manifest["relations"])


def test_canonical_ir_manifest_rejects_preclaimed_parser_runtime(tmp_path) -> None:
    dataset_root = tmp_path / "dataset"
    write_full_candidate_dataset(dataset_root)
    manifest = build_canonical_ir_manifest(dataset_root / "corpus")
    manifest["parser_runtime_executed"] = True

    result = validate_canonical_ir_manifest(manifest)

    assert not result.passed
    assert any("parser_runtime_executed must remain false" in error for error in result.errors)


def test_canonical_ir_manifest_writer_emits_evidence(tmp_path) -> None:
    dataset_root = tmp_path / "dataset"
    write_full_candidate_dataset(dataset_root)

    result = write_canonical_ir_manifest(tmp_path, corpus_root=dataset_root / "corpus")

    assert result["passed"]
    assert result["document_count"] == 8
    assert (tmp_path / "canonical_ir_manifest.json").exists()
    assert (tmp_path / "canonical_ir_manifest_report.json").exists()


def test_index_job_manifest_prepares_three_indexes_without_visibility(tmp_path) -> None:
    dataset_root = tmp_path / "dataset"
    write_full_candidate_dataset(dataset_root)
    canonical_ir = build_canonical_ir_manifest(dataset_root / "corpus")

    manifest = build_index_job_manifest(canonical_ir)
    result = validate_index_job_manifest(manifest)

    assert result.passed
    assert result.index_job_count == 3
    assert result.elasticsearch_job_count == 1
    assert result.milvus_job_count == 1
    assert result.neo4j_job_count == 1
    assert manifest["indexes_visible"] is False
    assert manifest["visibility_receipt_refs"] == []
    assert manifest["snapshot_activation_allowed"] is False


def test_index_job_manifest_rejects_preclaimed_snapshot_activation(tmp_path) -> None:
    dataset_root = tmp_path / "dataset"
    write_full_candidate_dataset(dataset_root)
    manifest = build_index_job_manifest(build_canonical_ir_manifest(dataset_root / "corpus"))
    manifest["snapshot_activation_allowed"] = True

    result = validate_index_job_manifest(manifest)

    assert not result.passed
    assert any("snapshot_activation_allowed must remain false" in error for error in result.errors)


def test_index_job_manifest_writer_emits_evidence(tmp_path) -> None:
    dataset_root = tmp_path / "dataset"
    write_full_candidate_dataset(dataset_root)
    write_canonical_ir_manifest(tmp_path, corpus_root=dataset_root / "corpus")

    result = write_index_job_manifest(
        tmp_path,
        canonical_ir_manifest_path=tmp_path / "canonical_ir_manifest.json",
    )

    assert result["passed"]
    assert result["index_job_count"] == 3
    assert (tmp_path / "index_job_manifest.json").exists()
    assert (tmp_path / "index_job_manifest_report.json").exists()


def test_snapshot_activation_manifest_blocks_without_visibility_receipts(tmp_path) -> None:
    dataset_root = tmp_path / "dataset"
    write_full_candidate_dataset(dataset_root)
    index_manifest = build_index_job_manifest(build_canonical_ir_manifest(dataset_root / "corpus"))

    manifest = build_snapshot_activation_manifest(index_manifest)
    result = validate_snapshot_activation_manifest(manifest)

    assert result.passed
    assert result.required_receipt_count == 3
    assert result.provided_receipt_count == 0
    assert result.missing_receipt_count == 3
    assert result.activation_allowed is False
    assert manifest["status"] == "snapshot_activation_blocked"
    assert manifest["snapshot_id"] is None


def test_snapshot_activation_manifest_rejects_snapshot_id_when_blocked(tmp_path) -> None:
    dataset_root = tmp_path / "dataset"
    write_full_candidate_dataset(dataset_root)
    manifest = build_snapshot_activation_manifest(
        build_index_job_manifest(build_canonical_ir_manifest(dataset_root / "corpus"))
    )
    manifest["snapshot_id"] = "snapshot-forged"

    result = validate_snapshot_activation_manifest(manifest)

    assert not result.passed
    assert any("snapshot_id must be null" in error for error in result.errors)


def test_snapshot_activation_manifest_writer_emits_blocked_evidence(tmp_path) -> None:
    dataset_root = tmp_path / "dataset"
    write_full_candidate_dataset(dataset_root)
    write_canonical_ir_manifest(tmp_path, corpus_root=dataset_root / "corpus")
    write_index_job_manifest(tmp_path, canonical_ir_manifest_path=tmp_path / "canonical_ir_manifest.json")

    result = write_snapshot_activation_manifest(
        tmp_path,
        index_job_manifest_path=tmp_path / "index_job_manifest.json",
    )

    assert result["passed"]
    assert result["activation_allowed"] is False
    assert (tmp_path / "snapshot_activation_manifest.json").exists()
    assert (tmp_path / "snapshot_activation_manifest_report.json").exists()
