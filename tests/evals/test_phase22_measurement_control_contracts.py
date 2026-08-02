"""PHASE22 Measurement Control Contracts (cross-contract truth tests).

A small, deterministic suite proving the three control boundaries that the
merged PHASE22 governance base must hold simultaneously:

* Benchmark Preflight ``READY`` is a request-to-start verdict, never a
  ``MEASURED`` claim.
* Runtime Evidence Binding ``VALID`` is a binding-consistency verdict,
  never ``RUNTIME_OBSERVED`` or ``MEASURED``.
* The merged Release Decision stays ``BLOCKED`` while formal measurement
  facts are absent, no matter how complete the preflight surface is.
* ``runtime_evidence_binding``, ``benchmark_preflight`` and the merged
  ``release_decision`` import together on the current governance base
  without circular dependencies; the merged Release Decision engine
  remains independent of the two control modules.

No network, no models, no credentials, no real benchmark runs.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src" / "backend"))

from tools.evals.zuno.rag_eval.benchmark_preflight import (  # noqa: E402
    CANONICAL_PROFILES,
    FORMAL_CREDENTIAL_ATTESTATION_VERSION,
    PRODUCT_RUNTIME_ATTESTATION_VERSION,
    STATE_READY,
    compute_formal_credential_attestation_hash,
    compute_product_runtime_attestation_hash,
    evaluate_payload,
)
from tools.evals.zuno.rag_eval.release_decision import (  # noqa: E402
    FINGERPRINT_DIMENSIONS,
    REQUIRED_PROFILE_IDS,
    ReleaseDecisionStatus,
    evaluate_release_decision,
)
from tools.evals.zuno.rag_eval.runtime_evidence_binding import (  # noqa: E402
    BindingValidationState,
    RECEIPT_OWNERS,
    RuntimeEvidenceBindingValidator,
    compute_reference_binding_hash,
)

# Statuses this control surface must NEVER emit: they would be claims of
# observed runtime execution, completed measurement or proven quality that
# no deterministic control contract is allowed to make.
NEVER_CLAIMED = frozenset(
    {"RUNTIME_OBSERVED", "MEASURED", "QUALITY_PROVEN", "PRODUCTION_READY"}
)


def _sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _valid_preflight_payload() -> dict:
    """A complete 11-gate READY preflight payload (no runtime execution)."""
    def profile_payload(name: str) -> dict:
        attestation = {
            "attestation_ref": f"attestation://phase22/{name}",
            "profile_name": name,
            "runtime_name": f"{name}-runtime",
            "runtime_version": "1.0.0",
            "corpus_snapshot_ref": "snapshot-2026-08-01",
            "security_epoch": "epoch-2026-Q3",
            "formal_adapter_ref": f"canonical-adapter://phase22/{name}",
            "runtime_evidence_contract_version": PRODUCT_RUNTIME_ATTESTATION_VERSION,
        }
        attestation["attestation_hash"] = compute_product_runtime_attestation_hash(
            attestation
        )
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
            "product_runtime_attestation": attestation,
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

    profiles = [profile_payload(name) for name in CANONICAL_PROFILES]
    formal_credential_attestation = {
        "attestation_ref": "attestation://phase22/formal-credential/eval-run-2026-08-01",
        "eval_run_id": "eval-run-2026-08-01",
        "credential_ref": "vault://preflight/credentials",
        "authorization_ref": "auth-ref-001",
        "security_epoch": "epoch-2026-Q3",
        "formal_execution_ref": "formal-execution://phase22/eval-run-2026-08-01",
        "formal_credential_contract_version": FORMAL_CREDENTIAL_ATTESTATION_VERSION,
    }
    formal_credential_attestation["attestation_hash"] = (
        compute_formal_credential_attestation_hash(formal_credential_attestation)
    )
    return {
        "eval_run_id": "eval-run-2026-08-01",
        "case_set_ref": "case-set-2026-08",
        "dataset_version": "dataset-v1",
        "dataset_hash": "0" * 64,
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
        "formal_credential_attestation": formal_credential_attestation,
        "output_artifact_ref": "s3://zuno-preflight/eval-run-2026-08-01.json",
        "profiles": profiles,
    }


def _valid_binding() -> dict:
    """A fully self-consistent VALID runtime evidence binding (no run)."""
    receipts = []
    refs = {
        "security_decision": "sd-1",
        "trace": "trace-1",
        "usage_receipt": "usage-1",
        "budget_settlement": "budget-1",
        "artifact_receipt": "artifact-1",
    }
    for receipt_type, ref in refs.items():
        receipts.append(
            {
                "receipt_type": receipt_type,
                "receipt_ref": ref,
                "owner": RECEIPT_OWNERS[receipt_type],
                "runtime_version": "rt-1.0",
                "snapshot_ref": "snapshot_v1",
                "payload_hash": _sha256_hex(ref),
            }
        )
    binding = {
        "eval_run_id": "eval-run-1",
        "case_id": "case-1",
        "requested_profile": "standard_rag",
        "actual_profile": "standard_rag",
        "runtime_name": "canonical-standard-runtime",
        "runtime_version": "rt-1.0",
        "corpus_snapshot_ref": "snapshot_v1",
        "trace_id": "trace-1",
        "security_decision_ref": "sd-1",
        "plan_version_ref": "",
        "run_outcome_ref": "",
        "usage_receipt_ref": "usage-1",
        "budget_settlement_ref": "budget-1",
        "artifact_receipt_ref": "artifact-1",
        "artifact_payload_hash": _sha256_hex("artifact-payload"),
        "result_payload_hash": _sha256_hex("result-payload"),
        "reference_binding_hash": "0" * 64,
        "receipts": receipts,
    }
    binding["reference_binding_hash"] = compute_reference_binding_hash(binding)
    return binding


def _fingerprint() -> dict:
    base = {dimension: "fingerprint-v1" for dimension in FINGERPRINT_DIMENSIONS}
    base["graph_snapshot"] = None
    return base


def _no_measurement_facts_payload() -> dict:
    """Release Decision input with profiles but no formal measurement facts:
    every profile declares NOT_MEASURED and no measurement gate block is
    supplied.
    """
    profiles = {}
    for profile_id in REQUIRED_PROFILE_IDS:
        profiles[profile_id] = {
            "profile_id": profile_id,
            "measurement_status": "NOT_MEASURED",
            "artifact": {
                "artifact_hash": "hash:profile",
                "manifest_hash": "manifest:profile",
            },
            "failure_buckets": [],
            "evidence_ref": "evidence:profile",
            "evaluation": {"ok": True},
            "fingerprint": _fingerprint(),
        }
    return {"profiles": profiles, "comparability_fingerprint": _fingerprint()}


# ── Cross-contract truths ──────────────────────────────────────────────────


def test_preflight_ready_is_not_measured():
    report = evaluate_payload(_valid_preflight_payload())
    assert report.state == STATE_READY
    # READY is a request-to-start verdict: it must not carry any claim that
    # measurement happened.
    assert report.state not in NEVER_CLAIMED
    for code in report.gap_codes:
        assert code not in NEVER_CLAIMED


def test_runtime_binding_valid_is_not_runtime_observed_or_measured():
    result = RuntimeEvidenceBindingValidator().validate(_valid_binding())
    assert result.state is BindingValidationState.VALID
    # The binding contract's states are exactly the four control states.
    assert {s.value for s in BindingValidationState} == {
        "VALID",
        "BLOCKED",
        "INCOMPARABLE",
        "INVALID",
    }
    assert NEVER_CLAIMED.isdisjoint(BindingValidationState.__members__)
    for code in result.gap_codes:
        assert code not in NEVER_CLAIMED


def test_release_decision_stays_blocked_without_measurement_facts():
    decision = evaluate_release_decision(_no_measurement_facts_payload())
    assert decision.status is ReleaseDecisionStatus.BLOCKED
    assert decision.reason_codes
    # The preflight surface being complete must not flip the decision: the
    # decision engine stays BLOCKED while formal measurement facts are
    # absent, and it never claims measurement.
    assert decision.status.value not in NEVER_CLAIMED


def test_release_decision_engine_does_not_import_control_modules():
    source = (
        ROOT / "tools" / "evals" / "zuno" / "rag_eval" / "release_decision.py"
    ).read_text(encoding="utf-8")
    # No import statement may reference the two control modules; docstring
    # mentions are allowed.
    for line in source.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(("import ", "from ")):
            assert "runtime_evidence_binding" not in line
            assert "benchmark_preflight" not in line


def test_three_modules_import_together_in_fresh_interpreter():
    # A fresh interpreter proves there is no circular import between the
    # three modules on the current governance base.
    code = (
        "import sys\n"
        f"sys.path.insert(0, {str(ROOT)!r})\n"
        f"sys.path.insert(0, {str(ROOT / 'src' / 'backend')!r})\n"
        "import tools.evals.zuno.rag_eval.runtime_evidence_binding\n"
        "import tools.evals.zuno.rag_eval.benchmark_preflight\n"
        "import tools.evals.zuno.rag_eval.release_decision\n"
        "print('imports-ok')\n"
    )
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    assert "imports-ok" in proc.stdout


def test_three_results_never_claim_measurement_or_observed():
    preflight = evaluate_payload(_valid_preflight_payload())
    binding = RuntimeEvidenceBindingValidator().validate(_valid_binding())
    decision = evaluate_release_decision(_no_measurement_facts_payload())
    for result in (preflight.state, binding.state.value, decision.status.value):
        assert result not in NEVER_CLAIMED
    # READY / VALID stay request-level or binding-level verdicts while the
    # decision engine remains BLOCKED for the same surface.
    assert preflight.state == STATE_READY
    assert binding.state is BindingValidationState.VALID
    assert decision.status is ReleaseDecisionStatus.BLOCKED
