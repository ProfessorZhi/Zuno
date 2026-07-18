from __future__ import annotations

from datetime import datetime, timezone
from typing import get_args

from pydantic import ValidationError

from zuno.platform.contracts import (
    ActionExecutionBindingV1,
    ActionProposalV1,
    AuditPersistenceReceiptV1,
    EffectReceiptV1,
    IndexWriteBatchV1,
    IndexWriteReceiptV1,
    KnowledgeVersionRefV1,
    PreparedToolActionV1,
    SecurityApprovalDecisionV1,
    WriteVisibilityReceiptV1,
    build_wave1_contract_registry,
    canonical_sha256,
)


def _now() -> datetime:
    return datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)


def _entry(contract_name: str):
    return build_wave1_contract_registry().get(contract_name, "1.0")


def _literal_values(model: type, field_name: str) -> set[str]:
    return set(get_args(model.model_fields[field_name].annotation))


def _prepared_action_payload() -> dict[str, object]:
    return {
        "canonical_hash_version": "v1",
        "tenant_id": "tenant-a",
        "workspace_id": "workspace-a",
        "principal_context_ref": "principal-context-ref",
        "tool_definition_ref": "tool.email.send",
        "tool_definition_version": "2026.07",
        "operation": "send",
        "canonical_args_hash": "args-hash",
        "target_resource_refs_hash": "target-resource-hash",
        "side_effect_class": "EXTERNAL_WRITE",
        "credential_scope_ref": "credential-scope-ref",
        "idempotency_scope": "run:step:tool",
        "policy_snapshot_ref": "policy-snapshot-ref",
        "effective_security_epoch_hash": "security-epoch-hash",
        "deadline_at": _now().isoformat().replace("+00:00", "Z"),
    }


def _prepared_action_hash() -> str:
    return canonical_sha256(_prepared_action_payload())


def _prepared_action() -> PreparedToolActionV1:
    return PreparedToolActionV1(
        prepared_tool_action_id="prepared-action-1",
        action_proposal_ref="proposal-1",
        canonical_args_ref="object://canonical-args",
        effective_security_epoch_ref="effective-security-epoch-ref",
        prepared_action_hash=_prepared_action_hash(),
        status="PREPARED",
        **_prepared_action_payload(),
    )


def verify_phase04_contract_ownership_boundaries() -> list[str]:
    errors: list[str] = []

    registry = build_wave1_contract_registry()
    manifest_names = {entry.contract_name for entry in registry.manifest().entries}
    required_contracts = {
        "IndexWriteBatchV1",
        "IndexWriteReceiptV1",
        "WriteVisibilityReceiptV1",
        "KnowledgeVersionRefV1",
        "ActionProposalV1",
        "ActionExecutionBindingV1",
        "PreparedToolActionV1",
        "EffectReceiptV1",
        "AuditPersistenceReceiptV1",
        "SecurityApprovalDecisionV1",
    }
    missing_contracts = sorted(required_contracts - manifest_names)
    if missing_contracts:
        errors.append(f"contract registry missing entries: {missing_contracts!r}")

    index_batch = IndexWriteBatchV1(
        batch_id="index-batch-1",
        build_run_id="build-run-1",
        owner_module="KNOWLEDGE",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        index_kind="VECTOR",
        target_version="knowledge-index-v1",
        source_snapshot_ref="source-snapshot-ref",
        item_identity_scheme="source-chunk-id",
        item_count=10,
        payload_ref="object://index-payload",
        payload_hash="payload-hash",
        schema_spec_ref="schema-spec-ref",
        idempotency_key="index-batch-idempotency",
        expected_generation=7,
        effective_security_epoch_ref="effective-security-epoch-ref",
        deadline_at=_now(),
    )
    index_receipt = IndexWriteReceiptV1(
        receipt_id="index-write-receipt-1",
        batch_id=index_batch.batch_id,
        physical_target_ref="milvus://collection/partition",
        attempt_no=1,
        accepted_count=10,
        rejected_count=0,
        observed_generation=index_batch.expected_generation,
        service_commit_ref="milvus-commit-ref",
        checksum_or_digest="checksum",
        status="COMMITTED",
    )
    visibility_receipt = WriteVisibilityReceiptV1(
        receipt_id="visibility-receipt-1",
        write_receipt_ref=index_receipt.receipt_id,
        consistency_class="BOUNDED_EVENTUAL",
        visibility_deadline_at=_now(),
        serving_watermark_ref="serving-watermark-ref",
        status="PENDING",
    )
    knowledge_version = KnowledgeVersionRefV1(
        knowledge_version_ref="knowledge-version-1",
        knowledge_space_id="knowledge-space-a",
        source_snapshot_ref=index_batch.source_snapshot_ref,
        index_manifest_hash="domain-owned-index-manifest-hash",
        visibility_receipt_ref=visibility_receipt.receipt_id,
    )

    if index_batch.owner_module not in {"KNOWLEDGE", "MEMORY"}:
        errors.append("index batch owner is not a domain owner")
    if index_receipt.observed_generation != index_batch.expected_generation:
        errors.append("index receipt generation does not bind to expected generation")
    if not visibility_receipt.consistency_class:
        errors.append("visibility receipt has silent consistency")
    if not visibility_receipt.visibility_deadline_at:
        errors.append("visibility receipt has no deadline")
    if not knowledge_version.index_manifest_hash:
        errors.append("KnowledgeVersionRefV1 lacks domain-owned index manifest")
    if knowledge_version.visibility_receipt_ref != visibility_receipt.receipt_id:
        errors.append("KnowledgeVersionRefV1 is not bound to visibility receipt")

    index_receipt_statuses = _literal_values(IndexWriteReceiptV1, "status")
    forbidden_acceptance_terms = {"ACCEPTED", "SERVING", "DOMAIN_ACCEPTED"}
    if index_receipt_statuses.intersection(forbidden_acceptance_terms):
        errors.append("IndexWriteReceiptV1 can claim domain acceptance")
    visibility_statuses = _literal_values(WriteVisibilityReceiptV1, "status")
    if "VISIBLE" not in visibility_statuses or "FAILED" not in visibility_statuses:
        errors.append("WriteVisibilityReceiptV1 lacks explicit visibility outcomes")

    expected_owners = {
        "IndexWriteBatchV1": "Knowledge/Memory",
        "IndexWriteReceiptV1": "Infrastructure",
        "WriteVisibilityReceiptV1": "Infrastructure",
        "KnowledgeVersionRefV1": "Knowledge",
        "ActionProposalV1": "Agent Core",
        "ActionExecutionBindingV1": "Agent Core",
        "PreparedToolActionV1": "Tool Runtime",
        "EffectReceiptV1": "Tool Runtime",
        "AuditPersistenceReceiptV1": "Infrastructure",
        "SecurityApprovalDecisionV1": "Security",
    }
    for contract_name, owner in expected_owners.items():
        actual_owner = _entry(contract_name).owner_module
        if actual_owner != owner:
            errors.append(
                f"{contract_name} owner mismatch: expected={owner!r} actual={actual_owner!r}"
            )

    if (
        _entry("PreparedToolActionV1").owner_module
        == _entry("ActionProposalV1").owner_module
    ):
        errors.append("PreparedToolActionV1 overlaps Agent Core action proposal owner")
    if (
        _entry("PreparedToolActionV1").owner_module
        == _entry("AuditPersistenceReceiptV1").owner_module
    ):
        errors.append("PreparedToolActionV1 overlaps Infrastructure audit owner")
    if (
        _entry("PreparedToolActionV1").owner_module
        == _entry("SecurityApprovalDecisionV1").owner_module
    ):
        errors.append("PreparedToolActionV1 overlaps Security approval owner")

    try:
        _prepared_action()
    except ValidationError as exc:
        errors.append(f"PreparedToolActionV1 canonical hash was rejected: {exc}")

    try:
        PreparedToolActionV1(
            **{
                **_prepared_action().model_dump(),
                "operation": "delete",
                "prepared_action_hash": _prepared_action_hash(),
            }
        )
        errors.append("PreparedToolActionV1 accepted a stale canonical hash")
    except ValidationError:
        pass

    for model in [
        ActionProposalV1,
        ActionExecutionBindingV1,
        PreparedToolActionV1,
        EffectReceiptV1,
        AuditPersistenceReceiptV1,
    ]:
        if not model.model_json_schema().get("title"):
            errors.append(f"{model.__name__} schema title is missing")

    return errors


def main() -> int:
    errors = verify_phase04_contract_ownership_boundaries()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 contract ownership boundary verification failed.")
        return 1
    print("PHASE04 contract ownership boundary verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
