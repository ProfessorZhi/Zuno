"""Tests for the PHASE22 Runtime Evidence Binding Contract (validation only).

Covers all contract scenarios:
- four-profile VALID cases
- unknown / missing / mismatched profiles
- missing runtime identity, snapshot, trace
- agentic plan_version / run_outcome requirements
- missing / duplicate / unknown / unbound / mismatched receipts
- receipt owner, runtime version and snapshot consistency
- payload hash format (short / long / non-hex / uppercase)
- reference binding hash contract (order independence, field sensitivity,
  gold and secret exclusion)
- determinism, gap code ordering, multi-error returns
- input immutability and the neutrality of is_test_double / authority claims

Owner strings are never duplicated here: tests read the owner map from the
module under test, which is the single source of truth.
"""

from __future__ import annotations

import copy
import hashlib
from typing import Any

import pytest

from tools.evals.zuno.rag_eval.runtime_evidence_binding import (
    ALLOWED_PROFILES,
    BindingValidationResult,
    BindingValidationState,
    RECEIPT_OWNERS,
    REF_FIELD_BY_RECEIPT_TYPE,
    REQUIRED_RECEIPTS,
    RuntimeEvidenceBinding,
    RuntimeEvidenceBindingValidator,
    compute_reference_binding_hash,
)

VALIDATOR = RuntimeEvidenceBindingValidator()


def _sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _receipt(
    receipt_type: str,
    *,
    ref: str,
    version: str = "rt-1.0",
    snapshot: str = "snapshot_v1",
    owner: str | None = None,
    payload_hash: str | None = None,
) -> dict[str, str]:
    base: dict[str, str] = {
        "receipt_type": receipt_type,
        "receipt_ref": ref,
        "owner": RECEIPT_OWNERS[receipt_type] if owner is None else owner,
        "runtime_version": version,
        "snapshot_ref": snapshot,
        "payload_hash": payload_hash if payload_hash is not None else _sha256_hex(ref),
    }
    return base


def make_binding(**overrides: Any) -> dict[str, Any]:
    """Fully valid standard_rag binding; overrides applied before the
    reference binding hash is (re)computed, so results stay self-consistent.
    """
    base: dict[str, Any] = {
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
        "receipts": [
            _receipt("security_decision", ref="sd-1"),
            _receipt("trace", ref="trace-1"),
            _receipt("usage_receipt", ref="usage-1"),
            _receipt("budget_settlement", ref="budget-1"),
            _receipt("artifact_receipt", ref="artifact-1"),
        ],
    }
    base.update(overrides)
    if "reference_binding_hash" not in overrides:
        try:
            base["reference_binding_hash"] = compute_reference_binding_hash(base)
        except (TypeError, ValueError):
            # Structurally broken input: stage 1 reports before hash checks.
            pass
    return base


def make_agentic_binding(**overrides: Any) -> dict[str, Any]:
    """Fully valid agentic_graphrag binding (all seven receipts)."""
    base = make_binding(
        requested_profile="agentic_graphrag",
        actual_profile="agentic_graphrag",
        runtime_name="canonical-agentic-runtime",
        plan_version_ref="pv-1",
        run_outcome_ref="ro-1",
    )
    base.update(overrides)
    base["receipts"] = [
        _receipt("security_decision", ref="sd-1"),
        _receipt("plan_version", ref="pv-1"),
        _receipt("run_outcome", ref="ro-1"),
        _receipt("usage_receipt", ref="usage-1"),
        _receipt("budget_settlement", ref="budget-1"),
        _receipt("trace", ref="trace-1"),
        _receipt("artifact_receipt", ref="artifact-1"),
    ]
    if "reference_binding_hash" not in overrides:
        try:
            base["reference_binding_hash"] = compute_reference_binding_hash(base)
        except (TypeError, ValueError):
            pass
    return base


def _drop_receipt(
    binding: dict[str, Any], receipt_type: str
) -> dict[str, Any]:
    """Remove a receipt (keeping its top-level reference) and rebind the hash."""
    binding = dict(binding)
    binding["receipts"] = [
        r for r in binding["receipts"] if r["receipt_type"] != receipt_type
    ]
    binding["reference_binding_hash"] = compute_reference_binding_hash(binding)
    return binding


def _rehash(binding: dict[str, Any]) -> dict[str, Any]:
    binding["reference_binding_hash"] = compute_reference_binding_hash(binding)
    return binding


# ── Four-profile VALID cases ──────────────────────────────────────────────


def test_valid_standard_rag_binding():
    result = VALIDATOR.validate(make_binding())
    assert result.state is BindingValidationState.VALID
    assert result.gap_codes == ()
    assert result.valid


def test_valid_local_graphrag_binding():
    binding = make_binding(
        requested_profile="local_graphrag",
        actual_profile="local_graphrag",
        runtime_name="canonical-local-runtime",
    )
    result = VALIDATOR.validate(binding)
    assert result.state is BindingValidationState.VALID
    assert result.gap_codes == ()


def test_valid_deep_graphrag_binding():
    binding = make_binding(
        requested_profile="deep_graphrag",
        actual_profile="deep_graphrag",
        runtime_name="canonical-deep-runtime",
    )
    result = VALIDATOR.validate(binding)
    assert result.state is BindingValidationState.VALID
    assert result.gap_codes == ()


def test_valid_agentic_graphrag_binding():
    result = VALIDATOR.validate(make_agentic_binding())
    assert result.state is BindingValidationState.VALID
    assert result.gap_codes == ()


def test_deep_graphrag_plan_version_not_forced():
    # The repository contract provides no evidence that PlanVersion is
    # mandatory for deep_graphrag, so a deep binding without it is VALID.
    binding = make_binding(
        requested_profile="deep_graphrag",
        actual_profile="deep_graphrag",
        runtime_name="canonical-deep-runtime",
    )
    assert VALIDATOR.validate(binding).state is BindingValidationState.VALID


def test_extra_known_receipt_fully_bound_is_valid():
    # A known non-required receipt (plan_version) is allowed on standard_rag
    # when it is bound one-to-one with a non-empty top-level reference.
    binding = _rehash(
        dict(
            make_binding(plan_version_ref="pv-1"),
            receipts=make_binding()["receipts"]
            + [_receipt("plan_version", ref="pv-1")],
        )
    )
    assert VALIDATOR.validate(binding).state is BindingValidationState.VALID


# ── Profile handling ──────────────────────────────────────────────────────


def test_unknown_requested_profile():
    result = VALIDATOR.validate(make_binding(requested_profile="super_rag"))
    assert result.state is BindingValidationState.INVALID
    assert result.gap_codes == ("unknown_requested_profile",)


def test_unknown_actual_profile():
    result = VALIDATOR.validate(make_binding(actual_profile="super_rag"))
    assert result.state is BindingValidationState.INVALID
    assert result.gap_codes == ("unknown_actual_profile",)


def test_requested_profile_missing():
    result = VALIDATOR.validate(make_binding(requested_profile=""))
    assert result.state is BindingValidationState.INVALID
    assert result.gap_codes == ("requested_profile_missing",)


def test_profile_mismatch():
    result = VALIDATOR.validate(
        make_binding(requested_profile="standard_rag", actual_profile="local_graphrag")
    )
    assert result.state is BindingValidationState.INCOMPARABLE
    assert result.gap_codes == ("profile_mismatch",)


# ── Runtime identity / snapshot / trace ───────────────────────────────────


def test_runtime_name_missing():
    result = VALIDATOR.validate(make_binding(runtime_name=""))
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == ("runtime_name_missing",)


def test_runtime_version_missing():
    result = VALIDATOR.validate(make_binding(runtime_version=""))
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == ("runtime_version_missing",)


def test_corpus_snapshot_ref_missing():
    result = VALIDATOR.validate(make_binding(corpus_snapshot_ref=""))
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == ("corpus_snapshot_ref_missing",)


def test_trace_id_missing():
    result = VALIDATOR.validate(make_binding(trace_id=""))
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == ("trace_id_missing", "receipt_ref_unbound:trace")


# ── Agentic plan_version / run_outcome requirements ───────────────────────


def test_agentic_plan_version_ref_missing():
    binding = make_agentic_binding(plan_version_ref="")
    binding = _drop_receipt(binding, "plan_version")
    result = VALIDATOR.validate(binding)
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == (
        "plan_version_ref_missing",
        "plan_version_receipt_missing",
    )


def test_agentic_plan_version_receipt_missing():
    binding = make_agentic_binding()
    binding = dict(binding)
    binding["receipts"] = [
        r for r in binding["receipts"] if r["receipt_type"] != "plan_version"
    ]
    binding = _rehash(binding)
    result = VALIDATOR.validate(binding)
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == (
        "plan_version_receipt_missing",
        "plan_version_ref_unbound",
    )


def test_agentic_run_outcome_ref_missing():
    binding = make_agentic_binding(run_outcome_ref="")
    binding = _drop_receipt(binding, "run_outcome")
    result = VALIDATOR.validate(binding)
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == (
        "run_outcome_ref_missing",
        "run_outcome_receipt_missing",
    )


def test_agentic_run_outcome_receipt_missing():
    binding = make_agentic_binding()
    binding = dict(binding)
    binding["receipts"] = [
        r for r in binding["receipts"] if r["receipt_type"] != "run_outcome"
    ]
    binding = _rehash(binding)
    result = VALIDATOR.validate(binding)
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == (
        "run_outcome_receipt_missing",
        "run_outcome_ref_unbound",
    )


# ── Missing required receipts ─────────────────────────────────────────────


def test_usage_receipt_missing():
    result = VALIDATOR.validate(_drop_receipt(make_binding(), "usage_receipt"))
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == (
        "usage_receipt_missing",
        "usage_receipt_ref_unbound",
    )


def test_budget_settlement_missing():
    result = VALIDATOR.validate(_drop_receipt(make_binding(), "budget_settlement"))
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == (
        "budget_settlement_missing",
        "budget_settlement_ref_unbound",
    )


def test_artifact_receipt_missing():
    result = VALIDATOR.validate(_drop_receipt(make_binding(), "artifact_receipt"))
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == (
        "artifact_receipt_missing",
        "artifact_receipt_ref_unbound",
    )


def test_trace_receipt_missing():
    result = VALIDATOR.validate(_drop_receipt(make_binding(), "trace"))
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == ("trace_receipt_missing", "trace_ref_unbound")


def test_security_decision_receipt_missing():
    result = VALIDATOR.validate(_drop_receipt(make_binding(), "security_decision"))
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == (
        "security_decision_receipt_missing",
        "security_decision_ref_unbound",
    )


# ── Receipt consistency (owner / version / snapshot) ──────────────────────


def test_receipt_owner_mismatch():
    binding = make_binding()
    receipts = list(binding["receipts"])
    receipts[2] = dict(
        receipts[2],
        owner=f"{RECEIPT_OWNERS['usage_receipt']}_claimed",
    )
    binding["receipts"] = receipts
    result = VALIDATOR.validate(_rehash(binding))
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == ("receipt_owner_mismatch:usage_receipt",)


def test_receipt_runtime_version_mismatch():
    binding = make_binding()
    binding["receipts"] = [
        r if r["receipt_type"] != "usage_receipt" else dict(r, runtime_version="rt-9.9")
        for r in binding["receipts"]
    ]
    result = VALIDATOR.validate(_rehash(binding))
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == ("receipt_runtime_version_mismatch:usage_receipt",)


def test_receipt_snapshot_mismatch():
    binding = make_binding()
    binding["receipts"] = [
        r if r["receipt_type"] != "usage_receipt" else dict(r, snapshot_ref="snapshot_other")
        for r in binding["receipts"]
    ]
    result = VALIDATOR.validate(_rehash(binding))
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == ("receipt_snapshot_mismatch:usage_receipt",)


def test_local_graphrag_index_snapshot_uncovered():
    # The local_graphrag graph index is covered by the top-level binding: the
    # artifact receipt must carry the corpus snapshot. No index receipt type
    # exists or is invented.
    binding = make_binding(
        requested_profile="local_graphrag",
        actual_profile="local_graphrag",
        runtime_name="canonical-local-runtime",
    )
    binding["receipts"] = [
        dict(r, snapshot_ref="snapshot_other")
        if r["receipt_type"] == "artifact_receipt"
        else r
        for r in binding["receipts"]
    ]
    result = VALIDATOR.validate(_rehash(binding))
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == ("local_graphrag_index_snapshot_uncovered",)


# ── Payload hash format ───────────────────────────────────────────────────


def test_hash_too_short():
    result = VALIDATOR.validate(make_binding(artifact_payload_hash="a" * 63))
    assert result.state is BindingValidationState.INVALID
    assert result.gap_codes == ("artifact_payload_hash_invalid",)


def test_hash_too_long():
    result = VALIDATOR.validate(make_binding(result_payload_hash="a" * 65))
    assert result.state is BindingValidationState.INVALID
    assert result.gap_codes == ("result_payload_hash_invalid",)


def test_hash_non_hex():
    binding = make_binding()
    binding["receipts"] = [
        dict(r, payload_hash="z" * 64)
        if r["receipt_type"] == "usage_receipt"
        else r
        for r in binding["receipts"]
    ]
    result = VALIDATOR.validate(_rehash(binding))
    assert result.state is BindingValidationState.INVALID
    assert result.gap_codes == ("receipt_payload_hash_invalid:usage_receipt",)


def test_uppercase_hash_rejected():
    # Fail-closed: uppercase SHA-256 hex is rejected, never normalized.
    result = VALIDATOR.validate(make_binding(artifact_payload_hash="A" * 64))
    assert result.state is BindingValidationState.INVALID
    assert result.gap_codes == ("artifact_payload_hash_invalid",)


def test_reference_binding_hash_missing():
    result = VALIDATOR.validate(make_binding(reference_binding_hash=""))
    assert result.state is BindingValidationState.INVALID
    assert result.gap_codes == ("reference_binding_hash_missing",)


def test_reference_binding_hash_invalid_format():
    result = VALIDATOR.validate(make_binding(reference_binding_hash="Z" * 64))
    assert result.state is BindingValidationState.INVALID
    assert result.gap_codes == ("reference_binding_hash_invalid",)


def test_reference_binding_hash_mismatch():
    result = VALIDATOR.validate(make_binding(reference_binding_hash="1" * 64))
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == ("reference_binding_hash_mismatch",)


# ── Reference binding hash contract ───────────────────────────────────────


def test_hash_field_order_independent():
    binding = make_binding()
    keys = list(binding.keys())
    reordered = {k: binding[k] for k in [keys[-1]] + keys[:-1]}
    assert compute_reference_binding_hash(reordered) == compute_reference_binding_hash(
        binding
    )
    result = VALIDATOR.validate(reordered)
    assert result.state is BindingValidationState.VALID


def test_receipt_list_order_does_not_affect_hash():
    binding = make_binding()
    binding["receipts"] = list(reversed(binding["receipts"]))
    assert compute_reference_binding_hash(binding) == compute_reference_binding_hash(
        make_binding()
    )
    assert VALIDATOR.validate(binding).state is BindingValidationState.VALID


@pytest.mark.parametrize(
    "field,value",
    [
        ("case_id", "case-other"),
        ("runtime_name", "other-runtime"),
        ("runtime_version", "rt-2.0"),
        ("corpus_snapshot_ref", "snapshot_v2"),
        ("trace_id", "trace-other"),
        ("usage_receipt_ref", "usage-other"),
        ("result_payload_hash", _sha256_hex("other-result")),
    ],
)
def test_any_binding_field_change_changes_hash(field: str, value: str):
    assert compute_reference_binding_hash(
        make_binding(**{field: value})
    ) != compute_reference_binding_hash(make_binding())


def test_receipt_field_change_changes_hash():
    binding = make_binding()
    receipts = list(binding["receipts"])
    receipts[2] = dict(receipts[2], snapshot_ref="snapshot_other")
    binding["receipts"] = receipts
    binding = _rehash(binding)
    assert compute_reference_binding_hash(binding) != compute_reference_binding_hash(
        make_binding()
    )


def test_tenant_id_changes_hash_when_provided():
    with_tenant = make_binding(tenant_id="tenant-1")
    without_tenant = make_binding()
    assert compute_reference_binding_hash(with_tenant) != compute_reference_binding_hash(
        without_tenant
    )
    assert VALIDATOR.validate(with_tenant).state is BindingValidationState.VALID


def test_gold_fields_do_not_enter_hash():
    binding = make_binding()
    binding["gold_document_refs"] = ["gold-doc-1", "gold-doc-2"]
    binding["gold_evidence_refs"] = ["gold-evidence-1"]
    binding["expected_answer"] = "the expected answer"
    binding["citation_ground_truth"] = ["cite-1"]
    assert compute_reference_binding_hash(binding) == compute_reference_binding_hash(
        make_binding()
    )
    result = VALIDATOR.validate(binding)
    assert result.state is BindingValidationState.VALID


def test_secret_does_not_enter_hash():
    binding = make_binding()
    binding["secret_api_key"] = "sk-prod-0123456789"
    binding["access_token"] = "tok-abcdef"
    assert compute_reference_binding_hash(binding) == compute_reference_binding_hash(
        make_binding()
    )
    result = VALIDATOR.validate(binding)
    assert result.state is BindingValidationState.VALID


# ── Determinism, multi-error, immutability ────────────────────────────────


def test_input_object_is_not_modified():
    binding = make_binding()
    before = copy.deepcopy(binding)
    VALIDATOR.validate(binding)
    assert binding == before

    invalid = make_binding(runtime_version="")
    before = copy.deepcopy(invalid)
    VALIDATOR.validate(invalid)
    assert invalid == before


def test_multiple_errors_in_stage_returned_together():
    result = VALIDATOR.validate(
        make_binding(runtime_name="", runtime_version="")
    )
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == ("runtime_name_missing", "runtime_version_missing")


def test_multiple_errors_across_stages_in_priority_order():
    binding = make_binding(runtime_name="")
    binding["receipts"] = [
        dict(r, owner=f"{RECEIPT_OWNERS[r['receipt_type']]}_claimed")
        if r["receipt_type"] == "usage_receipt"
        else r
        for r in binding["receipts"]
    ]
    binding["result_payload_hash"] = "not-a-hash"
    result = VALIDATOR.validate(_rehash(binding))
    assert result.state is BindingValidationState.BLOCKED  # stage 4 wins
    assert result.gap_codes == (
        "runtime_name_missing",
        "receipt_owner_mismatch:usage_receipt",
        "result_payload_hash_invalid",
    )


def test_gap_code_order_is_stable_and_deterministic():
    binding = make_binding(runtime_name="", runtime_version="", trace_id="")
    first = VALIDATOR.validate(binding)
    second = VALIDATOR.validate(binding)
    assert first.state is second.state
    assert first.gap_codes == second.gap_codes
    assert first.gap_codes == (
        "runtime_name_missing",
        "runtime_version_missing",
        "trace_id_missing",
        "receipt_ref_unbound:trace",
    )


# ── Claimed authority must not influence the result ───────────────────────


def test_is_test_double_false_has_no_effect():
    claimed = make_binding(is_test_double=False)
    plain = make_binding()
    result = VALIDATOR.validate(claimed)
    assert result.state is BindingValidationState.VALID
    assert result.gap_codes == VALIDATOR.validate(plain).gap_codes


def test_magic_authority_field_has_no_effect():
    claimed = make_binding(
        __zuno_product_authority__={
            "level": "product",
            "signed": True,
            "issuer": "runtime",
        }
    )
    plain = make_binding()
    result = VALIDATOR.validate(claimed)
    assert result.state is BindingValidationState.VALID
    assert result.gap_codes == VALIDATOR.validate(plain).gap_codes


# ── Input structure ───────────────────────────────────────────────────────


def test_input_type_invalid():
    assert VALIDATOR.validate(object()).gap_codes == ("input_type_invalid",)
    assert VALIDATOR.validate("not-a-binding").gap_codes == ("input_type_invalid",)
    assert VALIDATOR.validate([1, 2, 3]).gap_codes == ("input_type_invalid",)


def test_input_field_missing_absent_key():
    binding = make_binding()
    del binding["case_id"]
    result = VALIDATOR.validate(binding)
    assert result.state is BindingValidationState.INVALID
    assert result.gap_codes == ("input_field_missing:case_id",)


def test_input_field_wrong_type():
    result = VALIDATOR.validate(make_binding(runtime_version=123))
    assert result.state is BindingValidationState.INVALID
    assert result.gap_codes == ("input_field_wrong_type:runtime_version",)


def test_receipts_not_list():
    result = VALIDATOR.validate(make_binding(receipts="not-a-list"))
    assert result.state is BindingValidationState.INVALID
    assert result.gap_codes == ("input_field_wrong_type:receipts",)


def test_input_receipt_not_mapping():
    binding = make_binding()
    binding["receipts"] = ["not-a-receipt"]
    result = VALIDATOR.validate(binding)
    assert result.state is BindingValidationState.INVALID
    assert result.gap_codes == ("input_receipt_not_mapping",)


def test_receipt_field_missing():
    binding = make_binding()
    binding["receipts"] = [dict(r) for r in binding["receipts"]]
    del binding["receipts"][2]["owner"]
    result = VALIDATOR.validate(binding)
    assert result.state is BindingValidationState.INVALID
    assert result.gap_codes == ("receipt_field_missing:owner",)


# ── Receipt reference binding (one-to-one) ────────────────────────────────


def test_receipt_ref_duplicate():
    binding = make_binding(
        usage_receipt_ref="shared-1",
        budget_settlement_ref="shared-1",
    )
    binding["receipts"] = [
        _receipt("usage_receipt", ref="shared-1"),
        _receipt("budget_settlement", ref="shared-1"),
        _receipt("security_decision", ref="sd-1"),
        _receipt("trace", ref="trace-1"),
        _receipt("artifact_receipt", ref="artifact-1"),
    ]
    result = VALIDATOR.validate(_rehash(binding))
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == ("receipt_ref_duplicate",)


def test_receipt_type_duplicate():
    binding = make_binding()
    binding["receipts"] = list(binding["receipts"]) + [
        _receipt("usage_receipt", ref="usage-2")
    ]
    result = VALIDATOR.validate(_rehash(binding))
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == (
        "receipt_type_duplicate:usage_receipt",
        "receipt_ref_mismatch:usage_receipt",
    )


def test_unknown_receipt_type():
    binding = make_binding()
    binding["receipts"] = list(binding["receipts"]) + [
        {
            "receipt_type": "fake_receipt",
            "receipt_ref": "fake-1",
            "owner": "nobody",
            "runtime_version": "rt-1.0",
            "snapshot_ref": "snapshot_v1",
            "payload_hash": _sha256_hex("fake"),
        }
    ]
    result = VALIDATOR.validate(_rehash(binding))
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == ("unknown_receipt_type:fake_receipt",)


def test_receipt_ref_missing():
    binding = make_binding()
    binding["receipts"] = [
        dict(r, receipt_ref="") if r["receipt_type"] == "usage_receipt" else r
        for r in binding["receipts"]
    ]
    result = VALIDATOR.validate(_rehash(binding))
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == (
        "receipt_ref_missing:usage_receipt",
        "receipt_ref_mismatch:usage_receipt",
    )


def test_top_level_ref_unbound_without_receipt():
    # Top-level plan_version_ref is non-empty on standard_rag but no
    # plan_version receipt exists: the reference is unbound.
    result = VALIDATOR.validate(make_binding(plan_version_ref="pv-1"))
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == ("plan_version_ref_unbound",)


def test_receipt_unbound_without_top_level_ref():
    binding = make_binding()
    binding["receipts"] = list(binding["receipts"]) + [
        _receipt("plan_version", ref="pv-1")
    ]
    result = VALIDATOR.validate(_rehash(binding))
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == ("receipt_ref_unbound:plan_version",)


def test_receipt_ref_mismatch():
    binding = make_binding()
    binding["receipts"] = [
        dict(r, receipt_ref="usage-other")
        if r["receipt_type"] == "usage_receipt"
        else r
        for r in binding["receipts"]
    ]
    result = VALIDATOR.validate(_rehash(binding))
    assert result.state is BindingValidationState.BLOCKED
    assert result.gap_codes == ("receipt_ref_mismatch:usage_receipt",)


# ── Identity fields ───────────────────────────────────────────────────────


def test_eval_run_id_missing():
    result = VALIDATOR.validate(make_binding(eval_run_id=""))
    assert result.state is BindingValidationState.INVALID
    assert result.gap_codes == ("eval_run_id_missing",)


def test_case_id_missing():
    result = VALIDATOR.validate(make_binding(case_id=""))
    assert result.state is BindingValidationState.INVALID
    assert result.gap_codes == ("case_id_missing",)


# ── tenant_id / workspace_id (validated when present, never defaulted) ────


def test_tenant_id_empty_when_present():
    result = VALIDATOR.validate(make_binding(tenant_id=""))
    assert result.state is BindingValidationState.INVALID
    assert result.gap_codes == ("tenant_id_empty",)


def test_workspace_id_empty_when_present():
    result = VALIDATOR.validate(make_binding(workspace_id=""))
    assert result.state is BindingValidationState.INVALID
    assert result.gap_codes == ("workspace_id_empty",)


def test_tenant_workspace_absent_is_valid():
    # No invented default tenant / workspace: absence is simply not part of
    # the binding.
    result = VALIDATOR.validate(make_binding())
    assert result.state is BindingValidationState.VALID
    assert result.gap_codes == ()


def test_tenant_workspace_present_nonempty_is_valid():
    result = VALIDATOR.validate(make_binding(tenant_id="tenant-1", workspace_id="ws-1"))
    assert result.state is BindingValidationState.VALID


# ── API surface ───────────────────────────────────────────────────────────


def test_validate_accepts_dataclass_instance():
    binding = RuntimeEvidenceBinding.from_dict(make_binding())
    result = VALIDATOR.validate(binding)
    assert result.state is BindingValidationState.VALID


def test_dataclass_instance_absent_tenant_is_valid():
    binding = RuntimeEvidenceBinding.from_dict(make_binding())
    assert VALIDATOR.validate(binding).state is BindingValidationState.VALID


def test_valid_is_not_runtime_observed_or_measured():
    # This contract never produces RUNTIME_OBSERVED or MEASURED.
    assert [s.value for s in BindingValidationState] == [
        "VALID",
        "BLOCKED",
        "INCOMPARABLE",
        "INVALID",
    ]
    assert "RUNTIME_OBSERVED" not in BindingValidationState.__members__
    assert "MEASURED" not in BindingValidationState.__members__
    result = VALIDATOR.validate(make_binding())
    assert result.state is BindingValidationState.VALID
    assert result.gap_codes == ()


def test_owner_map_is_single_source_of_truth():
    assert set(RECEIPT_OWNERS) == set(REF_FIELD_BY_RECEIPT_TYPE)
    assert set(REQUIRED_RECEIPTS) == set(ALLOWED_PROFILES)
    for required in REQUIRED_RECEIPTS.values():
        assert set(required) <= set(RECEIPT_OWNERS)
    assert REF_FIELD_BY_RECEIPT_TYPE["trace"] == "trace_id"


def test_result_object_is_immutable():
    result = VALIDATOR.validate(make_binding())
    assert isinstance(result, BindingValidationResult)
    with pytest.raises(Exception):
        result.gap_codes = ("tampered",)  # type: ignore[misc]
