"""add phase20 observability eval runtime

Revision ID: 20260729_53
Revises: 20260728_52
Create Date: 2026-07-29 00:53:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260729_53"
down_revision = "20260728_52"
branch_labels = None
depends_on = None


def _hash_check(column_name: str, constraint_name: str) -> sa.CheckConstraint:
    return sa.CheckConstraint(
        f"char_length({column_name}) = 64 and {column_name} ~ '^[0-9a-f]+$'",
        name=constraint_name,
    )


def upgrade() -> None:
    op.create_table(
        "observability_eval_datasets",
        sa.Column("dataset_hash", sa.String(length=64), primary_key=True),
        sa.Column("dataset_id", sa.String(length=160), nullable=False),
        sa.Column("version", sa.String(length=80), nullable=False),
        sa.Column("case_hashes", sa.JSON(), nullable=False),
        sa.Column("supersedes_dataset_hash", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        _hash_check("dataset_hash", "ck_observability_eval_datasets_hash"),
        sa.UniqueConstraint("dataset_id", "version", name="uq_observability_eval_datasets_version"),
    )
    op.create_table(
        "observability_eval_cases",
        sa.Column("case_hash", sa.String(length=64), primary_key=True),
        sa.Column("dataset_hash", sa.String(length=64), nullable=False),
        sa.Column("case_id", sa.String(length=180), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("reference_claim_refs", sa.JSON(), nullable=False),
        sa.Column("gold_evidence_refs", sa.JSON(), nullable=False),
        sa.Column("slices", sa.JSON(), nullable=False),
        sa.Column("security_scope_ref", sa.String(length=240), nullable=False),
        sa.Column("case_payload", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["dataset_hash"], ["observability_eval_datasets.dataset_hash"], name="fk_observability_eval_cases_dataset"),
        _hash_check("case_hash", "ck_observability_eval_cases_hash"),
        sa.UniqueConstraint("dataset_hash", "case_id", name="uq_observability_eval_cases_dataset_case"),
    )
    op.create_table(
        "observability_eval_runs",
        sa.Column("run_id", sa.String(length=180), primary_key=True),
        sa.Column("profile_id", sa.String(length=160), nullable=False),
        sa.Column("dataset_hash", sa.String(length=64), nullable=False),
        sa.Column("config_hash", sa.String(length=64), nullable=False),
        sa.Column("corpus_snapshot_hash", sa.String(length=64), nullable=False),
        sa.Column("index_snapshot_hash", sa.String(length=64), nullable=False),
        sa.Column("model_profile_hash", sa.String(length=64), nullable=False),
        sa.Column("judge_policy_hash", sa.String(length=64), nullable=False),
        sa.Column("embedding_profile_hash", sa.String(length=64), nullable=False),
        sa.Column("metric_config_hash", sa.String(length=64), nullable=False),
        sa.Column("runtime_profile_hash", sa.String(length=64), nullable=False),
        sa.Column("security_scope_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("result_set_hash", sa.String(length=64), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["dataset_hash"], ["observability_eval_datasets.dataset_hash"], name="fk_observability_eval_runs_dataset"),
        _hash_check("config_hash", "ck_observability_eval_runs_config_hash"),
        _hash_check("dataset_hash", "ck_observability_eval_runs_dataset_hash"),
        _hash_check("corpus_snapshot_hash", "ck_observability_eval_runs_corpus_hash"),
        _hash_check("index_snapshot_hash", "ck_observability_eval_runs_index_hash"),
        _hash_check("model_profile_hash", "ck_observability_eval_runs_model_hash"),
        _hash_check("judge_policy_hash", "ck_observability_eval_runs_judge_hash"),
        _hash_check("embedding_profile_hash", "ck_observability_eval_runs_embedding_hash"),
        _hash_check("metric_config_hash", "ck_observability_eval_runs_metric_hash"),
        _hash_check("runtime_profile_hash", "ck_observability_eval_runs_runtime_hash"),
        _hash_check("security_scope_hash", "ck_observability_eval_runs_security_hash"),
        sa.CheckConstraint("status in ('PREPARED','RUNNING','PARTIAL','COMPLETED','BLOCKED','CANCELLED')", name="ck_observability_eval_runs_status"),
    )
    op.create_table(
        "observability_eval_case_executions",
        sa.Column("case_execution_id", sa.String(length=220), primary_key=True),
        sa.Column("run_id", sa.String(length=180), nullable=False),
        sa.Column("case_hash", sa.String(length=64), nullable=False),
        sa.Column("case_id", sa.String(length=180), nullable=False),
        sa.Column("attempt", sa.Integer(), nullable=False),
        sa.Column("lease_ref", sa.String(length=240), nullable=False),
        sa.Column("checkpoint_ref", sa.String(length=240), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("recovered", sa.Boolean(), nullable=False),
        sa.Column("failure_buckets", sa.JSON(), nullable=False),
        sa.Column("execution_hash", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["observability_eval_runs.run_id"], name="fk_observability_eval_case_executions_run"),
        sa.ForeignKeyConstraint(["case_hash"], ["observability_eval_cases.case_hash"], name="fk_observability_eval_case_executions_case"),
        _hash_check("case_hash", "ck_observability_eval_case_executions_case_hash"),
        _hash_check("execution_hash", "ck_observability_eval_case_executions_hash"),
        sa.CheckConstraint("attempt > 0", name="ck_observability_eval_case_executions_attempt"),
        sa.CheckConstraint("status in ('PREPARED','RUNNING','PARTIAL','COMPLETED','BLOCKED','CANCELLED')", name="ck_observability_eval_case_executions_status"),
        sa.UniqueConstraint("run_id", "case_id", "attempt", name="uq_observability_eval_case_executions_attempt"),
    )
    op.create_table(
        "observability_eval_metric_results",
        sa.Column("metric_result_id", sa.String(length=240), primary_key=True),
        sa.Column("case_execution_id", sa.String(length=220), nullable=False),
        sa.Column("metric_name", sa.String(length=80), nullable=False),
        sa.Column("measurement_status", sa.String(length=40), nullable=False),
        sa.Column("metric_value", sa.Float(), nullable=True),
        sa.Column("reason", sa.String(length=240), nullable=False),
        sa.Column("metric_hash", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["case_execution_id"], ["observability_eval_case_executions.case_execution_id"], name="fk_observability_eval_metric_results_execution"),
        _hash_check("metric_hash", "ck_observability_eval_metric_results_hash"),
        sa.CheckConstraint("measurement_status in ('MEASURED','BLOCKED','UNAVAILABLE','INVALID')", name="ck_observability_eval_metric_results_status"),
        sa.UniqueConstraint("case_execution_id", "metric_name", name="uq_observability_eval_metric_results_metric"),
    )
    op.create_table(
        "observability_graphrag_diagnostics",
        sa.Column("diagnostic_id", sa.String(length=220), primary_key=True),
        sa.Column("run_id", sa.String(length=180), nullable=False),
        sa.Column("case_id", sa.String(length=180), nullable=False),
        sa.Column("route_profile", sa.String(length=80), nullable=False),
        sa.Column("retrieval_round", sa.Integer(), nullable=False),
        sa.Column("diagnostic_payload", sa.JSON(), nullable=False),
        sa.Column("failure_buckets", sa.JSON(), nullable=False),
        sa.Column("diagnostic_hash", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["observability_eval_runs.run_id"], name="fk_observability_graphrag_diagnostics_run"),
        _hash_check("diagnostic_hash", "ck_observability_graphrag_diagnostics_hash"),
        sa.CheckConstraint("retrieval_round > 0", name="ck_observability_graphrag_diagnostics_round"),
    )
    op.create_table(
        "observability_agent_efficiency_snapshots",
        sa.Column("snapshot_id", sa.String(length=220), primary_key=True),
        sa.Column("run_id", sa.String(length=180), nullable=False),
        sa.Column("settled_cost_available", sa.Boolean(), nullable=False),
        sa.Column("wasted_work_ratio", sa.Float(), nullable=False),
        sa.Column("parallel_efficiency", sa.Float(), nullable=False),
        sa.Column("snapshot_payload", sa.JSON(), nullable=False),
        sa.Column("snapshot_hash", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["observability_eval_runs.run_id"], name="fk_observability_agent_efficiency_snapshots_run"),
        _hash_check("snapshot_hash", "ck_observability_agent_efficiency_snapshots_hash"),
        sa.CheckConstraint("wasted_work_ratio >= 0", name="ck_observability_agent_efficiency_snapshots_waste"),
        sa.CheckConstraint("parallel_efficiency >= 0 and parallel_efficiency <= 1", name="ck_observability_agent_efficiency_snapshots_parallel"),
    )
    op.create_table(
        "observability_failure_buckets",
        sa.Column("bucket_id", sa.String(length=220), primary_key=True),
        sa.Column("run_id", sa.String(length=180), nullable=False),
        sa.Column("case_id", sa.String(length=180), nullable=False),
        sa.Column("bucket", sa.String(length=120), nullable=False),
        sa.Column("bucket_hash", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["observability_eval_runs.run_id"], name="fk_observability_failure_buckets_run"),
        _hash_check("bucket_hash", "ck_observability_failure_buckets_hash"),
        sa.UniqueConstraint("run_id", "case_id", "bucket", name="uq_observability_failure_buckets_case_bucket"),
    )
    op.create_table(
        "observability_benchmark_comparisons",
        sa.Column("comparison_hash", sa.String(length=64), primary_key=True),
        sa.Column("baseline_run_id", sa.String(length=180), nullable=False),
        sa.Column("candidate_run_id", sa.String(length=180), nullable=False),
        sa.Column("comparable", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("reason", sa.String(length=240), nullable=False),
        sa.ForeignKeyConstraint(["baseline_run_id"], ["observability_eval_runs.run_id"], name="fk_observability_benchmark_comparisons_baseline"),
        sa.ForeignKeyConstraint(["candidate_run_id"], ["observability_eval_runs.run_id"], name="fk_observability_benchmark_comparisons_candidate"),
        _hash_check("comparison_hash", "ck_observability_benchmark_comparisons_hash"),
        sa.CheckConstraint("status in ('PASSED','FAILED','BLOCKED','INCOMPARABLE','ERROR')", name="ck_observability_benchmark_comparisons_status"),
    )
    op.create_table(
        "observability_evidence_records",
        sa.Column("evidence_hash", sa.String(length=64), primary_key=True),
        sa.Column("evidence_id", sa.String(length=180), nullable=False),
        sa.Column("artifact_ref", sa.String(length=360), nullable=False),
        sa.Column("artifact_hash", sa.String(length=64), nullable=False),
        sa.Column("result_set_hash", sa.String(length=64), nullable=False),
        sa.Column("gate_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        _hash_check("evidence_hash", "ck_observability_evidence_records_hash"),
        _hash_check("artifact_hash", "ck_observability_evidence_records_artifact_hash"),
        _hash_check("result_set_hash", "ck_observability_evidence_records_result_set_hash"),
        _hash_check("gate_hash", "ck_observability_evidence_records_gate_hash"),
        sa.UniqueConstraint("evidence_id", name="uq_observability_evidence_records_id"),
    )
    op.create_table(
        "observability_release_gate_evaluations",
        sa.Column("gate_hash", sa.String(length=64), primary_key=True),
        sa.Column("gate_id", sa.String(length=180), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("reason", sa.String(length=240), nullable=False),
        sa.Column("result_set_hash", sa.String(length=64), nullable=False),
        sa.Column("comparison_hash", sa.String(length=64), nullable=True),
        sa.Column("evidence_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["comparison_hash"], ["observability_benchmark_comparisons.comparison_hash"], name="fk_observability_release_gate_evaluations_comparison"),
        sa.ForeignKeyConstraint(["evidence_hash"], ["observability_evidence_records.evidence_hash"], name="fk_observability_release_gate_evaluations_evidence"),
        _hash_check("gate_hash", "ck_observability_release_gate_evaluations_hash"),
        _hash_check("result_set_hash", "ck_observability_release_gate_evaluations_result_set_hash"),
        sa.CheckConstraint("status in ('PASSED','FAILED','BLOCKED','INCOMPARABLE','ERROR')", name="ck_observability_release_gate_evaluations_status"),
    )


def downgrade() -> None:
    op.drop_table("observability_release_gate_evaluations")
    op.drop_table("observability_evidence_records")
    op.drop_table("observability_benchmark_comparisons")
    op.drop_table("observability_failure_buckets")
    op.drop_table("observability_agent_efficiency_snapshots")
    op.drop_table("observability_graphrag_diagnostics")
    op.drop_table("observability_eval_metric_results")
    op.drop_table("observability_eval_case_executions")
    op.drop_table("observability_eval_runs")
    op.drop_table("observability_eval_cases")
    op.drop_table("observability_eval_datasets")
