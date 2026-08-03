from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]

TRACK_DIR = Path(
    "docs/evidence/goal05-phase22-machine-attested-synthetic-regression"
)
TRACK_MANIFEST = TRACK_DIR / "track_manifest.json"
READINESS_REPORT = TRACK_DIR / "readiness-report.md"
PR100_FILE_CLASSIFICATION = TRACK_DIR / "pr100-file-classification.json"
SEED_DATASET_MANIFEST = TRACK_DIR / "seed-dataset" / "seed_dataset_manifest.json"
SEED_WORLD_MODEL = TRACK_DIR / "seed-dataset" / "world_model.json"
CANDIDATE_DATASET_MANIFEST = TRACK_DIR / "candidate-dataset" / "candidate_dataset_manifest.json"
CANDIDATE_DERIVATION_REPORT = TRACK_DIR / "candidate-dataset" / "candidate_derivation_report.json"
CANDIDATE_WORLD_MODEL = TRACK_DIR / "candidate-dataset" / "world_model.json"
SYNTHETIC_THRESHOLD_SET = TRACK_DIR / "synthetic_threshold_set.json"
SYNTHETIC_RELEASE_DECISION = TRACK_DIR / "synthetic_release_decision.json"
SYNTHETIC_RELEASE_CONTRACT_REPORT = TRACK_DIR / "synthetic_release_contract_report.json"
RUNTIME_REQUEST_MANIFEST = TRACK_DIR / "runtime_request_manifest.json"
RUNTIME_GOLD_ISOLATION_REPORT = TRACK_DIR / "runtime_gold_isolation_report.json"
SOURCE_UPLOAD_MANIFEST = TRACK_DIR / "source_upload_manifest.json"
SOURCE_UPLOAD_MANIFEST_REPORT = TRACK_DIR / "source_upload_manifest_report.json"
CANONICAL_IR_MANIFEST = TRACK_DIR / "canonical_ir_manifest.json"
CANONICAL_IR_MANIFEST_REPORT = TRACK_DIR / "canonical_ir_manifest_report.json"
INDEX_JOB_MANIFEST = TRACK_DIR / "index_job_manifest.json"
INDEX_JOB_MANIFEST_REPORT = TRACK_DIR / "index_job_manifest_report.json"
SNAPSHOT_ACTIVATION_MANIFEST = TRACK_DIR / "snapshot_activation_manifest.json"
SNAPSHOT_ACTIVATION_MANIFEST_REPORT = TRACK_DIR / "snapshot_activation_manifest_report.json"
PUBLIC_APPROVAL_SUMMARY = Path(
    "docs/evidence/goal05-phase22-public-benchmark-review-pack/approval_summary.json"
)
PUBLIC_INTEGRITY_REPORT = Path(
    "docs/evidence/goal05-phase22-public-benchmark-review-pack/integrity_report.json"
)
INVALIDATION_NOTICE = Path(
    "docs/evidence/goal05-phase22-synthetic-benchmark/INVALIDATION_NOTICE.md"
)
TASK_CARDS = [
    Path(".agent/programs/thread-prompts/CC-A-phase22-dataset-corpus-derivation-validator.md"),
    Path(".agent/programs/thread-prompts/CC-B-phase22-canonical-ingestion-three-indexes.md"),
    Path(".agent/programs/thread-prompts/CC-C-phase22-four-profile-runtime-benchmark.md"),
    Path(".agent/programs/thread-prompts/CC-D-phase22-integration-fault-security-evidence.md"),
]


def _read_text(path: Path) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(_read_text(path))


def verify_phase22_synthetic_regression_track() -> list[str]:
    errors: list[str] = []
    required_files = [
        TRACK_MANIFEST,
        READINESS_REPORT,
        PR100_FILE_CLASSIFICATION,
        SEED_DATASET_MANIFEST,
        SEED_WORLD_MODEL,
        CANDIDATE_DATASET_MANIFEST,
        CANDIDATE_DERIVATION_REPORT,
        CANDIDATE_WORLD_MODEL,
        SYNTHETIC_THRESHOLD_SET,
        SYNTHETIC_RELEASE_DECISION,
        SYNTHETIC_RELEASE_CONTRACT_REPORT,
        RUNTIME_REQUEST_MANIFEST,
        RUNTIME_GOLD_ISOLATION_REPORT,
        SOURCE_UPLOAD_MANIFEST,
        SOURCE_UPLOAD_MANIFEST_REPORT,
        CANONICAL_IR_MANIFEST,
        CANONICAL_IR_MANIFEST_REPORT,
        INDEX_JOB_MANIFEST,
        INDEX_JOB_MANIFEST_REPORT,
        SNAPSHOT_ACTIVATION_MANIFEST,
        SNAPSHOT_ACTIVATION_MANIFEST_REPORT,
        PUBLIC_APPROVAL_SUMMARY,
        PUBLIC_INTEGRITY_REPORT,
        INVALIDATION_NOTICE,
        *TASK_CARDS,
    ]
    for path in required_files:
        if not (REPO_ROOT / path).exists():
            errors.append(f"missing required synthetic regression track file: {path.as_posix()}")
    if errors:
        return errors

    manifest = _read_json(TRACK_MANIFEST)
    pr100_classification = _read_json(PR100_FILE_CLASSIFICATION)
    seed_manifest = _read_json(SEED_DATASET_MANIFEST)
    candidate_manifest = _read_json(CANDIDATE_DATASET_MANIFEST)
    derivation_report = _read_json(CANDIDATE_DERIVATION_REPORT)
    seed_world_model = _read_json(SEED_WORLD_MODEL)
    candidate_world_model = _read_json(CANDIDATE_WORLD_MODEL)
    threshold_set = _read_json(SYNTHETIC_THRESHOLD_SET)
    release_decision = _read_json(SYNTHETIC_RELEASE_DECISION)
    release_contract_report = _read_json(SYNTHETIC_RELEASE_CONTRACT_REPORT)
    runtime_request_manifest = _read_json(RUNTIME_REQUEST_MANIFEST)
    runtime_gold_isolation = _read_json(RUNTIME_GOLD_ISOLATION_REPORT)
    source_upload_manifest = _read_json(SOURCE_UPLOAD_MANIFEST)
    source_upload_report = _read_json(SOURCE_UPLOAD_MANIFEST_REPORT)
    canonical_ir_manifest = _read_json(CANONICAL_IR_MANIFEST)
    canonical_ir_report = _read_json(CANONICAL_IR_MANIFEST_REPORT)
    index_job_manifest = _read_json(INDEX_JOB_MANIFEST)
    index_job_report = _read_json(INDEX_JOB_MANIFEST_REPORT)
    snapshot_activation_manifest = _read_json(SNAPSHOT_ACTIVATION_MANIFEST)
    snapshot_activation_report = _read_json(SNAPSHOT_ACTIVATION_MANIFEST_REPORT)
    approval = _read_json(PUBLIC_APPROVAL_SUMMARY)
    integrity = _read_json(PUBLIC_INTEGRITY_REPORT)
    report = _read_text(READINESS_REPORT)
    invalidation = _read_text(INVALIDATION_NOTICE)

    if manifest.get("track_id") != "machine_attested_synthetic_regression":
        errors.append("track_manifest track_id must be machine_attested_synthetic_regression")
    if manifest.get("status") != "BLOCKED_WITH_EXACT_GAPS":
        errors.append("track_manifest must remain BLOCKED_WITH_EXACT_GAPS until full runtime evidence exists")
    decision = manifest.get("synthetic_release_decision", {})
    current_evidence = manifest.get("current_evidence", {})
    if decision.get("scope") != "machine_attested_synthetic_regression":
        errors.append("synthetic release decision must be scoped to machine_attested_synthetic_regression")
    if decision.get("status") != "BLOCKED":
        errors.append("synthetic release decision must remain BLOCKED before runtime execution")

    boundary = manifest.get("synthetic_public_boundary", {})
    for field in ["reviewer_approved_count", "benchmark_eligible_count"]:
        if approval.get(field) != 0 or integrity.get(field) != 0 or boundary.get(field) != 0:
            errors.append(f"public benchmark {field} must remain 0 for synthetic track")
    for field in ["machine_attested_count", "synthetic_regression_eligible_count"]:
        if field not in boundary:
            errors.append(f"synthetic boundary missing independent field: {field}")
    if boundary.get("machine_attested_count") != candidate_manifest.get("case_count"):
        errors.append("machine_attested_count must match candidate dataset case_count")
    if boundary.get("synthetic_regression_eligible_count") != 0:
        errors.append("synthetic_regression_eligible_count must remain 0 until full 80 is valid")
    if seed_manifest.get("status") != "PARTIAL_SEED_VALIDATED":
        errors.append("seed dataset manifest must be PARTIAL_SEED_VALIDATED")
    if seed_manifest.get("runtime_eligible") is not False:
        errors.append("seed dataset must not be runtime eligible")
    if seed_manifest.get("synthetic_regression_eligible") is not False:
        errors.append("seed dataset must not be synthetic regression eligible")
    if seed_manifest.get("world_model_hash") != candidate_manifest.get("world_model_hash"):
        errors.append("seed and candidate world_model_hash must match")
    if candidate_manifest.get("status") != "FULL_80_CANDIDATE_VALIDATED":
        errors.append("candidate dataset manifest must be FULL_80_CANDIDATE_VALIDATED")
    if candidate_manifest.get("case_count") != 80:
        errors.append("candidate dataset case_count must be 80")
    if candidate_manifest.get("runtime_eligible") is not False:
        errors.append("candidate dataset must not be runtime eligible before ingestion")
    if candidate_manifest.get("synthetic_regression_eligible") is not False:
        errors.append("candidate dataset must not be synthetic regression eligible before runtime")
    if derivation_report.get("case_count") != 80:
        errors.append("candidate derivation report case_count must be 80")
    if derivation_report.get("derivation_valid_count") != 80:
        errors.append("candidate derivation report derivation_valid_count must be 80")
    if derivation_report.get("source_evidence_valid_count") != 80:
        errors.append("candidate derivation report source_evidence_valid_count must be 80")
    if derivation_report.get("unsupported_answer_count") != 0:
        errors.append("candidate derivation report unsupported_answer_count must be 0")
    if derivation_report.get("duplicate_question_count") != 0:
        errors.append("candidate derivation report duplicate_question_count must be 0")
    if derivation_report.get("gold_leakage_count") != 0:
        errors.append("candidate derivation report gold_leakage_count must be 0")
    if derivation_report.get("hard_negative_valid_count") != 5:
        errors.append("candidate derivation report hard_negative_valid_count must be 5")
    if derivation_report.get("hash_valid_count") != 80:
        errors.append("candidate derivation report hash_valid_count must be 80")
    if derivation_report.get("answer_derivation_valid_count") != 80:
        errors.append("candidate derivation report answer_derivation_valid_count must be 80")
    if derivation_report.get("world_model_valid_count") != 80:
        errors.append("candidate derivation report world_model_valid_count must be 80")
    if derivation_report.get("world_model_hash") != candidate_manifest.get("world_model_hash"):
        errors.append("candidate derivation report world_model_hash must match dataset manifest")
    if seed_world_model != candidate_world_model:
        errors.append("seed and candidate world_model.json must match")
    if threshold_set.get("track_id") != "machine_attested_synthetic_regression":
        errors.append("synthetic threshold set track_id mismatch")
    if threshold_set.get("status") != "FROZEN_BEFORE_RUNTIME":
        errors.append("synthetic threshold set must be FROZEN_BEFORE_RUNTIME")
    threshold_metrics = threshold_set.get("metrics", {})
    required_threshold_metrics = {
        "answer_exact_match",
        "answer_semantic_score",
        "recall_at_5",
        "context_precision_at_5",
        "hit_at_5",
        "citation_accuracy",
        "citation_completeness",
        "abstention_accuracy",
        "security_violation_rate",
        "unsupported_claim_rate",
        "profile_failure_rate",
        "resume_success_rate",
        "p50_latency",
        "p95_latency",
        "cost_per_case",
        "budget_overrun_rate",
    }
    if set(threshold_metrics) != required_threshold_metrics:
        errors.append("synthetic threshold set must contain the required metric set")
    numeric_thresholds = [
        spec.get("threshold")
        for spec in threshold_metrics.values()
        if isinstance(spec, dict) and isinstance(spec.get("threshold"), (int, float))
    ]
    if not numeric_thresholds or all(value == 0 for value in numeric_thresholds):
        errors.append("synthetic threshold set must not be all zero")
    if release_decision.get("status") != "BLOCKED":
        errors.append("synthetic release decision must remain BLOCKED before runtime metrics")
    if release_decision.get("scope") != "machine_attested_synthetic_regression":
        errors.append("synthetic release decision scope mismatch")
    if release_decision.get("threshold_hash") != threshold_set.get("threshold_hash"):
        errors.append("synthetic release decision threshold_hash mismatch")
    if release_decision.get("runtime_metrics_ref") is not None:
        errors.append("synthetic release decision must not reference runtime metrics before execution")
    if release_decision.get("public_benchmark_claim") is not False:
        errors.append("synthetic release decision must not claim public benchmark")
    if release_decision.get("production_release_claim") is not False:
        errors.append("synthetic release decision must not claim production release")
    if release_contract_report.get("passed") is not True:
        errors.append("synthetic release contract report must pass")
    if release_contract_report.get("threshold_hash") != threshold_set.get("threshold_hash"):
        errors.append("synthetic release contract report threshold_hash mismatch")
    if release_contract_report.get("decision_hash") != release_decision.get("decision_hash"):
        errors.append("synthetic release contract report decision_hash mismatch")
    if decision.get("threshold_hash") != threshold_set.get("threshold_hash"):
        errors.append("track_manifest synthetic_release_decision threshold_hash mismatch")
    if decision.get("decision_hash") != release_decision.get("decision_hash"):
        errors.append("track_manifest synthetic_release_decision decision_hash mismatch")
    if current_evidence.get("synthetic_threshold_hash") != threshold_set.get("threshold_hash"):
        errors.append("track_manifest current_evidence synthetic_threshold_hash mismatch")
    if current_evidence.get("synthetic_blocked_release_decision_hash") != release_decision.get("decision_hash"):
        errors.append("track_manifest current_evidence synthetic_blocked_release_decision_hash mismatch")
    if runtime_request_manifest.get("status") != "RUNTIME_INPUT_GOLD_ISOLATED":
        errors.append("runtime request manifest must be RUNTIME_INPUT_GOLD_ISOLATED")
    if runtime_request_manifest.get("case_count") != 80:
        errors.append("runtime request manifest case_count must be 80")
    if runtime_request_manifest.get("request_count") != 320:
        errors.append("runtime request manifest request_count must be 320")
    if runtime_request_manifest.get("dataset_hash") != candidate_manifest.get("dataset_hash"):
        errors.append("runtime request manifest dataset_hash mismatch")
    if runtime_request_manifest.get("corpus_hash") != candidate_manifest.get("corpus_hash"):
        errors.append("runtime request manifest corpus_hash mismatch")
    for field in ["runtime_may_read_case_file", "runtime_may_read_gold", "runtime_may_read_world_model"]:
        if runtime_request_manifest.get(field) is not False:
            errors.append(f"runtime request manifest {field} must be false")
    if runtime_gold_isolation.get("passed") is not True:
        errors.append("runtime gold isolation report must pass")
    if runtime_gold_isolation.get("case_count") != 80:
        errors.append("runtime gold isolation report case_count must be 80")
    if runtime_gold_isolation.get("request_count") != 320:
        errors.append("runtime gold isolation report request_count must be 320")
    if runtime_gold_isolation.get("forbidden_field_count") != 0:
        errors.append("runtime gold isolation report forbidden_field_count must be 0")
    if runtime_gold_isolation.get("runtime_request_hash") != runtime_request_manifest.get("runtime_request_hash"):
        errors.append("runtime gold isolation report runtime_request_hash mismatch")
    if current_evidence.get("runtime_request_hash") != runtime_request_manifest.get("runtime_request_hash"):
        errors.append("track_manifest current_evidence runtime_request_hash mismatch")
    if current_evidence.get("runtime_request_case_count") != runtime_request_manifest.get("case_count"):
        errors.append("track_manifest current_evidence runtime_request_case_count mismatch")
    if current_evidence.get("runtime_gold_forbidden_field_count") != runtime_gold_isolation.get("forbidden_field_count"):
        errors.append("track_manifest current_evidence runtime_gold_forbidden_field_count mismatch")
    if source_upload_manifest.get("status") != "SOURCE_UPLOAD_INPUTS_PREPARED":
        errors.append("source upload manifest must be SOURCE_UPLOAD_INPUTS_PREPARED")
    if source_upload_manifest.get("source_count") != 8:
        errors.append("source upload manifest source_count must be 8")
    for field in ["runtime_ingested", "object_store_verified", "postgres_facts_verified"]:
        if source_upload_manifest.get(field) is not False:
            errors.append(f"source upload manifest {field} must be false")
    sources = source_upload_manifest.get("sources", [])
    if not isinstance(sources, list):
        errors.append("source upload manifest sources must be a list")
        sources = []
    for source in sources:
        if not isinstance(source, dict):
            errors.append("source upload manifest source entry must be an object")
            continue
        for field in ["source_id", "document_id", "tenant_id", "workspace_id", "security_scope", "source_hash", "idempotency_key"]:
            if not source.get(field):
                errors.append(f"source upload manifest source missing {field}")
        if source.get("initial_state") != "accepted":
            errors.append("source upload manifest source initial_state must be accepted")
    if source_upload_report.get("passed") is not True:
        errors.append("source upload manifest report must pass")
    if source_upload_report.get("source_count") != source_upload_manifest.get("source_count"):
        errors.append("source upload manifest report source_count mismatch")
    if source_upload_report.get("duplicate_source_count") != 0:
        errors.append("source upload manifest duplicate_source_count must be 0")
    if source_upload_report.get("source_manifest_hash") != source_upload_manifest.get("source_manifest_hash"):
        errors.append("source upload manifest report source_manifest_hash mismatch")
    if current_evidence.get("source_upload_manifest_hash") != source_upload_manifest.get("source_manifest_hash"):
        errors.append("track_manifest current_evidence source_upload_manifest_hash mismatch")
    if canonical_ir_manifest.get("status") != "CANONICAL_IR_INPUTS_PREPARED":
        errors.append("canonical IR manifest must be CANONICAL_IR_INPUTS_PREPARED")
    for field in ["parser_runtime_executed", "postgres_facts_verified", "knowledge_version_created"]:
        if canonical_ir_manifest.get(field) is not False:
            errors.append(f"canonical IR manifest {field} must be false")
    if canonical_ir_manifest.get("source_manifest_hash") != source_upload_manifest.get("source_manifest_hash"):
        errors.append("canonical IR manifest source_manifest_hash mismatch")
    if canonical_ir_manifest.get("document_count") != 8:
        errors.append("canonical IR manifest document_count must be 8")
    if not canonical_ir_manifest.get("chunk_count"):
        errors.append("canonical IR manifest chunk_count must be non-zero")
    if not canonical_ir_manifest.get("entity_count"):
        errors.append("canonical IR manifest entity_count must be non-zero")
    if not canonical_ir_manifest.get("relation_count"):
        errors.append("canonical IR manifest relation_count must be non-zero")
    relations = canonical_ir_manifest.get("relations", [])
    if not isinstance(relations, list):
        errors.append("canonical IR manifest relations must be a list")
        relations = []
    for relation in relations:
        if not isinstance(relation, dict):
            errors.append("canonical IR manifest relation entry must be an object")
            continue
        for field in ["relation_id", "kind", "from", "to", "direction", "evidence_chunk_ids"]:
            if not relation.get(field):
                errors.append(f"canonical IR manifest relation missing {field}")
        if relation.get("direction") != "outbound":
            errors.append("canonical IR manifest relation direction must be outbound")
    if canonical_ir_report.get("passed") is not True:
        errors.append("canonical IR manifest report must pass")
    for field in ["document_count", "chunk_count", "entity_count", "relation_count"]:
        if canonical_ir_report.get(field) != canonical_ir_manifest.get(field):
            errors.append(f"canonical IR manifest report {field} mismatch")
    if canonical_ir_report.get("canonical_ir_hash") != canonical_ir_manifest.get("canonical_ir_hash"):
        errors.append("canonical IR manifest report canonical_ir_hash mismatch")
    if current_evidence.get("canonical_ir_hash") != canonical_ir_manifest.get("canonical_ir_hash"):
        errors.append("track_manifest current_evidence canonical_ir_hash mismatch")
    if index_job_manifest.get("status") != "INDEX_JOBS_PREPARED":
        errors.append("index job manifest must be INDEX_JOBS_PREPARED")
    if index_job_manifest.get("canonical_ir_hash") != canonical_ir_manifest.get("canonical_ir_hash"):
        errors.append("index job manifest canonical_ir_hash mismatch")
    if index_job_manifest.get("index_job_count") != 3:
        errors.append("index job manifest index_job_count must be 3")
    if index_job_manifest.get("index_kinds") != ["elasticsearch_bm25", "milvus_vector", "neo4j_graph"]:
        errors.append("index job manifest index_kinds mismatch")
    if index_job_manifest.get("indexes_visible") is not False:
        errors.append("index job manifest indexes_visible must be false")
    if index_job_manifest.get("visibility_receipt_refs") != []:
        errors.append("index job manifest visibility_receipt_refs must be empty")
    if index_job_manifest.get("snapshot_activation_allowed") is not False:
        errors.append("index job manifest snapshot_activation_allowed must be false")
    jobs = index_job_manifest.get("jobs", [])
    if not isinstance(jobs, list):
        errors.append("index job manifest jobs must be a list")
        jobs = []
    for job in jobs:
        if not isinstance(job, dict):
            errors.append("index job manifest job entry must be an object")
            continue
        if job.get("state") != "prepared":
            errors.append("index job manifest job state must be prepared")
        for field in ["submitted_to_worker", "write_read_verified"]:
            if job.get(field) is not False:
                errors.append(f"index job manifest job {field} must be false")
        if job.get("visibility_receipt_ref") is not None:
            errors.append("index job manifest job visibility_receipt_ref must be null")
    if index_job_report.get("passed") is not True:
        errors.append("index job manifest report must pass")
    if index_job_report.get("index_job_count") != index_job_manifest.get("index_job_count"):
        errors.append("index job manifest report index_job_count mismatch")
    if index_job_report.get("index_job_manifest_hash") != index_job_manifest.get("index_job_manifest_hash"):
        errors.append("index job manifest report index_job_manifest_hash mismatch")
    if current_evidence.get("index_job_manifest_hash") != index_job_manifest.get("index_job_manifest_hash"):
        errors.append("track_manifest current_evidence index_job_manifest_hash mismatch")
    if snapshot_activation_manifest.get("status") != "snapshot_activation_blocked":
        errors.append("snapshot activation manifest must be snapshot_activation_blocked")
    if snapshot_activation_manifest.get("index_job_manifest_hash") != index_job_manifest.get("index_job_manifest_hash"):
        errors.append("snapshot activation manifest index_job_manifest_hash mismatch")
    if snapshot_activation_manifest.get("required_receipt_kinds") != [
        "elasticsearch_bm25_visibility",
        "milvus_vector_visibility",
        "neo4j_graph_visibility",
    ]:
        errors.append("snapshot activation manifest required_receipt_kinds mismatch")
    if snapshot_activation_manifest.get("provided_receipt_count") != 0:
        errors.append("snapshot activation manifest provided_receipt_count must be 0")
    if snapshot_activation_manifest.get("missing_receipt_kinds") != [
        "elasticsearch_bm25_visibility",
        "milvus_vector_visibility",
        "neo4j_graph_visibility",
    ]:
        errors.append("snapshot activation manifest missing_receipt_kinds mismatch")
    if snapshot_activation_manifest.get("activation_allowed") is not False:
        errors.append("snapshot activation manifest activation_allowed must be false")
    if snapshot_activation_manifest.get("snapshot_id") is not None:
        errors.append("snapshot activation manifest snapshot_id must be null")
    if snapshot_activation_manifest.get("activation_receipt_ref") is not None:
        errors.append("snapshot activation manifest activation_receipt_ref must be null")
    if snapshot_activation_report.get("passed") is not True:
        errors.append("snapshot activation manifest report must pass")
    if snapshot_activation_report.get("activation_allowed") is not False:
        errors.append("snapshot activation manifest report activation_allowed must be false")
    if snapshot_activation_report.get("missing_receipt_count") != 3:
        errors.append("snapshot activation manifest report missing_receipt_count must be 3")
    if snapshot_activation_report.get("snapshot_activation_manifest_hash") != snapshot_activation_manifest.get("snapshot_activation_manifest_hash"):
        errors.append("snapshot activation manifest report hash mismatch")
    if current_evidence.get("snapshot_activation_manifest_hash") != snapshot_activation_manifest.get("snapshot_activation_manifest_hash"):
        errors.append("track_manifest current_evidence snapshot_activation_manifest_hash mismatch")
    if current_evidence.get("neo4j_path_visibility_receipt_contract") != "CONTRACT_DEFINED_RUNTIME_NOT_EXECUTED":
        errors.append("track_manifest current_evidence neo4j path receipt contract status mismatch")
    report_field_pairs = {
        "candidate_derivation_valid_count": "derivation_valid_count",
        "candidate_source_evidence_valid_count": "source_evidence_valid_count",
        "candidate_unsupported_answer_count": "unsupported_answer_count",
        "candidate_duplicate_question_count": "duplicate_question_count",
        "candidate_gold_leakage_count": "gold_leakage_count",
        "candidate_hard_negative_valid_count": "hard_negative_valid_count",
        "candidate_hash_valid_count": "hash_valid_count",
        "candidate_answer_derivation_valid_count": "answer_derivation_valid_count",
        "candidate_world_model_valid_count": "world_model_valid_count",
    }
    for manifest_field, report_field in report_field_pairs.items():
        if current_evidence.get(manifest_field) != derivation_report.get(report_field):
            errors.append(f"track_manifest {manifest_field} must match derivation report {report_field}")
    if current_evidence.get("candidate_derivation_report_hash") != derivation_report.get("report_hash"):
        errors.append("track_manifest candidate_derivation_report_hash must match derivation report")

    required_report_phrases = [
        "status: BLOCKED_WITH_EXACT_GAPS",
        "PHASE22：`in_progress`",
        "Production Readiness：not established",
        "Public Benchmark：`reviewer_approved_count=0`",
        "PR #100",
        "PR #104",
        "PR #105",
        "CONTRACT_DEFINED_RUNTIME_NOT_EXECUTED",
        "two-hop runtime read-back：NOT_RUN",
    ]
    for phrase in required_report_phrases:
        if phrase not in report:
            errors.append(f"readiness report missing phrase: {phrase}")

    for phrase in ["INVALIDATED", "canonical_runtime_not_executed", "SUCCESS_REAL_INGESTION"]:
        if phrase not in invalidation:
            errors.append(f"synthetic invalidation notice missing phrase: {phrase}")

    files_by_path = {
        item.get("path"): item.get("classification")
        for item in pr100_classification.get("files", [])
        if isinstance(item, dict)
    }
    required_classifications = {
        "docs/evidence/goal05-phase22-synthetic-benchmark/build_world_model.py": "ACCEPT_AFTER_REWORK",
        "docs/evidence/goal05-phase22-synthetic-benchmark/build_cases.py": "ACCEPT_AFTER_REWORK",
        "docs/evidence/goal05-phase22-synthetic-benchmark/synthetic_cases.jsonl": "ACCEPT_AFTER_REWORK",
        "docs/evidence/goal05-phase22-synthetic-benchmark/ingest_and_run.py": "DROP",
        "docs/evidence/goal05-phase22-synthetic-benchmark/profile_results/*.json": "DROP",
        "docs/evidence/goal05-phase22-synthetic-benchmark/release_decision.json": "DROP",
        "docs/evidence/goal05-phase22-synthetic-benchmark/runtime_ingestion.json": "DROP",
    }
    for path, expected in required_classifications.items():
        if files_by_path.get(path) != expected:
            errors.append(
                f"PR100 file classification for {path} must be {expected}, got {files_by_path.get(path)!r}"
            )

    required_card_fields = [
        "WORKER_TASK_ID",
        "Base SHA",
        "Goal",
        "Current Gap",
        "Allowed Paths",
        "Forbidden Paths",
        "Contracts",
        "Owner",
        "State Transitions",
        "Failure Semantics",
        "Retry / Recovery / Idempotency",
        "Security",
        "Required Tests",
        "Acceptance Criteria",
        "Commit Contract",
        "Handoff Format",
    ]
    for card in TASK_CARDS:
        text = _read_text(card)
        for field in required_card_fields:
            if field not in text:
                errors.append(f"{card.as_posix()} missing task-card field: {field}")

    return errors


def main() -> int:
    errors = verify_phase22_synthetic_regression_track()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("PHASE22 synthetic regression track boundary passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
