"""Tests for the PHASE22 Formal Benchmark Execution Entry.

Covers the P22-T01 formal-execution-readiness contract:

- Manifest Schema validation
- four-profile completeness
- dataset / case hash validation against the ACTUAL files
- runtime / credential / reviewer / budget / security attestation gates
- artifact hash, Git SHA, environment manifest, rerun reproducibility
- profile-independent blockers (one blocked profile never fakes the others)
- test doubles can never become MEASURED
- RUNTIME_OBSERVED never auto-promotes to MEASURED
- single-profile MEASURED never passes the whole run
- four-profile MEASURED but incomparable -> INCOMPARABLE
- measurement attestation missing / invalid -> BLOCKED
- formal fixture happy path with serialized attestations
"""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any, Mapping

from tools.evals.zuno.rag_eval.benchmark_preflight import (
    FORMAL_CREDENTIAL_ATTESTATION_VERSION,
    FORMAL_EXECUTION_ATTESTATION_VERSION,
    HUMAN_BUDGET_ATTESTATION_VERSION,
    PRODUCT_RUNTIME_ATTESTATION_VERSION,
    REVIEWER_ATTESTATION_VERSION,
    compute_formal_credential_attestation_hash,
    compute_formal_execution_attestation_hash,
    compute_human_budget_attestation_hash,
    compute_product_runtime_attestation_hash,
    compute_reviewer_attestation_hash,
)
from tools.evals.zuno.rag_eval.canonical_profile_runners import (
    CanonicalCaseInput,
    CanonicalCaseResult,
)
from tools.evals.zuno.rag_eval.run_phase22_formal_benchmark import (
    BLOCKER_ARTIFACT_STORE_UNAVAILABLE,
    BLOCKER_BUDGET_APPROVAL_MISSING,
    BLOCKER_CASE_SET_HASH_MISMATCH,
    BLOCKER_DATASET_HASH_MISMATCH,
    BLOCKER_MANIFEST_SCHEMA_INVALID,
    BLOCKER_MEASUREMENT_ATTESTATION_INVALID,
    BLOCKER_MEASUREMENT_ATTESTATION_MISSING,
    BLOCKER_MISSING_FORMAL_CREDENTIAL,
    BLOCKER_PROFILE_RUNTIME_UNAVAILABLE,
    BLOCKER_REVIEWER_NOT_APPROVED,
    BLOCKER_RUNTIME_ATTESTATION_INVALID,
    BLOCKER_SECURITY_APPROVAL_MISSING,
    BLOCKER_TEST_DOUBLE,
    CANONICAL_PROFILES,
    MANIFEST_VERSION,
    STATUS_BLOCKED,
    STATUS_INCOMPARABLE,
    STATUS_MEASURED,
    STATUS_RUNTIME_OBSERVED,
    build_profile_artifact,
    canonical_case_id_hash,
    run_formal_benchmark,
    serialize_json,
    sha256_file,
    text_sha256,
)
from tools.evals.zuno.rag_eval.release_decision import (
    MEASUREMENT_ATTESTATION_VERSION,
    compute_measurement_attestation_hash,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _sha256_hex(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()


class _AttestationBuilder:
    """Builds serialized attestations with valid canonical hashes."""

    @staticmethod
    def _with_hash(payload: Mapping[str, Any], compute) -> dict[str, Any]:
        base = dict(payload)
        base["attestation_hash"] = compute(base)
        return base

    def reviewer(
        self,
        *,
        eval_run_id: str,
        case_set_ref: str,
        dataset_version: str,
        dataset_hash: str,
        candidate_count: int,
        reviewer_status: str = "approved",
        benchmark_eligible: bool = True,
    ) -> dict[str, Any]:
        return self._with_hash(
            {
                "attestation_ref": "reviewer-attestation:test:approved",
                "eval_run_id": eval_run_id,
                "case_set_ref": case_set_ref,
                "dataset_version": dataset_version,
                "dataset_hash": dataset_hash,
                "candidate_count": candidate_count,
                "reviewer_status": reviewer_status,
                "benchmark_eligible": benchmark_eligible,
                "reviewer_attestation_contract_version": REVIEWER_ATTESTATION_VERSION,
            },
            compute_reviewer_attestation_hash,
        )

    def credential(
        self,
        *,
        eval_run_id: str,
        credential_ref: str,
        authorization_ref: str,
        security_epoch: str,
    ) -> dict[str, Any]:
        return self._with_hash(
            {
                "attestation_ref": "credential-attestation:test:valid",
                "eval_run_id": eval_run_id,
                "credential_ref": credential_ref,
                "authorization_ref": authorization_ref,
                "security_epoch": security_epoch,
                "formal_execution_ref": "formal-execution:test:1",
                "formal_credential_contract_version": FORMAL_CREDENTIAL_ATTESTATION_VERSION,
            },
            compute_formal_credential_attestation_hash,
        )

    def formal_execution(
        self,
        *,
        eval_run_id: str,
        authorization_ref: str,
        security_epoch: str,
        approved: bool = True,
        requested: bool = True,
    ) -> dict[str, Any]:
        return self._with_hash(
            {
                "attestation_ref": "formal-execution-attestation:test:approved",
                "eval_run_id": eval_run_id,
                "authorization_ref": authorization_ref,
                "security_epoch": security_epoch,
                "formal_execution_approved": approved,
                "formal_execution_requested": requested,
                "formal_execution_attestation_contract_version": FORMAL_EXECUTION_ATTESTATION_VERSION,
            },
            compute_formal_execution_attestation_hash,
        )

    def budget(
        self,
        *,
        eval_run_id: str,
        budget_policy_ref: str,
        provider_cost_limit: float = 100.0,
        token_limit: int = 100000,
        deadline: str = "2026-12-31T00:00:00+00:00",
        approved: bool = True,
    ) -> dict[str, Any]:
        return self._with_hash(
            {
                "attestation_ref": "budget-attestation:test:approved",
                "eval_run_id": eval_run_id,
                "budget_policy_ref": budget_policy_ref,
                "provider_cost_limit": provider_cost_limit,
                "token_limit": token_limit,
                "deadline": deadline,
                "human_budget_approved": approved,
                "human_budget_attestation_contract_version": HUMAN_BUDGET_ATTESTATION_VERSION,
            },
            compute_human_budget_attestation_hash,
        )

    def runtime(
        self,
        *,
        profile_name: str,
        runtime_name: str,
        runtime_version: str,
        corpus_snapshot_ref: str,
        security_epoch: str,
        forged: bool = False,
    ) -> dict[str, Any]:
        payload = {
            "attestation_ref": f"runtime-attestation:test:{profile_name}",
            "profile_name": profile_name,
            "runtime_name": runtime_name,
            "runtime_version": runtime_version,
            "corpus_snapshot_ref": corpus_snapshot_ref,
            "security_epoch": security_epoch,
            "formal_adapter_ref": f"canonical-adapter://phase22/{profile_name}",
            "runtime_evidence_contract_version": PRODUCT_RUNTIME_ATTESTATION_VERSION,
        }
        attestation = dict(payload)
        attestation["attestation_hash"] = compute_product_runtime_attestation_hash(
            attestation
        )
        if forged:
            attestation["attestation_hash"] = "f" * 64
        return attestation


class _FixtureManifest:
    """Builds a fully READY formal benchmark manifest over a temp dataset."""

    def __init__(self, tmp: Path, seed: str = "case") -> None:
        self.tmp = Path(tmp)
        self.dataset_path = self.tmp / "dataset.jsonl"
        self.rows = [
            {
                "id": f"{seed}-{i}",
                "case_id": f"{seed}-{i}",
                "question": f"question {i}",
                "question_type": "simple_retrieval",
                "complexity": "simple",
                "expected_doc_ids": [f"doc-{i}"],
                "expected_answer": f"answer {i}",
            }
            for i in range(1, 5)
        ]
        self.dataset_path.write_text(
            "\n".join(json.dumps(row) for row in self.rows) + "\n",
            encoding="utf-8",
        )
        self.dataset_hash = sha256_file(self.dataset_path)
        self.case_set_hash = canonical_case_id_hash(self.rows)
        self.eval_run_id = "phase22-formal-entry-test"
        self.case_set_ref = "PublicBenchmarkSuiteV1::test"
        self.dataset_version = "test-v1"
        self.security_epoch = "security-epoch:test:v1"
        self.authorization_ref = "authorization:test:1"
        self.budget_policy_ref = "budget-policy:test:v1"
        self.credential_ref = "credential:test:1"
        self.deadline = "2026-12-31T00:00:00+00:00"
        self.attestations = _AttestationBuilder()

    def profile_block(self, profile_name: str, **overrides: Any) -> dict[str, Any]:
        block = {
            "profile_name": profile_name,
            "case_set_ref": self.case_set_ref,
            "dataset_version": self.dataset_version,
            "corpus_snapshot_ref": "corpus-snapshot:test:v1",
            # Fixed-benchmark contract: all four profiles run the SAME
            # knowledge snapshot (comparable surface).
            "knowledge_snapshot_ref": "knowledge-snapshot:test:v1",
            "model_config_ref": "model-config:test:gpt-4o",
            "judge_config_ref": "judge-config:test:gpt-4o-mini",
            "embedding_config_ref": "embedding-config:test:embed-3-small",
            "metric_definition_ref": "metric-definition:test:enterprise-rag-v1",
            "security_epoch": self.security_epoch,
            "budget_policy_ref": self.budget_policy_ref,
            "runtime_name": f"canonical-{profile_name}-runtime",
            "runtime_version": "phase22-canonical-runtime-v1",
            "product_runtime_attested": True,
            "product_runtime_attestation": self.attestations.runtime(
                profile_name=profile_name,
                runtime_name=f"canonical-{profile_name}-runtime",
                runtime_version="phase22-canonical-runtime-v1",
                corpus_snapshot_ref="corpus-snapshot:test:v1",
                security_epoch=self.security_epoch,
            ),
            "formal_adapter_wired": True,
            "knowledge_runtime_available": True,
            "index_runtime_available": True,
            "agent_run_runtime_available": True,
            "trace_adapter_available": True,
            "result_store_available": True,
            "artifact_store_available": True,
            "usage_receipt_provider_available": True,
            "budget_settlement_provider_available": True,
        }
        block.update(overrides)
        return block

    def build(self, **overrides: Any) -> dict[str, Any]:
        manifest = {
            "manifest_version": MANIFEST_VERSION,
            "eval_run_id": self.eval_run_id,
            "case_set_ref": self.case_set_ref,
            "dataset_version": self.dataset_version,
            "dataset_path": str(self.dataset_path),
            "dataset_hash": self.dataset_hash,
            "case_set_hash": self.case_set_hash,
            "candidate_count": len(self.rows),
            "reviewer_status": "approved",
            "benchmark_eligible": True,
            "reviewer_attestation": self.attestations.reviewer(
                eval_run_id=self.eval_run_id,
                case_set_ref=self.case_set_ref,
                dataset_version=self.dataset_version,
                dataset_hash=self.dataset_hash,
                candidate_count=len(self.rows),
            ),
            "license_status": "verified",
            "integrity_status": "verified",
            "runtime_request_schema_gold_free": True,
            "authorization_ref": self.authorization_ref,
            "security_epoch": self.security_epoch,
            "security_epoch_stale": False,
            "formal_execution_approved": True,
            "formal_execution_attestation": self.attestations.formal_execution(
                eval_run_id=self.eval_run_id,
                authorization_ref=self.authorization_ref,
                security_epoch=self.security_epoch,
            ),
            "human_budget_approved": True,
            "human_budget_attestation": self.attestations.budget(
                eval_run_id=self.eval_run_id,
                budget_policy_ref=self.budget_policy_ref,
            ),
            "budget_policy_ref": self.budget_policy_ref,
            "provider_cost_limit": 100.0,
            "token_limit": 100000,
            "deadline": self.deadline,
            "credential_ref": self.credential_ref,
            "has_formal_credentials": True,
            "formal_execution_requested": True,
            "formal_credential_attestation": self.attestations.credential(
                eval_run_id=self.eval_run_id,
                credential_ref=self.credential_ref,
                authorization_ref=self.authorization_ref,
                security_epoch=self.security_epoch,
            ),
            "output_artifact_ref": "artifact-store://test/phase22",
            "profiles": [self.profile_block(name) for name in CANONICAL_PROFILES],
        }
        manifest.update(overrides)
        return manifest


class _FakeFactory:
    """Injected profile runtime factory for the entry."""

    def __init__(
        self,
        *,
        state: str = "MEASURED",
        is_test_double: bool = False,
        measurement_attestation: Mapping[str, Any] | None = None,
        fail_profiles: set[str] | None = None,
        per_profile_override: Mapping[str, str] | None = None,
    ) -> None:
        self.state = state
        self.is_test_double = is_test_double
        self.measurement_attestation = measurement_attestation
        self.fail_profiles = set(fail_profiles or ())
        self.per_profile_override = dict(per_profile_override or {})

    def create_runner(self, profile_name: str) -> "_FakeRunner":
        if profile_name in self.fail_profiles:
            raise RuntimeError("factory_create_runner_failed")
        return _FakeRunner(
            profile_name=profile_name,
            state=self.per_profile_override.get(profile_name, self.state),
            is_test_double=self.is_test_double,
            measurement_attestation=self.measurement_attestation,
        )


class _FakeRunner:
    def __init__(
        self,
        *,
        profile_name: str,
        state: str,
        is_test_double: bool = False,
        measurement_attestation: Mapping[str, Any] | None = None,
    ) -> None:
        self._profile_name = profile_name
        self._state = state
        self._is_test_double = is_test_double
        self._measurement_attestation = measurement_attestation

    def run_canonical_case(self, case_input: CanonicalCaseInput) -> CanonicalCaseResult:
        # The fake measurement owner embeds only THIS profile's attestation
        # in its results (a container map would be rejected by the entry).
        attestation = None
        if isinstance(self._measurement_attestation, Mapping):
            if "profile_id" in self._measurement_attestation:
                attestation = self._measurement_attestation
            else:
                attestation = self._measurement_attestation.get(
                    case_input.profile_name
                )
        else:
            attestation = self._measurement_attestation
        return CanonicalCaseResult(
            eval_run_id=case_input.eval_run_id,
            case_id=case_input.case_id,
            profile_name=case_input.profile_name,
            runtime_status="completed",
            measurement_state=self._state,
            answer="mock answer",
            retrieved_document_refs=tuple(case_input.gold_document_refs),
            retrieved_evidence_refs=(),
            citation_refs=(),
            knowledge_snapshot_ref=case_input.corpus_snapshot_ref,
            plan_version_ref=f"plan:{case_input.case_id}",
            run_outcome_ref=f"outcome:{case_input.case_id}",
            budget_settlement_ref=f"budget:{case_input.case_id}",
            artifact_receipt_ref=f"artifact:{case_input.case_id}",
            trace_id=f"trace:{case_input.case_id}",
            is_test_double=self._is_test_double,
            evidence_refs=(f"evidence:{case_input.eval_run_id}:{case_input.case_id}",),
            measurement_attestation=attestation,
        )


def _measurement_attestation_for(
    *,
    profile_id: str,
    artifact_payload: Mapping[str, Any],
    evidence_ref: str,
) -> dict[str, Any]:
    """Build a valid measurement attestation bound to the deterministic
    facts artifact (same serialization the entry uses)."""
    facts_text = serialize_json(dict(artifact_payload))
    artifact_hash = text_sha256(facts_text)
    fingerprint_hash = str(artifact_payload.get("fingerprint_hash") or "")
    attestation = {
        "attestation_ref": f"measurement-attestation:test:{profile_id}",
        "profile_id": profile_id,
        "measurement_status": "MEASURED",
        "artifact_hash": artifact_hash,
        "fingerprint_hash": fingerprint_hash,
        "evidence_ref": evidence_ref,
        "measurement_attestation_contract_version": MEASUREMENT_ATTESTATION_VERSION,
    }
    attestation["attestation_hash"] = compute_measurement_attestation_hash(
        attestation
    )
    return attestation


def _run_fake_results(
    factory: _FakeFactory, profile_name: str, manifest: Mapping[str, Any], rows: list[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    """Replicate the entry's per-case execution for the fake runner so the
    test can build the exact deterministic artifact the entry will produce."""
    import dataclasses

    from tools.evals.zuno.rag_eval.canonical_profile_runners import CanonicalCaseInput

    runner = factory.create_runner(profile_name)
    results: list[dict[str, Any]] = []
    for row in rows:
        case_input = CanonicalCaseInput(
            eval_run_id=str(manifest.get("eval_run_id") or ""),
            case_id=str(row.get("case_id") or row.get("id") or ""),
            profile_name=profile_name,
            question=str(row.get("question") or row.get("query") or ""),
            question_type=str(row.get("question_type") or "unknown"),
            corpus_snapshot_ref=str(row.get("corpus_snapshot_ref") or ""),
            gold_document_refs=tuple(str(item) for item in (row.get("expected_doc_ids") or [])),
            gold_evidence_refs=tuple(str(item) for item in (row.get("gold_evidence") or [])),
            authorization_ref=str(manifest.get("authorization_ref") or ""),
            security_epoch=str(manifest.get("security_epoch") or ""),
            deadline=str(manifest.get("deadline") or ""),
        )
        results.append(dataclasses.asdict(runner.run_canonical_case(case_input)))
    return results


def _profile_artifact_for(
    *,
    manifest: Mapping[str, Any],
    profile_name: str,
    rows: list[Mapping[str, Any]],
    case_set_hash: str,
    results: list[Mapping[str, Any]],
) -> dict[str, Any]:
    from tools.evals.zuno.rag_eval.benchmark_preflight import (
        ProfilePreflightResult,
        STATE_READY,
    )

    profile_block = next(
        entry
        for entry in manifest["profiles"]
        if entry.get("profile_name") == profile_name
    )
    return build_profile_artifact(
        profile_name=profile_name,
        manifest=manifest,
        profile_block=profile_block,
        case_set_hash=case_set_hash,
        rows=rows,
        results=[dict(item) for item in results],
        measurement_status="MEASURED",
        blocker_codes=[],
        blocker_details=[],
        # The entry records the per-profile preflight verdict in the
        # artifact; a READY profile yields a READY preflight result.
        preflight_profile_result=ProfilePreflightResult(
            profile_name=profile_name, state=STATE_READY, gap_codes=()
        ),
    )


def _attestations_for(
    factory: _FakeFactory,
    manifest: Mapping[str, Any],
    rows: list[Mapping[str, Any]],
    case_set_hash: str,
) -> dict[str, dict[str, Any]]:
    """Build valid measurement attestations bound to the exact deterministic
    artifacts the entry will produce for the given fake factory."""
    attestations: dict[str, dict[str, Any]] = {}
    for profile_name in CANONICAL_PROFILES:
        results = _run_fake_results(factory, profile_name, manifest, rows)
        evidence_ref = ""
        for item in results:
            refs = item.get("evidence_refs") or []
            if refs:
                evidence_ref = str(refs[0])
                break
        artifact_payload = _profile_artifact_for(
            manifest=manifest,
            profile_name=profile_name,
            rows=rows,
            case_set_hash=case_set_hash,
            results=results,
        )
        attestations[profile_name] = _measurement_attestation_for(
            profile_id=profile_name,
            artifact_payload=artifact_payload,
            evidence_ref=evidence_ref,
        )
    return attestations


class FormalBenchmarkEntryTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="phase22-formal-entry-")
        self.tmp = Path(self._tmp)
        self.fixture = _FixtureManifest(self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self._tmp, ignore_errors=True)

    def _output(self, name: str) -> Path:
        path = self.tmp / f"out-{name}"
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)
        return path

    def _read_report(self, output: Path) -> dict[str, Any]:
        return json.loads(
            (output / "benchmark_report.json").read_text(encoding="utf-8")
        )

    @staticmethod
    def _read_artifact(output: Path, profile_name: str) -> str:
        return (output / "profiles" / f"{profile_name}.json").read_text(
            encoding="utf-8"
        )

    # ------------------------------------------------------------------
    # 1. Manifest Schema
    # ------------------------------------------------------------------

    def test_manifest_schema_invalid_blocks(self) -> None:
        manifest = self.fixture.build()
        del manifest["manifest_version"]
        report = run_formal_benchmark(
            manifest, self._output("schema"), profile_runtime_factory=_FakeFactory()
        )
        self.assertEqual(report["overall_status"], "ERROR")
        self.assertIn(BLOCKER_MANIFEST_SCHEMA_INVALID, report.get("error", ""))

    def test_manifest_profile_field_missing_blocks(self) -> None:
        manifest = self.fixture.build()
        manifest["profiles"][0]["model_config_ref"] = ""
        report = run_formal_benchmark(
            manifest, self._output("profile-field"), profile_runtime_factory=_FakeFactory()
        )
        self.assertEqual(report["overall_status"], "ERROR")
        self.assertEqual(report.get("error"), BLOCKER_MANIFEST_SCHEMA_INVALID)

    # ------------------------------------------------------------------
    # 2. Four-profile completeness
    # ------------------------------------------------------------------

    def test_four_profile_set_incomplete_blocks(self) -> None:
        manifest = self.fixture.build()
        manifest["profiles"] = manifest["profiles"][:3]
        report = run_formal_benchmark(
            manifest, self._output("profiles"), profile_runtime_factory=_FakeFactory()
        )
        self.assertEqual(report["overall_status"], "ERROR")
        self.assertEqual(report.get("error"), BLOCKER_MANIFEST_SCHEMA_INVALID)

    # ------------------------------------------------------------------
    # 3/4. Dataset / case hash against the ACTUAL files
    # ------------------------------------------------------------------

    def test_dataset_hash_mismatch_blocks(self) -> None:
        manifest = self.fixture.build()
        manifest["dataset_hash"] = "d" * 64
        report = run_formal_benchmark(
            manifest, self._output("dataset-hash"), profile_runtime_factory=_FakeFactory()
        )
        self.assertEqual(report["overall_status"], STATUS_BLOCKED)
        for profile in report["profiles"]:
            self.assertIn(BLOCKER_DATASET_HASH_MISMATCH, profile["blocker_codes"])

    def test_dataset_file_missing_blocks(self) -> None:
        manifest = self.fixture.build()
        manifest["dataset_path"] = str(self.tmp / "missing.jsonl")
        report = run_formal_benchmark(
            manifest, self._output("dataset-missing"), profile_runtime_factory=_FakeFactory()
        )
        self.assertEqual(report["overall_status"], STATUS_BLOCKED)
        for profile in report["profiles"]:
            self.assertIn("DATASET_UNAVAILABLE", profile["blocker_codes"])

    def test_case_set_hash_mismatch_blocks(self) -> None:
        manifest = self.fixture.build()
        manifest["case_set_hash"] = "c" * 64
        report = run_formal_benchmark(
            manifest, self._output("case-hash"), profile_runtime_factory=_FakeFactory()
        )
        self.assertEqual(report["overall_status"], STATUS_BLOCKED)
        for profile in report["profiles"]:
            self.assertIn(BLOCKER_CASE_SET_HASH_MISMATCH, profile["blocker_codes"])

    def test_candidate_count_mismatch_blocks(self) -> None:
        manifest = self.fixture.build()
        manifest["candidate_count"] = 99
        report = run_formal_benchmark(
            manifest, self._output("count"), profile_runtime_factory=_FakeFactory()
        )
        self.assertEqual(report["overall_status"], STATUS_BLOCKED)
        for profile in report["profiles"]:
            self.assertIn("CANDIDATE_COUNT_MISMATCH", profile["blocker_codes"])

    # ------------------------------------------------------------------
    # 5-9. Attestation gates
    # ------------------------------------------------------------------

    def test_runtime_attestation_binding_error_blocks(self) -> None:
        manifest = self.fixture.build()
        block = manifest["profiles"][0]
        block["product_runtime_attestation"] = self.fixture.attestations.runtime(
            profile_name="standard_rag",
            runtime_name="canonical-standard_rag-runtime",
            runtime_version="phase22-canonical-runtime-v1",
            corpus_snapshot_ref="corpus-snapshot:test:v1",
            security_epoch=self.fixture.security_epoch,
            forged=True,
        )
        report = run_formal_benchmark(
            manifest, self._output("runtime-att"), profile_runtime_factory=_FakeFactory()
        )
        self.assertEqual(report["overall_status"], STATUS_BLOCKED)
        self.assertIn(
            BLOCKER_RUNTIME_ATTESTATION_INVALID,
            report["profiles"][0]["blocker_codes"],
        )

    def test_credential_attestation_binding_error_blocks(self) -> None:
        manifest = self.fixture.build()
        manifest["formal_credential_attestation"] = {
            **manifest["formal_credential_attestation"],
            "attestation_hash": "e" * 64,
        }
        report = run_formal_benchmark(
            manifest, self._output("cred-att"), profile_runtime_factory=_FakeFactory()
        )
        self.assertEqual(report["overall_status"], STATUS_BLOCKED)
        for profile in report["profiles"]:
            self.assertIn(BLOCKER_MISSING_FORMAL_CREDENTIAL, profile["blocker_codes"])

    def test_reviewer_not_approved_blocks(self) -> None:
        manifest = self.fixture.build(reviewer_status="pending", benchmark_eligible=False)
        report = run_formal_benchmark(
            manifest, self._output("reviewer"), profile_runtime_factory=_FakeFactory()
        )
        self.assertEqual(report["overall_status"], STATUS_BLOCKED)
        for profile in report["profiles"]:
            self.assertIn(BLOCKER_REVIEWER_NOT_APPROVED, profile["blocker_codes"])

    def test_budget_not_approved_blocks(self) -> None:
        manifest = self.fixture.build()
        manifest["human_budget_approved"] = False
        report = run_formal_benchmark(
            manifest, self._output("budget"), profile_runtime_factory=_FakeFactory()
        )
        self.assertEqual(report["overall_status"], STATUS_BLOCKED)
        for profile in report["profiles"]:
            self.assertIn(BLOCKER_BUDGET_APPROVAL_MISSING, profile["blocker_codes"])

    def test_security_not_approved_blocks(self) -> None:
        manifest = self.fixture.build()
        manifest["formal_execution_approved"] = False
        report = run_formal_benchmark(
            manifest, self._output("security"), profile_runtime_factory=_FakeFactory()
        )
        self.assertEqual(report["overall_status"], STATUS_BLOCKED)
        for profile in report["profiles"]:
            self.assertIn(BLOCKER_SECURITY_APPROVAL_MISSING, profile["blocker_codes"])

    # ------------------------------------------------------------------
    # 10-12. Artifact hash / Git SHA / environment manifest
    # ------------------------------------------------------------------

    def test_artifact_hashes_present(self) -> None:
        manifest = self.fixture.build()
        output = self._output("hashes")
        run_formal_benchmark(
            manifest, output, profile_runtime_factory=_FakeFactory(state="RUNTIME_OBSERVED")
        )
        report = self._read_report(output)
        for profile_ref in report["artifact_refs"]["profiles"].values():
            self.assertEqual(len(profile_ref["sha256"]), 64)
        self.assertTrue((output / "profiles" / "standard_rag.json").exists())
        for profile in CANONICAL_PROFILES:
            artifact = self._read_artifact(output, profile)
            self.assertEqual(
                sha256_file(output / "profiles" / f"{profile}.json"),
                text_sha256(artifact),
            )

    def test_git_sha_in_environment(self) -> None:
        manifest = self.fixture.build()
        output = self._output("git")
        run_formal_benchmark(
            manifest, output, profile_runtime_factory=_FakeFactory(state="RUNTIME_OBSERVED")
        )
        report = self._read_report(output)
        self.assertTrue(report["environment"]["git_commit_sha"])
        self.assertIsInstance(report["environment"]["git_working_tree_dirty"], bool)

    def test_environment_manifest_present(self) -> None:
        manifest = self.fixture.build()
        output = self._output("env")
        run_formal_benchmark(
            manifest, output, profile_runtime_factory=_FakeFactory(state="RUNTIME_OBSERVED")
        )
        report = self._read_report(output)
        env = report["environment"]
        self.assertTrue(env["python_version"])
        self.assertTrue(env["platform"])
        self.assertEqual(env["manifest_version"], MANIFEST_VERSION)
        self.assertTrue((output / "environment.json").exists())

    # ------------------------------------------------------------------
    # 13. Rerun reproducibility
    # ------------------------------------------------------------------

    def test_rerun_reproducibility(self) -> None:
        manifest = self.fixture.build()
        out_a = self._output("rerun-a")
        out_b = self._output("rerun-b")
        run_formal_benchmark(
            manifest, out_a, profile_runtime_factory=_FakeFactory(state="RUNTIME_OBSERVED")
        )
        run_formal_benchmark(
            manifest, out_b, profile_runtime_factory=_FakeFactory(state="RUNTIME_OBSERVED")
        )
        report_a = self._read_report(out_a)
        report_b = self._read_report(out_b)
        self.assertEqual(report_a["overall_status"], report_b["overall_status"])
        for profile in CANONICAL_PROFILES:
            self.assertEqual(
                report_a["artifact_refs"]["profiles"][profile]["sha256"],
                report_b["artifact_refs"]["profiles"][profile]["sha256"],
            )
            self.assertEqual(
                sha256_file(out_a / "profiles" / f"{profile}.json"),
                sha256_file(out_b / "profiles" / f"{profile}.json"),
            )
        self.assertEqual(
            report_a["report_checksum_sidecar"], report_b["report_checksum_sidecar"]
        )

    # ------------------------------------------------------------------
    # 14. Profile-independent blockers
    # ------------------------------------------------------------------

    def test_one_blocked_profile_does_not_fake_others(self) -> None:
        manifest = self.fixture.build()
        factory = _FakeFactory(
            state="RUNTIME_OBSERVED", fail_profiles={"local_graphrag"}
        )
        output = self._output("independent")
        report = run_formal_benchmark(manifest, output, profile_runtime_factory=factory)
        by_profile = {p["profile_id"]: p for p in report["profiles"]}
        self.assertEqual(report["overall_status"], STATUS_BLOCKED)
        self.assertEqual(
            by_profile["local_graphrag"]["measurement_status"], STATUS_BLOCKED
        )
        self.assertIn(
            BLOCKER_PROFILE_RUNTIME_UNAVAILABLE,
            by_profile["local_graphrag"]["blocker_codes"],
        )
        # The other profiles keep their own honest status — never faked to
        # blocked, never promoted to measured.
        for name in ("standard_rag", "deep_graphrag", "agentic_graphrag"):
            self.assertEqual(
                by_profile[name]["measurement_status"], STATUS_RUNTIME_OBSERVED
            )
            self.assertEqual(by_profile[name]["blocker_codes"], [])

    # ------------------------------------------------------------------
    # 15/16. Test double / runtime observed can never become MEASURED
    # ------------------------------------------------------------------

    def test_test_double_cannot_be_measured(self) -> None:
        manifest = self.fixture.build()
        report = run_formal_benchmark(
            manifest,
            self._output("test-double"),
            profile_runtime_factory=_FakeFactory(state="MEASURED", is_test_double=True),
        )
        self.assertEqual(report["overall_status"], STATUS_BLOCKED)
        for profile in report["profiles"]:
            self.assertEqual(profile["measurement_status"], STATUS_BLOCKED)
            self.assertIn(BLOCKER_TEST_DOUBLE, profile["blocker_codes"])

    def test_runtime_observed_never_auto_promotes(self) -> None:
        manifest = self.fixture.build()
        output = self._output("observed")
        report = run_formal_benchmark(
            manifest, output, profile_runtime_factory=_FakeFactory(state="RUNTIME_OBSERVED")
        )
        self.assertEqual(report["overall_status"], STATUS_RUNTIME_OBSERVED)
        for profile in report["profiles"]:
            self.assertEqual(profile["measurement_status"], STATUS_RUNTIME_OBSERVED)

    # ------------------------------------------------------------------
    # 17/18. Aggregation semantics
    # ------------------------------------------------------------------

    def test_single_profile_measured_is_not_overall_measured(self) -> None:
        manifest = self.fixture.build()
        report = run_formal_benchmark(
            manifest,
            self._output("single-measured"),
            profile_runtime_factory=_FakeFactory(
                state="RUNTIME_OBSERVED",
                per_profile_override={"standard_rag": "MEASURED"},
            ),
        )
        # The single MEASURED profile has no measurement attestation -> it is
        # demoted to BLOCKED, and the overall run must never be MEASURED.
        self.assertNotEqual(report["overall_status"], STATUS_MEASURED)
        by_profile = {p["profile_id"]: p for p in report["profiles"]}
        self.assertEqual(
            by_profile["standard_rag"]["measurement_status"], STATUS_BLOCKED
        )
        self.assertIn(
            BLOCKER_MEASUREMENT_ATTESTATION_MISSING,
            by_profile["standard_rag"]["blocker_codes"],
        )

    def test_four_measured_but_incomparable_is_incomparable(self) -> None:
        manifest = self.fixture.build()
        rows = self.fixture.rows
        case_set_hash = self.fixture.case_set_hash
        # Make the deep profile incomparable: different corpus snapshot.
        manifest["profiles"][2]["corpus_snapshot_ref"] = "corpus-snapshot:test:OTHER"
        factory = _FakeFactory(state="MEASURED")
        attestations = _attestations_for(factory, manifest, rows, case_set_hash)
        output = self._output("incomparable")
        report = run_formal_benchmark(
            manifest, output, profile_runtime_factory=_FakeFactory(
                state="MEASURED", measurement_attestation=attestations
            ),
        )
        self.assertEqual(report["overall_status"], STATUS_INCOMPARABLE)

    # ------------------------------------------------------------------
    # 19. Measurement attestation missing / invalid
    # ------------------------------------------------------------------

    def test_measurement_attestation_missing_blocks(self) -> None:
        manifest = self.fixture.build()
        report = run_formal_benchmark(
            manifest,
            self._output("att-missing"),
            profile_runtime_factory=_FakeFactory(state="MEASURED"),
        )
        self.assertEqual(report["overall_status"], STATUS_BLOCKED)
        for profile in report["profiles"]:
            self.assertEqual(profile["measurement_status"], STATUS_BLOCKED)
            self.assertIn(
                BLOCKER_MEASUREMENT_ATTESTATION_MISSING, profile["blocker_codes"]
            )

    def test_measurement_attestation_invalid_blocks(self) -> None:
        manifest = self.fixture.build()
        forged = {
            "attestation_ref": "measurement-attestation:test:forged",
            "profile_id": "standard_rag",
            "measurement_status": "MEASURED",
            "artifact_hash": "a" * 64,
            "fingerprint_hash": "b" * 64,
            "evidence_ref": "evidence:forged",
            "measurement_attestation_contract_version": MEASUREMENT_ATTESTATION_VERSION,
            "attestation_hash": "f" * 64,
        }
        report = run_formal_benchmark(
            manifest,
            self._output("att-invalid"),
            profile_runtime_factory=_FakeFactory(
                state="MEASURED", measurement_attestation=forged
            ),
        )
        self.assertEqual(report["overall_status"], STATUS_BLOCKED)
        for profile in report["profiles"]:
            self.assertIn(
                BLOCKER_MEASUREMENT_ATTESTATION_INVALID, profile["blocker_codes"]
            )

    # ------------------------------------------------------------------
    # 20. Formal fixture happy path
    # ------------------------------------------------------------------

    def test_formal_fixture_happy_path(self) -> None:
        """A fully attested manifest with a measurement-owner factory yields
        four MEASURED profiles, comparable fingerprints, immutable artifacts
        and serialized measurement attestations."""
        manifest = self.fixture.build()
        rows = self.fixture.rows
        case_set_hash = self.fixture.case_set_hash
        factory = _FakeFactory(state="MEASURED")
        attestations = _attestations_for(factory, manifest, rows, case_set_hash)
        factory = _FakeFactory(state="MEASURED", measurement_attestation=attestations)
        output = self._output("happy")
        report = run_formal_benchmark(manifest, output, profile_runtime_factory=factory)

        self.assertEqual(report["overall_status"], STATUS_MEASURED)
        self.assertEqual(report["preflight"]["state"], "READY")
        for profile in report["profiles"]:
            self.assertEqual(profile["measurement_status"], STATUS_MEASURED)
            self.assertEqual(profile["blocker_codes"], [])
            self.assertTrue(profile["output_artifact_hash"])
            self.assertTrue(
                (output / profile["output_artifact_path"]).exists(),
                profile["output_artifact_path"],
            )
            attestation_ref = report["artifact_refs"]["profiles"][profile["profile_id"]][
                "measurement_attestation"
            ]
            self.assertIsNotNone(attestation_ref)
            attestation_path = output / attestation_ref["path"]
            self.assertTrue(attestation_path.exists())
            self.assertEqual(
                sha256_file(attestation_path), attestation_ref["sha256"]
            )
        # The attestation's artifact_hash binds to the facts artifact.
        facts = self._read_artifact(output, "standard_rag")
        self.assertEqual(text_sha256(facts), report["profiles"][0]["output_artifact_hash"])

    # ------------------------------------------------------------------
    # Output immutability / check-only
    # ------------------------------------------------------------------

    def test_output_immutable_refuses_overwrite(self) -> None:
        manifest = self.fixture.build()
        output = self._output("immutable")
        run_formal_benchmark(
            manifest, output, profile_runtime_factory=_FakeFactory(state="RUNTIME_OBSERVED")
        )
        report = run_formal_benchmark(
            manifest, output, profile_runtime_factory=_FakeFactory(state="RUNTIME_OBSERVED")
        )
        self.assertEqual(report["overall_status"], "ERROR")
        self.assertEqual(report.get("error"), "OUTPUT_PATH_EXISTS")

    def test_check_only_reports_ready_for_formal_execution(self) -> None:
        manifest = self.fixture.build()
        output = self._output("check-only")
        report = run_formal_benchmark(
            manifest, output, profile_runtime_factory=_FakeFactory(), check_only=True
        )
        self.assertEqual(report["overall_status"], "READY_FOR_FORMAL_EXECUTION")
        for profile in report["profiles"]:
            self.assertEqual(
                profile["measurement_status"], "READY_FOR_FORMAL_EXECUTION"
            )


if __name__ == "__main__":
    unittest.main()
