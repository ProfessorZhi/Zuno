from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from zuno.platform.contracts import (
    ContractRegistryEntry,
    ContractVersion,
    CrossModuleEnvelopeV1,
    FailureCodeV1,
    FailureOwner,
    PreparedToolActionV1,
    build_wave1_contract_registry,
    canonical_sha256,
)
from zuno.platform.contracts.shared import EffectReceiptV1, IndexWriteReceiptV1


def _now() -> datetime:
    return datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)


def test_contract_registry_rejects_duplicate_versions_and_unknown_major() -> None:
    registry = build_wave1_contract_registry()
    entry = registry.get("CrossModuleEnvelopeV1", "1.0")
    assert entry.owner_module == "Infrastructure"
    assert entry.schema_hash
    with pytest.raises(ValueError, match="unsupported major"):
        registry.get("CrossModuleEnvelopeV1", "2.0")
    with pytest.raises(ValueError, match="duplicate contract version"):
        type(registry)([entry, entry])


def test_bundle_manifest_hash_is_stable() -> None:
    registry = build_wave1_contract_registry()
    first = registry.manifest()
    second = build_wave1_contract_registry().manifest()
    assert first.bundle_hash == second.bundle_hash
    assert len(first.entries) >= 15
    assert {entry.contract_name for entry in first.entries} >= {
        "CrossModuleEnvelopeV1",
        "PreparedToolActionV1",
        "EffectReconciliationV1",
        "AuditPersistenceReceiptV1",
    }


def test_cross_module_envelope_hash_and_payload_boundary() -> None:
    payload = {"b": 2, "a": 1}
    envelope = CrossModuleEnvelopeV1(
        contract_name="RuntimeRequest",
        contract_version="1.0",
        contract_bundle_version="2026.07.wave1",
        message_id="msg-1",
        producer_module="Product Surface",
        consumer_module="Agent Core",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        correlation_id="corr-1",
        trace_id="trace-1",
        data_classification="internal",
        occurred_at=_now(),
        created_at=_now(),
        payload=payload,
        payload_hash=canonical_sha256(payload),
        payload_schema_hash="schema-hash",
    )
    assert envelope.payload == payload
    with pytest.raises(ValidationError, match="exactly one"):
        CrossModuleEnvelopeV1(
            **{
                **envelope.model_dump(),
                "payload_ref": "object://payload",
            }
        )
    with pytest.raises(ValidationError, match="payload_hash"):
        CrossModuleEnvelopeV1(**{**envelope.model_dump(), "payload_hash": "bad"})


def test_prepared_tool_action_hash_excludes_runtime_identity() -> None:
    base = {
        "prepared_tool_action_id": "pta-1",
        "action_proposal_ref": "proposal-1",
        "tenant_id": "tenant-a",
        "workspace_id": "workspace-a",
        "principal_context_ref": "principal-1",
        "tool_definition_ref": "tool.send_email",
        "tool_definition_version": "1",
        "operation": "send",
        "canonical_args_ref": "object://args",
        "canonical_args_hash": "args-hash",
        "target_resource_refs_hash": "target-hash",
        "side_effect_class": "EXTERNAL_WRITE",
        "credential_scope_ref": "credential-scope",
        "idempotency_scope": "run:step:tool",
        "policy_snapshot_ref": "policy-1",
        "effective_security_epoch_ref": "epoch-1",
        "effective_security_epoch_hash": "epoch-hash",
        "deadline_at": _now(),
        "canonical_hash_version": "v1",
        "status": "PREPARED",
    }
    expected_hash = canonical_sha256(
        {
            "canonical_hash_version": "v1",
            "tenant_id": "tenant-a",
            "workspace_id": "workspace-a",
            "principal_context_ref": "principal-1",
            "tool_definition_ref": "tool.send_email",
            "tool_definition_version": "1",
            "operation": "send",
            "canonical_args_hash": "args-hash",
            "target_resource_refs_hash": "target-hash",
            "side_effect_class": "EXTERNAL_WRITE",
            "credential_scope_ref": "credential-scope",
            "idempotency_scope": "run:step:tool",
            "policy_snapshot_ref": "policy-1",
            "effective_security_epoch_hash": "epoch-hash",
            "deadline_at": "2026-07-15T12:00:00Z",
        }
    )
    action = PreparedToolActionV1(**{**base, "prepared_action_hash": expected_hash})
    changed_identity = PreparedToolActionV1(**{**base, "prepared_tool_action_id": "pta-2", "prepared_action_hash": expected_hash})
    assert action.prepared_action_hash == changed_identity.prepared_action_hash
    with pytest.raises(ValidationError, match="prepared_action_hash"):
        PreparedToolActionV1(**{**base, "operation": "delete", "prepared_action_hash": expected_hash})


def test_failure_code_prefix_owner_is_fail_closed() -> None:
    failure = FailureCodeV1(
        code="TOOL_EFFECT_UNKNOWN",
        owner=FailureOwner.TOOL_RUNTIME,
        recovery_owner=FailureOwner.TOOL_RUNTIME,
        requires_reconcile=True,
    )
    assert failure.requires_reconcile is True
    with pytest.raises(ValidationError, match="owner prefix"):
        FailureCodeV1(
            code="SEC_STALE_EPOCH",
            owner=FailureOwner.TOOL_RUNTIME,
            recovery_owner=FailureOwner.SECURITY,
        )


def test_receipts_are_not_interchangeable_domain_success() -> None:
    effect_schema = EffectReceiptV1.model_json_schema()
    index_schema = IndexWriteReceiptV1.model_json_schema()
    assert effect_schema["title"] == "EffectReceiptV1"
    assert index_schema["title"] == "IndexWriteReceiptV1"
    assert "effect_state" in effect_schema["properties"]
    assert "status" in index_schema["properties"]
    assert "effect_state" not in index_schema["properties"]


def test_same_contract_version_with_different_schema_hash_is_rejected() -> None:
    entry = build_wave1_contract_registry().get("CrossModuleEnvelopeV1", "1.0")
    conflicting = ContractRegistryEntry(
        contract_name=entry.contract_name,
        version=ContractVersion(major=1, minor=0),
        schema_hash="different",
        owner_module=entry.owner_module,
    )
    with pytest.raises(ValueError, match="duplicate contract version"):
        type(build_wave1_contract_registry())([entry, conflicting])
