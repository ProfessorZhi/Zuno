from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ADR = REPO_ROOT / "docs/decisions/0003-wave1-cross-module-contract-freeze.md"
DECISIONS_INDEX = REPO_ROOT / "docs/decisions/README.md"
REGISTRY = REPO_ROOT / "docs/governance/wave1-cross-module-contract-registry.md"
MODULES_INDEX = REPO_ROOT / "docs/modules/README.md"
AGENT_MODULES_INDEX = REPO_ROOT / ".agent/modules/README.md"

BASELINE_SHA = "729e439e29deadc101c5687fc47125104e62e2c1"

ADR_TERMS = [
    "status: accepted-target-pending-merge",
    "CrossModuleEnvelopeV1",
    "EffectiveSecurityEpochRefV1",
    "CredentialVersionRefV1",
    "SecretLeaseV1",
    "SecurityAuditRequirementV1",
    "AuditPersistenceReceiptV1",
    "ProviderConnectionRequestV1",
    "ModelQuotaReservationV1",
    "ModelUsageReceiptV1",
    "ModelCancellationReceiptV1",
    "IndexWriteBatchV1",
    "IndexWriteReceiptV1",
    "WriteVisibilityReceiptV1",
    "ActionProposalV1",
    "PreparedToolActionV1",
    "ActionExecutionBinding",
    "EffectReceipt",
    "EffectReconciliation",
    "FIELD_FROZEN_PENDING_MERGE",
    "src/backend/zuno/platform/",
    "platform/data_services/",
    "Queue ACK != Tool Effect Success",
    "Checkpoint Commit != Domain Commit",
]

REGISTRY_TERMS = [
    "status: field-frozen-pending-merge",
    "previous_status: parallel-proposal-governance",
    "CrossModuleEnvelopeV1",
    "SecurityConditionalWrite",
    "CredentialVersionRefV1",
    "SecretLeaseV1",
    "SecurityAuditRequirementV1",
    "AuditDurabilityRequirement",
    "AuditPersistenceReceiptV1",
    "TelemetryEnvelope",
    "ProviderConnectionFactory",
    "UsageReceipt",
    "QuotaReservation",
    "CancellationReceipt",
    "VectorIndexSpec",
    "GraphIndexSpec",
    "LexicalIndexSpec",
    "IndexWriteBatch",
    "IndexWriteReceipt",
    "WriteVisibilityReceipt",
    "IndexManifest",
    "ServingWatermark",
    "DeletionRequest",
    "RecoverySetManifest",
    "PreparedAction Ownership 决议建议——现已冻结",
    "PreparedToolAction",
    "Queue ACK != Tool Effect Success",
    "Failure Ownership Matrix",
    "Wave 1 合并前审计清单",
    "design field freeze complete",
]

CANONICAL_FAILURE_CODES = [
    "SEC_CONTEXT_MISSING",
    "SEC_STALE_EPOCH",
    "SEC_APPROVAL_REQUIRED",
    "SEC_APPROVAL_REPLAY",
    "SEC_REDACTION_FAILED",
    "SEC_AUDIT_REQUIREMENT_UNSATISFIED",
    "INFRA_CONDITIONAL_WRITE_CONFLICT",
    "INFRA_SECRET_LEASE_UNAVAILABLE",
    "INFRA_AUDIT_PERSISTENCE_FAILED",
    "INFRA_CAPACITY_EXHAUSTED",
    "INFRA_INDEX_CUTOVER_CONFLICT",
    "INFRA_WRITE_VISIBILITY_DEADLINE",
    "MODEL_PROVIDER_TIMEOUT",
    "MODEL_ATTEMPT_UNKNOWN",
    "MODEL_QUOTA_UNAVAILABLE",
    "MODEL_USAGE_SETTLEMENT_PENDING",
    "MODEL_CANCELLATION_UNCONFIRMED",
    "OBS_ENVELOPE_SCHEMA_UNSUPPORTED",
    "OBS_INGEST_GAP",
    "OBS_AUDIT_ACCEPTANCE_FAILED",
    "OBS_EXTERNAL_SINK_DELIVERY_FAILED",
    "TOOL_PREPARED_ACTION_INVALID",
    "TOOL_EFFECT_UNKNOWN",
    "TOOL_EFFECT_RECONCILIATION_REQUIRED",
    "TOOL_DUPLICATE_EFFECT_BLOCKED",
    "KNOW_INDEX_MANIFEST_REJECTED",
    "KNOW_RETRIEVAL_POLICY_UNSATISFIED",
]


@dataclass(frozen=True)
class Finding:
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _require(content: str, term: str, code: str, findings: list[Finding]) -> None:
    if term not in content:
        findings.append(Finding(code, f"missing required term: {term}"))


def verify() -> list[Finding]:
    findings: list[Finding] = []

    for path, code in [
        (ADR, "XMOD_ADR_MISSING"),
        (DECISIONS_INDEX, "XMOD_DECISIONS_INDEX_MISSING"),
        (REGISTRY, "XMOD_REGISTRY_MISSING"),
        (MODULES_INDEX, "XMOD_MODULES_INDEX_MISSING"),
        (AGENT_MODULES_INDEX, "XMOD_AGENT_INDEX_MISSING"),
    ]:
        if not path.exists():
            findings.append(Finding(code, str(path.relative_to(REPO_ROOT))))

    if findings:
        return findings

    adr = _read(ADR)
    registry = _read(REGISTRY)
    decisions_index = _read(DECISIONS_INDEX)
    modules_index = _read(MODULES_INDEX)
    agent_index = _read(AGENT_MODULES_INDEX)

    for content, label in [(adr, "ADR"), (registry, "REGISTRY")]:
        if BASELINE_SHA not in content:
            findings.append(Finding("XMOD_BASELINE_MISSING", f"{label} does not pin baseline SHA"))

    for term in ADR_TERMS:
        _require(adr, term, "XMOD_ADR_COVERAGE", findings)
    for term in REGISTRY_TERMS:
        _require(registry, term, "XMOD_REGISTRY_COVERAGE", findings)
    for code in CANONICAL_FAILURE_CODES:
        _require(adr, code, "XMOD_ADR_FAILURE_COVERAGE", findings)
        _require(registry, code, "XMOD_REGISTRY_FAILURE_COVERAGE", findings)

    if "0003-wave1-cross-module-contract-freeze.md" not in decisions_index:
        findings.append(Finding("XMOD_DECISION_ROUTE", "docs/decisions/README.md does not route ADR 0003"))

    for content, label in [(modules_index, "docs/modules/README.md"), (agent_index, ".agent/modules/README.md")]:
        for term in [
            "0003-wave1-cross-module-contract-freeze.md",
            "wave1-cross-module-contract-registry.md",
            "FIELD_FROZEN_PENDING_MERGE",
            "src/backend/zuno/platform/**",
            "PreparedToolAction",
        ]:
            if term not in content:
                findings.append(Finding("XMOD_INDEX_ROUTE", f"{label} missing {term}"))

    requirement_ids = [int(value) for value in re.findall(r"ARCH-XMOD-(\d{3})", registry)]
    if sorted(requirement_ids) != list(range(1, 11)):
        findings.append(Finding("XMOD_REQUIREMENT_REGISTRY", "ARCH-XMOD IDs must be exactly 001..010"))

    for number in range(1, 11):
        for suffix in ["UT", "IT"]:
            test_id = f"XMOD-{number:03d}-{suffix}"
            if test_id not in registry:
                findings.append(Finding("XMOD_TEST_MAPPING", f"missing {test_id}"))
        evidence_id = f"EV-XMOD-{number:03d}"
        if evidence_id not in registry:
            findings.append(Finding("XMOD_EVIDENCE_MAPPING", f"missing {evidence_id}"))

    if registry.count("`FIELD_FROZEN_PENDING_MERGE`") < 25:
        findings.append(Finding("XMOD_STATUS_NOT_FROZEN", "too few shared contracts are field-frozen"))

    forbidden_unresolved_phrases = [
        "协调状态：`CONFLICT_REQUIRES_DECISION`",
        "本文件当前所有条目最高只能是 `ALIGNED_PENDING_FIELDS`",
        "字段级 Contract 尚未全部确认",
    ]
    for phrase in forbidden_unresolved_phrases:
        if phrase in registry:
            findings.append(Finding("XMOD_UNRESOLVED_DRIFT", f"registry still contains unresolved statement: {phrase}"))

    for content, label in [(adr, "ADR"), (registry, "REGISTRY")]:
        for line in content.splitlines():
            if "src/backend/zuno/infrastructure/" in line and "不新增" not in line:
                findings.append(
                    Finding("XMOD_PHYSICAL_OWNER_DRIFT", f"{label} positively maps runtime code to zuno/infrastructure: {line}")
                )

    for phrase in [
        "Queue ACK != Tool Effect Success",
        "Audit Persistence != Tool Effect Success",
        "Checkpoint Commit != Domain Commit",
    ]:
        if phrase not in adr or phrase not in registry:
            findings.append(Finding("XMOD_RECEIPT_BOUNDARY", f"missing invariant: {phrase}"))

    if "accepted-target-pending-merge" not in adr or "field-frozen-pending-merge" not in registry:
        findings.append(Finding("XMOD_STATUS_INVALID", "ADR/Registry pending-merge status is inconsistent"))

    forbidden_promotions = [
        "production ready 已完成",
        "PostgreSQL 已是 Current",
        "RabbitMQ 已是 Current",
        "Milvus 已是 Current",
        "Neo4j 已是 Current",
        "Redis 已是 Current",
    ]
    for phrase in forbidden_promotions:
        if phrase in adr or phrase in registry:
            findings.append(Finding("XMOD_FALSE_PROMOTION", f"unsupported status promotion: {phrase}"))

    return findings


def main() -> int:
    findings = verify()
    if findings:
        print("Wave 1 contract freeze verification failed:")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("Wave 1 contract freeze verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
