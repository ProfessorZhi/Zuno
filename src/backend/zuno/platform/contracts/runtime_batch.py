from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from pydantic import BaseModel, ValidationError

from zuno.platform.contracts.canonical import canonical_sha256
from zuno.platform.contracts.registry import (
    ContractRegistry,
    ContractRegistryEntry,
    ContractVersion,
    build_wave1_contract_registry,
)
from zuno.platform.contracts.shared import (
    AuditPersistenceReceiptV1,
    CrossModuleEnvelopeV1,
    EffectiveSecurityEpochRefV1,
    EffectReceiptV1,
    FailureCodeV1,
    FailureOwner,
    IndexWriteBatchV1,
    IndexWriteReceiptV1,
    PreparedToolActionV1,
    WriteVisibilityReceiptV1,
)


CANONICAL_FAILURE_CODES: tuple[tuple[str, FailureOwner, FailureOwner], ...] = (
    ("SEC_CONTEXT_MISSING", FailureOwner.SECURITY, FailureOwner.SECURITY),
    ("SEC_STALE_EPOCH", FailureOwner.SECURITY, FailureOwner.SECURITY),
    ("SEC_APPROVAL_REQUIRED", FailureOwner.SECURITY, FailureOwner.SECURITY),
    ("SEC_APPROVAL_REPLAY", FailureOwner.SECURITY, FailureOwner.SECURITY),
    ("SEC_REDACTION_FAILED", FailureOwner.SECURITY, FailureOwner.SECURITY),
    ("SEC_AUDIT_REQUIREMENT_UNSATISFIED", FailureOwner.SECURITY, FailureOwner.OBSERVABILITY),
    ("INFRA_CONDITIONAL_WRITE_CONFLICT", FailureOwner.INFRASTRUCTURE, FailureOwner.INFRASTRUCTURE),
    ("INFRA_SECRET_LEASE_UNAVAILABLE", FailureOwner.INFRASTRUCTURE, FailureOwner.INFRASTRUCTURE),
    ("INFRA_AUDIT_PERSISTENCE_FAILED", FailureOwner.INFRASTRUCTURE, FailureOwner.OBSERVABILITY),
    ("INFRA_CAPACITY_EXHAUSTED", FailureOwner.INFRASTRUCTURE, FailureOwner.INFRASTRUCTURE),
    ("INFRA_INDEX_CUTOVER_CONFLICT", FailureOwner.INFRASTRUCTURE, FailureOwner.KNOWLEDGE),
    ("INFRA_WRITE_VISIBILITY_DEADLINE", FailureOwner.INFRASTRUCTURE, FailureOwner.KNOWLEDGE),
    ("MODEL_PROVIDER_TIMEOUT", FailureOwner.MODEL_GATEWAY, FailureOwner.MODEL_GATEWAY),
    ("MODEL_ATTEMPT_UNKNOWN", FailureOwner.MODEL_GATEWAY, FailureOwner.MODEL_GATEWAY),
    ("MODEL_QUOTA_UNAVAILABLE", FailureOwner.MODEL_GATEWAY, FailureOwner.MODEL_GATEWAY),
    ("MODEL_USAGE_SETTLEMENT_PENDING", FailureOwner.MODEL_GATEWAY, FailureOwner.MODEL_GATEWAY),
    ("MODEL_CANCELLATION_UNCONFIRMED", FailureOwner.MODEL_GATEWAY, FailureOwner.MODEL_GATEWAY),
    ("OBS_ENVELOPE_SCHEMA_UNSUPPORTED", FailureOwner.OBSERVABILITY, FailureOwner.OBSERVABILITY),
    ("OBS_INGEST_GAP", FailureOwner.OBSERVABILITY, FailureOwner.OBSERVABILITY),
    ("OBS_AUDIT_ACCEPTANCE_FAILED", FailureOwner.OBSERVABILITY, FailureOwner.OBSERVABILITY),
    ("OBS_EXTERNAL_SINK_DELIVERY_FAILED", FailureOwner.OBSERVABILITY, FailureOwner.OBSERVABILITY),
    ("TOOL_PREPARED_ACTION_INVALID", FailureOwner.TOOL_RUNTIME, FailureOwner.TOOL_RUNTIME),
    ("TOOL_EFFECT_UNKNOWN", FailureOwner.TOOL_RUNTIME, FailureOwner.TOOL_RUNTIME),
    ("TOOL_EFFECT_RECONCILIATION_REQUIRED", FailureOwner.TOOL_RUNTIME, FailureOwner.TOOL_RUNTIME),
    ("TOOL_DUPLICATE_EFFECT_BLOCKED", FailureOwner.TOOL_RUNTIME, FailureOwner.TOOL_RUNTIME),
    ("KNOW_INDEX_MANIFEST_REJECTED", FailureOwner.KNOWLEDGE, FailureOwner.KNOWLEDGE),
    ("KNOW_RETRIEVAL_POLICY_UNSATISFIED", FailureOwner.KNOWLEDGE, FailureOwner.KNOWLEDGE),
)


@dataclass(frozen=True)
class CrossModuleRuntimeBatchReport:
    requirement_ids: tuple[str, ...]
    contract_count: int
    manifest_hash: str
    failure_code_count: int
    confirmed_registry: bool
    confirmed_adr: bool


class CrossModuleRuntimeBatchError(ValueError):
    def __init__(self, errors: Iterable[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("; ".join(self.errors))


def validate_cross_module_runtime_batch(
    *,
    registry: ContractRegistry | None = None,
    registry_doc: str | None = None,
    adr_doc: str | None = None,
) -> CrossModuleRuntimeBatchReport:
    registry = registry or build_wave1_contract_registry()
    manifest = registry.manifest()
    errors: list[str] = []

    errors.extend(_validate_single_owner(manifest.entries))
    errors.extend(_validate_owner_coverage(manifest.entries))
    errors.extend(_validate_epoch_generation_deadline())
    errors.extend(_validate_receipt_boundaries())
    errors.extend(_validate_prepared_action_ownership(registry))
    errors.extend(_validate_audit_backpressure(registry_doc))
    errors.extend(_validate_index_protocol(registry))
    errors.extend(_validate_version_and_enum_compatibility(registry))
    failure_codes = _build_failure_codes(errors)
    errors.extend(_validate_adr_and_audit_evidence(registry_doc, adr_doc))

    if errors:
        raise CrossModuleRuntimeBatchError(errors)

    return CrossModuleRuntimeBatchReport(
        requirement_ids=tuple(f"ARCH-XMOD-{index:03d}" for index in range(1, 11)),
        contract_count=len(manifest.entries),
        manifest_hash=manifest.bundle_hash,
        failure_code_count=len(failure_codes),
        confirmed_registry=bool(registry_doc and "status: confirmed-target" in registry_doc),
        confirmed_adr=bool(adr_doc and "status: accepted-target" in adr_doc),
    )


def validate_cross_module_runtime_batch_from_repo(
    repo_root: Path,
) -> CrossModuleRuntimeBatchReport:
    registry_doc = (
        repo_root / "docs/governance/wave1-cross-module-contract-registry.md"
    ).read_text(encoding="utf-8")
    adr_doc = (
        repo_root / "docs/decisions/0003-wave1-cross-module-contract-freeze.md"
    ).read_text(encoding="utf-8")
    return validate_cross_module_runtime_batch(
        registry_doc=registry_doc,
        adr_doc=adr_doc,
    )


def _validate_single_owner(entries: tuple[ContractRegistryEntry, ...]) -> list[str]:
    errors: list[str] = []
    owners_by_contract: dict[str, str] = {}
    for entry in entries:
        owner = owners_by_contract.setdefault(entry.contract_name, entry.owner_module)
        if owner != entry.owner_module:
            errors.append(
                f"{entry.contract_name} has duplicate owners: {owner}, {entry.owner_module}"
            )
    return errors


def _validate_owner_coverage(entries: tuple[ContractRegistryEntry, ...]) -> list[str]:
    errors: list[str] = []
    for entry in entries:
        if not entry.owner_module:
            errors.append(f"{entry.contract_name} is missing owner")
        if not entry.producer_modules:
            errors.append(f"{entry.contract_name} is missing producer modules")
        if not entry.consumer_modules:
            errors.append(f"{entry.contract_name} is missing consumer modules")
        if not entry.schema_hash:
            errors.append(f"{entry.contract_name} is missing schema hash")
    required = {
        "FailureCodeV1",
        "AuditPersistenceReceiptV1",
        "IndexWriteBatchV1",
        "IndexWriteReceiptV1",
        "WriteVisibilityReceiptV1",
    }
    names = {entry.contract_name for entry in entries}
    for name in sorted(required - names):
        errors.append(f"missing owner boundary contract: {name}")
    return errors


def _schema_fields(model: type[BaseModel]) -> set[str]:
    return set(model.model_json_schema()["properties"])


def _validate_epoch_generation_deadline() -> list[str]:
    errors: list[str] = []
    required = {
        CrossModuleEnvelopeV1: {
            "effective_security_epoch_ref",
            "effective_security_epoch_hash",
            "expected_generation",
            "deadline_at",
        },
        PreparedToolActionV1: {
            "effective_security_epoch_ref",
            "effective_security_epoch_hash",
            "deadline_at",
        },
        IndexWriteBatchV1: {
            "expected_generation",
            "effective_security_epoch_ref",
            "deadline_at",
        },
        EffectiveSecurityEpochRefV1: {
            "tenant_epoch",
            "workspace_epoch",
            "principal_epoch",
            "resource_epoch",
            "epoch_hash",
        },
    }
    for model, fields in required.items():
        missing = fields - _schema_fields(model)
        if missing:
            errors.append(f"{model.__name__} missing temporal fields: {sorted(missing)}")
    return errors


def _validate_receipt_boundaries() -> list[str]:
    errors: list[str] = []
    for model in (
        AuditPersistenceReceiptV1,
        EffectReceiptV1,
        IndexWriteReceiptV1,
        WriteVisibilityReceiptV1,
    ):
        fields = _schema_fields(model)
        forbidden = {
            "domain_success",
            "run_outcome",
            "task_succeeded",
            "tool_effect_success",
        }
        overlap = fields.intersection(forbidden)
        if overlap:
            errors.append(f"{model.__name__} exposes domain success fields: {overlap}")
    if "effect_state" not in _schema_fields(EffectReceiptV1):
        errors.append("EffectReceiptV1 must expose effect_state, not generic success")
    if "status" not in _schema_fields(AuditPersistenceReceiptV1):
        errors.append("AuditPersistenceReceiptV1 must expose audit persistence status")
    return errors


def _validate_prepared_action_ownership(registry: ContractRegistry) -> list[str]:
    expected = {
        "ActionProposalV1": "Agent Core",
        "ActionExecutionBindingV1": "Agent Core",
        "PreparedToolActionV1": "Tool Runtime",
        "SecurityApprovalDecisionV1": "Security",
        "EffectReceiptV1": "Tool Runtime",
    }
    errors: list[str] = []
    for contract_name, owner in expected.items():
        try:
            entry = registry.get(contract_name, "1.0")
        except (KeyError, ValueError) as exc:
            errors.append(f"{contract_name} ownership entry missing: {exc}")
            continue
        if entry.owner_module != owner:
            errors.append(
                f"{contract_name} owner must be {owner}, got {entry.owner_module}"
            )
    return errors


def _validate_audit_backpressure(registry_doc: str | None) -> list[str]:
    errors: list[str] = []
    if "audit_requirement_ref" not in _schema_fields(CrossModuleEnvelopeV1):
        errors.append("CrossModuleEnvelopeV1 missing audit_requirement_ref")
    status_schema = AuditPersistenceReceiptV1.model_json_schema()["properties"]["status"]
    if "FAILED" not in status_schema["enum"]:
        errors.append("AuditPersistenceReceiptV1 must preserve failed audit state")
    if registry_doc is not None:
        for phrase in (
            "Mandatory Audit Backpressure",
            "SEC_AUDIT_REQUIREMENT_UNSATISFIED",
            "INFRA_AUDIT_PERSISTENCE_FAILED",
            "OBS_AUDIT_ACCEPTANCE_FAILED",
        ):
            if phrase not in registry_doc:
                errors.append(f"registry missing audit backpressure phrase: {phrase}")
    return errors


def _validate_index_protocol(registry: ContractRegistry) -> list[str]:
    errors: list[str] = []
    expected = {
        "IndexWriteBatchV1": (
            "Knowledge/Memory",
            ("Knowledge", "Memory"),
            ("Infrastructure",),
        ),
        "IndexWriteReceiptV1": (
            "Infrastructure",
            ("Infrastructure",),
            ("Knowledge", "Memory"),
        ),
        "WriteVisibilityReceiptV1": (
            "Infrastructure",
            ("Infrastructure",),
            ("Knowledge", "Memory"),
        ),
    }
    for contract_name, (owner, producers, consumers) in expected.items():
        try:
            entry = registry.get(contract_name, "1.0")
        except (KeyError, ValueError) as exc:
            errors.append(f"{contract_name} index protocol entry missing: {exc}")
            continue
        if entry.owner_module != owner:
            errors.append(f"{contract_name} owner mismatch: {entry.owner_module}")
        if entry.producer_modules != producers:
            errors.append(f"{contract_name} producer mismatch: {entry.producer_modules}")
        if entry.consumer_modules != consumers:
            errors.append(f"{contract_name} consumer mismatch: {entry.consumer_modules}")
    for model, required_fields in {
        IndexWriteBatchV1: {"payload_hash", "idempotency_key", "expected_generation"},
        IndexWriteReceiptV1: {"observed_generation", "status"},
        WriteVisibilityReceiptV1: {"visibility_deadline_at", "status"},
    }.items():
        missing = required_fields - _schema_fields(model)
        if missing:
            errors.append(f"{model.__name__} missing index protocol fields: {missing}")
    return errors


def _validate_version_and_enum_compatibility(registry: ContractRegistry) -> list[str]:
    errors: list[str] = []
    try:
        registry.get("CrossModuleEnvelopeV1", "9.0")
        errors.append("unknown major version was accepted")
    except (KeyError, ValueError):
        pass
    try:
        entry = registry.get("CrossModuleEnvelopeV1", "1.0")
    except (KeyError, ValueError) as exc:
        return [f"CrossModuleEnvelopeV1 compatibility entry missing: {exc}"]
    compat_registry = ContractRegistry(
        [
            entry,
            ContractRegistryEntry(
                contract_name=entry.contract_name,
                version=ContractVersion(major=1, minor=2),
                schema_hash=entry.schema_hash,
                owner_module=entry.owner_module,
                producer_modules=entry.producer_modules,
                consumer_modules=entry.consumer_modules,
            ),
        ]
    )
    if compat_registry.get("CrossModuleEnvelopeV1", "1.1").version.minor != 2:
        errors.append("compatible minor version lookup did not return latest reader")
    try:
        FailureCodeV1(
            code="TOOL_EFFECT_UNKNOWN",
            owner="UNRECOGNIZED_OWNER",  # type: ignore[arg-type]
            recovery_owner=FailureOwner.TOOL_RUNTIME,
        )
        errors.append("unknown failure owner enum was accepted")
    except ValidationError:
        pass
    return errors


def _build_failure_codes(errors: list[str]) -> tuple[FailureCodeV1, ...]:
    seen: set[str] = set()
    codes: list[FailureCodeV1] = []
    for code, owner, recovery_owner in CANONICAL_FAILURE_CODES:
        if code in seen:
            errors.append(f"duplicate failure code: {code}")
            continue
        seen.add(code)
        try:
            codes.append(
                FailureCodeV1(
                    code=code,
                    owner=owner,
                    recovery_owner=recovery_owner,
                    requires_reconcile=code.endswith("UNKNOWN")
                    or "PENDING" in code
                    or "UNCONFIRMED" in code,
                )
            )
        except ValidationError as exc:
            errors.append(f"invalid failure code {code}: {exc}")
    if len(codes) < 20:
        errors.append("canonical failure code set is incomplete")
    return tuple(codes)


def _validate_adr_and_audit_evidence(
    registry_doc: str | None, adr_doc: str | None
) -> list[str]:
    errors: list[str] = []
    if registry_doc is None or adr_doc is None:
        return errors
    for requirement in range(1, 11):
        requirement_id = f"ARCH-XMOD-{requirement:03d}"
        if requirement_id not in registry_doc:
            errors.append(f"registry missing {requirement_id}")
        for suffix in ("UT", "IT"):
            if f"XMOD-{requirement:03d}-{suffix}" not in registry_doc:
                errors.append(f"registry missing XMOD-{requirement:03d}-{suffix}")
        if f"EV-XMOD-{requirement:03d}" not in registry_doc:
            errors.append(f"registry missing EV-XMOD-{requirement:03d}")
    for phrase in (
        "status: confirmed-target",
        "Wave 1 合并审计清单",
        "docs/decisions/0003-wave1-cross-module-contract-freeze.md",
        "confirmed_wave1_main_sha",
    ):
        if phrase not in registry_doc and phrase not in adr_doc:
            errors.append(f"ADR/registry missing audit evidence phrase: {phrase}")
    if canonical_sha256(registry_doc) == canonical_sha256(adr_doc):
        errors.append("ADR and registry evidence must be distinct documents")
    return errors
