"""Tests for PHASE22 Benchmark Preflight Contract.

These tests cover the full evaluators and the CLI. They are deliberately
deterministic and do not require network, environment secrets, or any real
runtime object.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from typing import Any, Dict, List, Tuple


# ---------------------------------------------------------------------------
# Path setup so the package can be imported when pytest is run from the
# repo root.  conftest.py already adds the repo root to sys.path, so we
# import via the package path.
# ---------------------------------------------------------------------------

from tools.evals.zuno.rag_eval.benchmark_preflight import (  # noqa: E402
    BenchmarkPreflightEvaluator,
    BenchmarkPreflightReport,
    CANONICAL_PROFILES,
    ProfilePreflightInput,
    STATE_BLOCKED,
    STATE_INCOMPARABLE,
    STATE_INVALID,
    STATE_READY,
    evaluate_payload,
    report_to_dict,
)


_RAG_EVAL_TOOLS = os.path.join(
    "tools", "evals", "zuno", "rag_eval"
)


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------


def _zero_filled_sha256() -> str:
    return "0" * 64


def _valid_profile(name: str) -> Dict[str, Any]:
    return {
        "profile_name": name,
        "case_set_ref": "case-set-2026-08",
        "dataset_version": "dataset-v1",
        "corpus_snapshot_ref": "snapshot-2026-08-01",
        "security_epoch": "epoch-2026-Q3",
        "budget_policy_ref": "budget-policy-standard",
        "runtime_name": f"{name}-runtime",
        "runtime_version": "1.0.0",
        "product_runtime_attested": True,
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


def _valid_payload(profiles: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    return {
        "eval_run_id": "eval-run-2026-08-01",
        "case_set_ref": "case-set-2026-08",
        "dataset_version": "dataset-v1",
        "dataset_hash": _zero_filled_sha256(),
        "candidate_count": 12,
        "reviewer_status": "approved",
        "benchmark_eligible": True,
        "license_status": "verified",
        "integrity_status": "verified",
        "runtime_request_schema_gold_free": True,
        "authorization_ref": "auth-ref-001",
        "security_epoch": "epoch-2026-Q3",
        "security_epoch_stale": False,
        "formal_execution_approved": True,
        "human_budget_approved": True,
        "budget_policy_ref": "budget-policy-standard",
        "provider_cost_limit": 100.0,
        "token_limit": 1_000_000,
        "deadline": "2026-12-31T23:59:59Z",
        "credential_ref": "vault://preflight/credentials",
        "has_formal_credentials": True,
        "formal_execution_requested": True,
        "output_artifact_ref": "s3://zuno-preflight/eval-run-2026-08-01.json",
        "profiles": profiles
        if profiles is not None
        else [_valid_profile(name) for name in CANONICAL_PROFILES],
    }


def _evaluate(payload: Dict[str, Any]) -> BenchmarkPreflightReport:
    return BenchmarkPreflightEvaluator().evaluate(payload)


# ---------------------------------------------------------------------------
# 1. READY
# ---------------------------------------------------------------------------


class ReadyContractTests(unittest.TestCase):
    def test_01_full_ready_case(self) -> None:
        report = _evaluate(_valid_payload())
        self.assertEqual(report.state, STATE_READY)
        self.assertEqual(report.gap_codes, ())
        self.assertEqual(len(report.profile_results), len(CANONICAL_PROFILES))
        for pr in report.profile_results:
            self.assertEqual(pr.state, STATE_READY)
            self.assertEqual(pr.gap_codes, ())
        self.assertEqual(report.contract_version, "phase22-benchmark-preflight.v1")
        self.assertEqual(len(report.input_fingerprint), 64)

    def test_02_profile_input_order_does_not_change_state(self) -> None:
        ordered = _valid_payload()
        reordered_payload = _valid_payload(
            profiles=list(reversed(ordered["profiles"]))
        )
        report = _evaluate(ordered)
        reordered_report = _evaluate(reordered_payload)
        self.assertEqual(report.state, reordered_report.state)
        self.assertEqual(report.gap_codes, reordered_report.gap_codes)
        self.assertEqual(report.input_fingerprint, reordered_report.input_fingerprint)
        # Profile results are always in canonical order.
        self.assertEqual(
            [pr.profile_name for pr in report.profile_results],
            list(CANONICAL_PROFILES),
        )
        self.assertEqual(
            [pr.profile_name for pr in reordered_report.profile_results],
            list(CANONICAL_PROFILES),
        )

    def test_03_output_deterministic(self) -> None:
        payload = _valid_payload()
        dict_a = report_to_dict(_evaluate(payload))
        dict_b = report_to_dict(_evaluate(payload))
        self.assertEqual(dict_a, dict_b)

    def test_04_fingerprint_stable(self) -> None:
        a = _evaluate(_valid_payload()).input_fingerprint
        b = _evaluate(_valid_payload()).input_fingerprint
        self.assertEqual(a, b)
        self.assertEqual(len(a), 64)

    def test_05_same_input_yields_byte_identical_reports(self) -> None:
        # Build canonical JSON via the CLI path so we exercise the same
        # serialisation rules.
        with tempfile.TemporaryDirectory() as tmp:
            input_path = os.path.join(tmp, "in.json")
            output_a = os.path.join(tmp, "a.json")
            output_b = os.path.join(tmp, "b.json")
            with open(input_path, "w", encoding="utf-8") as handle:
                json.dump(_valid_payload(), handle, sort_keys=True)
            cli = os.path.join(_RAG_EVAL_TOOLS, "run_phase22_preflight.py")
            for out in (output_a, output_b):
                subprocess.run(
                    [sys.executable, cli, "--input", input_path, "--output", out],
                    check=True,
                )
            with open(output_a, "r", encoding="utf-8") as handle:
                a = handle.read()
            with open(output_b, "r", encoding="utf-8") as handle:
                b = handle.read()
            self.assertEqual(a, b)
            self.assertTrue(a.endswith("\n"))


# ---------------------------------------------------------------------------
# 2. Profile Set
# ---------------------------------------------------------------------------


class ProfileSetGateTests(unittest.TestCase):
    def _missing_payload(self, remove: str) -> Dict[str, Any]:
        payload = _valid_payload()
        payload["profiles"] = [
            p for p in payload["profiles"] if p["profile_name"] != remove
        ]
        return payload

    def test_06_missing_standard_rag(self) -> None:
        report = _evaluate(self._missing_payload("standard_rag"))
        self.assertEqual(report.state, STATE_INVALID)
        self.assertIn("profile_set_missing_standard_rag", report.gap_codes)

    def test_07_missing_local_graphrag(self) -> None:
        report = _evaluate(self._missing_payload("local_graphrag"))
        self.assertEqual(report.state, STATE_INVALID)
        self.assertIn("profile_set_missing_local_graphrag", report.gap_codes)

    def test_08_missing_deep_graphrag(self) -> None:
        report = _evaluate(self._missing_payload("deep_graphrag"))
        self.assertEqual(report.state, STATE_INVALID)
        self.assertIn("profile_set_missing_deep_graphrag", report.gap_codes)

    def test_09_missing_agentic_graphrag(self) -> None:
        report = _evaluate(self._missing_payload("agentic_graphrag"))
        self.assertEqual(report.state, STATE_INVALID)
        self.assertIn(
            "profile_set_missing_agentic_graphrag", report.gap_codes
        )

    def test_10_duplicate_profile(self) -> None:
        payload = _valid_payload()
        payload["profiles"].append(dict(payload["profiles"][0]))
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_INVALID)
        self.assertIn("profile_duplicate", report.gap_codes)

    def test_11_unknown_profile(self) -> None:
        payload = _valid_payload()
        payload["profiles"][0] = _valid_profile("mystery_profile")
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_INVALID)
        self.assertIn("profile_unknown", report.gap_codes)

    def test_12_extra_profile(self) -> None:
        payload = _valid_payload()
        payload["profiles"].append(_valid_profile("extras_rag"))
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_INVALID)
        self.assertIn("profile_unknown", report.gap_codes)

    def test_13_profiles_type_error(self) -> None:
        payload = _valid_payload()
        payload["profiles"] = "not-a-list"
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_INVALID)
        self.assertIn("profiles_not_a_list", report.gap_codes)


# ---------------------------------------------------------------------------
# 3. Comparability
# ---------------------------------------------------------------------------


class ComparabilityGateTests(unittest.TestCase):
    def _mutate(self, **mutations: Any) -> Dict[str, Any]:
        payload = _valid_payload()
        for profile in payload["profiles"]:
            for key, value in mutations.items():
                profile[key] = value
        return payload

    def test_14_case_set_ref_mismatch(self) -> None:
        payload = _valid_payload()
        payload["profiles"][0]["case_set_ref"] = "case-set-2026-07"
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_INCOMPARABLE)
        self.assertIn("case_set_mismatch", report.gap_codes)

    def test_15_dataset_version_mismatch(self) -> None:
        payload = _valid_payload()
        payload["profiles"][0]["dataset_version"] = "dataset-v2"
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_INCOMPARABLE)
        self.assertIn("dataset_version_mismatch", report.gap_codes)

    def test_16_corpus_snapshot_mismatch(self) -> None:
        payload = self._mutate(corpus_snapshot_ref="snapshot-other")
        payload["profiles"][0]["corpus_snapshot_ref"] = "snapshot-baseline"
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_INCOMPARABLE)
        self.assertIn("corpus_snapshot_mismatch", report.gap_codes)

    def test_17_security_epoch_mismatch(self) -> None:
        payload = _valid_payload()
        payload["profiles"][0]["security_epoch"] = "epoch-2026-Q1"
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_INCOMPARABLE)
        self.assertIn("security_epoch_mismatch", report.gap_codes)

    def test_18_budget_policy_mismatch(self) -> None:
        payload = _valid_payload()
        payload["profiles"][0]["budget_policy_ref"] = "budget-policy-other"
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_INCOMPARABLE)
        self.assertIn("budget_policy_mismatch", report.gap_codes)


# ---------------------------------------------------------------------------
# 4. Governance
# ---------------------------------------------------------------------------


class GovernanceGateTests(unittest.TestCase):
    def test_19_reviewer_pending(self) -> None:
        payload = _valid_payload()
        payload["reviewer_status"] = "pending"
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_BLOCKED)
        self.assertIn("reviewer_not_approved", report.gap_codes)

    def test_20_benchmark_not_eligible(self) -> None:
        payload = _valid_payload()
        payload["benchmark_eligible"] = False
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_BLOCKED)
        self.assertIn("benchmark_not_eligible", report.gap_codes)

    def test_21_license_pending(self) -> None:
        payload = _valid_payload()
        payload["license_status"] = "pending"
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_BLOCKED)
        self.assertIn("license_not_verified", report.gap_codes)

    def test_22_integrity_review_required(self) -> None:
        payload = _valid_payload()
        payload["integrity_status"] = "review_required"
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_BLOCKED)
        self.assertIn("integrity_not_verified", report.gap_codes)


# ---------------------------------------------------------------------------
# 5. Dataset and Snapshot
# ---------------------------------------------------------------------------


class DatasetGateTests(unittest.TestCase):
    def test_23_invalid_sha256(self) -> None:
        payload = _valid_payload()
        payload["dataset_hash"] = "not-a-real-hash"
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_INVALID)
        self.assertIn("input_type_invalid_dataset_hash", report.gap_codes)

    def test_24_candidate_count_zero(self) -> None:
        payload = _valid_payload()
        payload["candidate_count"] = 0
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_INVALID)
        self.assertIn("input_type_invalid_candidate_count", report.gap_codes)

    def test_25_snapshot_missing(self) -> None:
        payload = _valid_payload()
        payload["profiles"][0]["corpus_snapshot_ref"] = ""
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_BLOCKED)
        self.assertIn("corpus_snapshot_missing", report.gap_codes)


# ---------------------------------------------------------------------------
# 6. Gold Firewall
# ---------------------------------------------------------------------------


class GoldFirewallGateTests(unittest.TestCase):
    def test_26_field_removed(self) -> None:
        payload = _valid_payload()
        del payload["runtime_request_schema_gold_free"]
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_INVALID)
        self.assertIn(
            "input_missing_runtime_request_schema_gold_free",
            report.gap_codes,
        )

    def test_27_false_means_blocked(self) -> None:
        payload = _valid_payload()
        payload["runtime_request_schema_gold_free"] = False
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_BLOCKED)
        self.assertIn("gold_firewall_not_proven", report.gap_codes)

    def test_28_true_means_ready(self) -> None:
        payload = _valid_payload()
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_READY)
        self.assertNotIn("gold_firewall_not_proven", report.gap_codes)


# ---------------------------------------------------------------------------
# 7. Runtime Gate
# ---------------------------------------------------------------------------


class RuntimeGateTests(unittest.TestCase):
    def test_29_product_attestation_false(self) -> None:
        payload = _valid_payload()
        for profile in payload["profiles"]:
            profile["product_runtime_attested"] = False
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_BLOCKED)
        self.assertIn("product_runtime_not_attested", report.gap_codes)

    def test_30_adapter_unwired(self) -> None:
        payload = _valid_payload()
        for profile in payload["profiles"]:
            profile["formal_adapter_wired"] = False
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_BLOCKED)
        self.assertIn("runtime_adapter_unwired", report.gap_codes)

    def test_31_runtime_name_missing(self) -> None:
        payload = _valid_payload()
        for profile in payload["profiles"]:
            profile["runtime_name"] = ""
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_BLOCKED)
        self.assertIn("runtime_name_missing", report.gap_codes)

    def test_32_runtime_version_missing(self) -> None:
        payload = _valid_payload()
        for profile in payload["profiles"]:
            profile["runtime_version"] = ""
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_BLOCKED)
        self.assertIn("runtime_version_missing", report.gap_codes)

    def test_33_knowledge_runtime_unavailable(self) -> None:
        payload = _valid_payload()
        for profile in payload["profiles"]:
            profile["knowledge_runtime_available"] = False
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_BLOCKED)
        self.assertIn("knowledge_runtime_unavailable", report.gap_codes)

    def test_34_local_index_runtime_missing(self) -> None:
        payload = _valid_payload()
        for profile in payload["profiles"]:
            if profile["profile_name"] == "local_graphrag":
                profile["index_runtime_available"] = False
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_BLOCKED)
        self.assertIn("index_runtime_unavailable", report.gap_codes)

    def test_35_agentic_agent_run_runtime_missing(self) -> None:
        payload = _valid_payload()
        for profile in payload["profiles"]:
            if profile["profile_name"] == "agentic_graphrag":
                profile["agent_run_runtime_available"] = False
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_BLOCKED)
        self.assertIn("agent_run_runtime_unavailable", report.gap_codes)

    def test_36_trace_adapter_unavailable(self) -> None:
        payload = _valid_payload()
        for profile in payload["profiles"]:
            profile["trace_adapter_available"] = False
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_BLOCKED)
        self.assertIn("trace_adapter_unavailable", report.gap_codes)

    def test_37_result_store_unavailable(self) -> None:
        payload = _valid_payload()
        for profile in payload["profiles"]:
            profile["result_store_available"] = False
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_BLOCKED)
        self.assertIn("result_store_unavailable", report.gap_codes)

    def test_38_artifact_store_unavailable(self) -> None:
        payload = _valid_payload()
        for profile in payload["profiles"]:
            profile["artifact_store_available"] = False
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_BLOCKED)
        self.assertIn("artifact_store_unavailable", report.gap_codes)

    def test_39_usage_receipt_provider_unavailable(self) -> None:
        payload = _valid_payload()
        for profile in payload["profiles"]:
            profile["usage_receipt_provider_available"] = False
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_BLOCKED)
        self.assertIn("usage_receipt_provider_unavailable", report.gap_codes)

    def test_40_budget_settlement_provider_unavailable(self) -> None:
        payload = _valid_payload()
        for profile in payload["profiles"]:
            profile["budget_settlement_provider_available"] = False
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_BLOCKED)
        self.assertIn(
            "budget_settlement_provider_unavailable", report.gap_codes
        )


# ---------------------------------------------------------------------------
# 8. Security
# ---------------------------------------------------------------------------


class SecurityGateTests(unittest.TestCase):
    def test_41_authorization_ref_missing(self) -> None:
        payload = _valid_payload()
        payload["authorization_ref"] = ""
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_INVALID)
        self.assertIn("input_type_invalid_authorization_ref", report.gap_codes)

    def test_42_security_epoch_missing(self) -> None:
        payload = _valid_payload()
        payload["security_epoch"] = ""
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_INVALID)
        self.assertIn("input_type_invalid_security_epoch", report.gap_codes)

    def test_43_security_epoch_stale(self) -> None:
        payload = _valid_payload()
        payload["security_epoch_stale"] = True
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_BLOCKED)
        self.assertIn("security_epoch_stale", report.gap_codes)

    def test_44_formal_execution_approval_missing(self) -> None:
        payload = _valid_payload()
        payload["formal_execution_approved"] = False
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_BLOCKED)
        self.assertIn("formal_execution_not_approved", report.gap_codes)


# ---------------------------------------------------------------------------
# 9. Budget
# ---------------------------------------------------------------------------


class BudgetGateTests(unittest.TestCase):
    def test_45_human_budget_not_approved(self) -> None:
        payload = _valid_payload()
        payload["human_budget_approved"] = False
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_BLOCKED)
        self.assertIn("human_budget_not_approved", report.gap_codes)

    def test_46_budget_policy_ref_missing(self) -> None:
        payload = _valid_payload()
        payload["budget_policy_ref"] = ""
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_INVALID)
        self.assertIn("input_type_invalid_budget_policy_ref", report.gap_codes)

    def test_47_cost_limit_zero_is_invalid(self) -> None:
        payload = _valid_payload()
        payload["provider_cost_limit"] = 0
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_INVALID)
        self.assertIn(
            "input_type_invalid_provider_cost_limit", report.gap_codes
        )

    def test_48_cost_limit_nan_is_invalid(self) -> None:
        # NaN is not valid JSON; raw JSON cannot represent it. We rely on
        # the underlying Python float typing: the evaluator detects NaN
        # via math.isfinite.
        payload = _valid_payload()
        payload["provider_cost_limit"] = float("nan")
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_INVALID)
        self.assertIn(
            "input_type_invalid_provider_cost_limit", report.gap_codes
        )

    def test_49_cost_limit_infinity_is_invalid(self) -> None:
        payload = _valid_payload()
        payload["provider_cost_limit"] = float("inf")
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_INVALID)
        self.assertIn(
            "input_type_invalid_provider_cost_limit", report.gap_codes
        )

    def test_50_token_limit_zero_is_invalid(self) -> None:
        payload = _valid_payload()
        payload["token_limit"] = 0
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_INVALID)
        self.assertIn("input_type_invalid_token_limit", report.gap_codes)

    def test_51_deadline_missing(self) -> None:
        payload = _valid_payload()
        payload["deadline"] = ""
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_INVALID)
        self.assertIn("input_type_invalid_deadline", report.gap_codes)


# ---------------------------------------------------------------------------
# 10. Credentials
# ---------------------------------------------------------------------------


class CredentialsGateTests(unittest.TestCase):
    def test_52_credential_ref_missing(self) -> None:
        payload = _valid_payload()
        payload["credential_ref"] = ""
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_INVALID)
        self.assertIn("input_type_invalid_credential_ref", report.gap_codes)

    def test_53_formal_credentials_false(self) -> None:
        payload = _valid_payload()
        payload["has_formal_credentials"] = False
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_BLOCKED)
        self.assertIn("formal_credentials_missing", report.gap_codes)

    def test_54_formal_execution_requested_false(self) -> None:
        payload = _valid_payload()
        payload["formal_execution_requested"] = False
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_BLOCKED)
        self.assertIn("formal_execution_not_requested", report.gap_codes)


# ---------------------------------------------------------------------------
# 11. CLI
# ---------------------------------------------------------------------------


class CliContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp()
        self.input_path = os.path.join(self.tmp, "in.json")
        self.output_path = os.path.join(self.tmp, "out.json")
        self.cli = os.path.join(_RAG_EVAL_TOOLS, "run_phase22_preflight.py")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, payload: Dict[str, Any]) -> Tuple[int, str, str]:
        with open(self.input_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, sort_keys=True)
        proc = subprocess.run(
            [sys.executable, self.cli, "--input", self.input_path, "--output", self.output_path],
            capture_output=True,
            text=True,
        )
        return proc.returncode, proc.stdout, proc.stderr

    def _read_output(self) -> Dict[str, Any]:
        with open(self.output_path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def test_55_ready_exit_zero(self) -> None:
        rc, _, _ = self._run(_valid_payload())
        self.assertEqual(rc, 0)
        report = self._read_output()
        self.assertEqual(report["state"], STATE_READY)

    def test_56_blocked_exit_two(self) -> None:
        payload = _valid_payload()
        payload["reviewer_status"] = "pending"
        rc, _, _ = self._run(payload)
        self.assertEqual(rc, 2)
        report = self._read_output()
        self.assertEqual(report["state"], STATE_BLOCKED)
        self.assertIn("reviewer_not_approved", report["gap_codes"])

    def test_57_incomparable_exit_three(self) -> None:
        payload = _valid_payload()
        payload["profiles"][0]["security_epoch"] = "epoch-2026-Q1"
        rc, _, _ = self._run(payload)
        self.assertEqual(rc, 3)
        report = self._read_output()
        self.assertEqual(report["state"], STATE_INCOMPARABLE)
        self.assertIn("security_epoch_mismatch", report["gap_codes"])

    def test_58_invalid_exit_four(self) -> None:
        payload = _valid_payload()
        del payload["runtime_request_schema_gold_free"]
        rc, _, _ = self._run(payload)
        self.assertEqual(rc, 4)
        report = self._read_output()
        self.assertEqual(report["state"], STATE_INVALID)

    def test_59_invalid_json(self) -> None:
        with open(self.input_path, "w", encoding="utf-8") as handle:
            handle.write("{not valid json}")
        proc = subprocess.run(
            [sys.executable, self.cli, "--input", self.input_path, "--output", self.output_path],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 4)
        self.assertNotIn("Traceback", proc.stderr)
        self.assertEqual(proc.stderr.strip(), "preflight: input_invalid_json")

    def test_60_input_file_missing(self) -> None:
        missing = os.path.join(self.tmp, "does-not-exist.json")
        output_missing = os.path.join(self.tmp, "out.json")
        proc = subprocess.run(
            [sys.executable, self.cli, "--input", missing, "--output", output_missing],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 4)
        self.assertNotIn("Traceback", proc.stderr)
        self.assertEqual(
            proc.stderr.strip(), "preflight: input_file_not_found"
        )

    def test_61_output_dir_created(self) -> None:
        nested = os.path.join(self.tmp, "deep", "nested", "out.json")
        with open(self.input_path, "w", encoding="utf-8") as handle:
            json.dump(_valid_payload(), handle, sort_keys=True)
        proc = subprocess.run(
            [sys.executable, self.cli, "--input", self.input_path, "--output", nested],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(os.path.exists(nested))

    def test_62_output_ends_with_newline(self) -> None:
        with open(self.input_path, "w", encoding="utf-8") as handle:
            json.dump(_valid_payload(), handle, sort_keys=True)
        subprocess.run(
            [sys.executable, self.cli, "--input", self.input_path, "--output", self.output_path],
            check=True,
        )
        with open(self.output_path, "rb") as handle:
            data = handle.read()
        self.assertTrue(data.endswith(b"\n"))

    def test_63_output_does_not_contain_secrets(self) -> None:
        payload = _valid_payload()
        payload["credential_ref"] = "vault://preflight/credentials"
        with open(self.input_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, sort_keys=True)
        subprocess.run(
            [sys.executable, self.cli, "--input", self.input_path, "--output", self.output_path],
            check=True,
        )
        with open(self.output_path, "r", encoding="utf-8") as handle:
            text = handle.read()
        self.assertNotIn("sk-prod-secret", text)
        # The report schema does not surface credential_ref content even
        # when the input contains it.
        self.assertNotIn("vault://preflight/credentials", text)

    def test_64_input_file_not_modified(self) -> None:
        with open(self.input_path, "w", encoding="utf-8") as handle:
            json.dump(_valid_payload(), handle, sort_keys=True)
        with open(self.input_path, "rb") as handle:
            before = handle.read()
        subprocess.run(
            [sys.executable, self.cli, "--input", self.input_path, "--output", self.output_path],
            check=True,
        )
        with open(self.input_path, "rb") as handle:
            after = handle.read()
        self.assertEqual(before, after)

    def test_65_same_input_byte_identical_output(self) -> None:
        with open(self.input_path, "w", encoding="utf-8") as handle:
            json.dump(_valid_payload(), handle, sort_keys=True)
        out_a = os.path.join(self.tmp, "a.json")
        out_b = os.path.join(self.tmp, "b.json")
        for out in (out_a, out_b):
            subprocess.run(
                [sys.executable, self.cli, "--input", self.input_path, "--output", out],
                check=True,
            )
        with open(out_a, "rb") as handle:
            a = handle.read()
        with open(out_b, "rb") as handle:
            b = handle.read()
        self.assertEqual(a, b)


# ---------------------------------------------------------------------------
# Extras: gate priority, fingerprint independence, schema integrity
# ---------------------------------------------------------------------------


class GatePriorityTests(unittest.TestCase):
    def test_comparability_failure_does_not_get_masked_by_reviewer_pending(
        self,
    ) -> None:
        # Comparability gate has higher priority than governance gate, so
        # this should fail with INCOMPARABLE, not BLOCKED.
        payload = _valid_payload()
        payload["profiles"][0]["case_set_ref"] = "case-set-2026-07"
        payload["reviewer_status"] = "pending"
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_INCOMPARABLE)
        self.assertIn("case_set_mismatch", report.gap_codes)

    def test_input_structure_takes_priority_over_comparability(self) -> None:
        payload = _valid_payload()
        payload["profiles"][0]["case_set_ref"] = "case-set-2026-07"
        payload["candidate_count"] = -1
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_INVALID)
        self.assertIn(
            "input_type_invalid_candidate_count", report.gap_codes
        )

    def test_fingerprint_does_not_change_on_profile_reorder(self) -> None:
        payload = _valid_payload()
        a = _evaluate(payload).input_fingerprint
        payload["profiles"] = list(reversed(payload["profiles"]))
        b = _evaluate(payload).input_fingerprint
        self.assertEqual(a, b)

    def test_fingerprint_changes_on_field_change(self) -> None:
        a = _evaluate(_valid_payload()).input_fingerprint
        payload = _valid_payload()
        payload["candidate_count"] = 99
        b = _evaluate(payload).input_fingerprint
        self.assertNotEqual(a, b)

    def test_unknown_top_level_field_is_invalid(self) -> None:
        payload = _valid_payload()
        payload["secret_consumer_token"] = "sk-prod-secret"
        report = _evaluate(payload)
        self.assertEqual(report.state, STATE_INVALID)
        self.assertIn("input_unknown_field", report.gap_codes)

    def test_input_not_object_is_invalid(self) -> None:
        report = evaluate_payload(["not", "a", "dict"])
        self.assertEqual(report.state, STATE_INVALID)
        self.assertIn("input_not_object", report.gap_codes)


if __name__ == "__main__":
    unittest.main()
