from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FORMAL = REPO_ROOT / "docs/modules/11-infrastructure.md"
MIRROR = REPO_ROOT / ".agent/modules/11-infrastructure.md"
DATA_FORMAL = REPO_ROOT / "docs/modules/11-infrastructure-data-services.md"
DATA_MIRROR = REPO_ROOT / ".agent/modules/11-infrastructure-data-services.md"
LIFECYCLE_FORMAL = REPO_ROOT / "docs/modules/11-infrastructure-consistency-lifecycle.md"
LIFECYCLE_MIRROR = REPO_ROOT / ".agent/modules/11-infrastructure-consistency-lifecycle.md"
CONTRACT_REGISTRY = REPO_ROOT / "docs/governance/wave1-cross-module-contract-registry.md"
FORMAL_INDEX = REPO_ROOT / "docs/modules/README.md"
MIRROR_INDEX = REPO_ROOT / ".agent/modules/README.md"

PARTS = [
    "# Part I：问题、目标与选择",
    "# Part II：逻辑边界与运行拓扑",
    "# Part III：核心 Contract 与状态机",
    "# Part IV：数据库、队列、配置与运维协议",
    "# Part V：故障、恢复与灾备",
    "# Part VI：跨模块依赖协议",
    "# Part VII：目标实现规格",
    "# Part VIII：Requirement、测试与完成证据",
]

REQUIRED_OBJECTS = [
    "InfrastructureCapabilityProfile",
    "DatabaseTransaction",
    "StorageObject",
    "ObjectCommit",
    "CheckpointRecord",
    "QueueMessage",
    "InboxRecord",
    "OutboxRecord",
    "WorkerLease",
    "FencingToken",
    "MigrationPlan",
    "MigrationRun",
    "BackupPlan",
    "BackupRun",
    "RestoreRun",
    "RetentionPolicy",
    "LegalHold",
    "DrainMarker",
    "InfrastructureHealth",
    "CapacityReservation",
    "RecoveryWatermark",
]

REQUIRED_STATE_MACHINES = [
    "ObjectCommit State Machine",
    "QueueMessage / Delivery State Machine",
    "WorkerLease State Machine",
    "MigrationRun State Machine",
    "BackupRun State Machine",
    "RestoreRun State Machine",
    "Drain State Machine",
    "CapacityReservation",
]

REQUIRED_FAULTS = [
    "Outbox Crash",
    "Inbox Duplicate",
    "Object Commit Crash",
    "Lease Expiry",
    "Stale Fencing Token",
    "Checkpoint / Domain Divergence",
    "Queue Redelivery",
    "Migration Rollback",
    "Backup Corruption",
    "Restore Failure",
    "Clock Skew",
    "Drain Deadline",
    "Capacity Exhaustion",
]

CROSS_MODULE_TERMS = [
    "Security Epoch",
    "Secret Delivery Port",
    "Provider Config",
    "Usage Ledger",
    "Trace/Audit",
    "Eval Job Queue",
    "PostgreSQL 保存领域事实",
    "LangGraph Checkpointer 保存图控制状态",
    "Generation、Fencing、RecoveryWatermark 与 Outbox",
]

NOT_SELECTED = [
    "Kafka 作为默认工作队列",
    "Event Sourcing 作为全系统事实模型",
    "XA / 2PC",
    "默认多区域 Active-Active",
    "大量微服务",
    "Kubernetes 作为本模块完成标准",
]

DATA_SERVICE_TERMS = [
    "PostgreSQL",
    "RabbitMQ",
    "Object Store / MinIO",
    "LangGraph Checkpointer",
    "Redis",
    "Milvus",
    "Neo4j",
    "BM25 / Search",
    "Trace/Audit persistence",
    "Secret/KMS",
    "DataServiceCapability",
    "VectorIndexRuntimePort",
    "GraphIndexRuntimePort",
    "LexicalIndexRuntimePort",
    "CacheAccelerationPort",
    "DerivedIndexReplica State Machine",
    "Cross-store Publish Protocol",
    "IndexWriteReceipt",
    "IndexManifest",
    "generation/CAS",
    "authoritative",
    "rebuildable",
]

DATA_FAILURE_TERMS = [
    "INFRA_VECTOR_WRITE_PARTIAL",
    "INFRA_VECTOR_SCHEMA_INCOMPATIBLE",
    "INFRA_GRAPH_WRITE_PARTIAL",
    "INFRA_GRAPH_SCHEMA_INCOMPATIBLE",
    "INFRA_LEXICAL_INDEX_CORRUPT",
    "INFRA_CACHE_STALE_GENERATION",
    "INFRA_CROSS_STORE_VERSION_DIVERGENCE",
    "INFRA_INDEX_CUTOVER_CONFLICT",
    "Milvus Write-Then-Crash Before Manifest Commit",
    "Neo4j Commit-Then-Crash Before Manifest Commit",
    "Tenant Filter Omission / Cross-tenant Hit",
    "PITR with Stale Derived Indexes",
]

LIFECYCLE_TERMS = [
    "IndexBuildRun",
    "IndexWriteBatch",
    "IndexWriteReceipt",
    "IndexVerification",
    "DerivedIndexReplica",
    "IndexCutover",
    "IndexRebuildRun",
    "IndexRetirement",
    "IndexReconciliationFinding",
    "ServingWatermark",
    "WriteVisibilityReceipt",
    "DeletionRequest",
    "DeletionTarget",
    "DeletionVerification",
    "RecoverySetManifest",
    "RecoverySetValidation",
    "AuditDurabilityRequirement",
    "AuditBufferReservation",
    "AuditPersistenceReceipt",
    "TenantIsolationProfile",
    "ServiceCompatibilityEntry",
    "AdapterConformanceProfile",
    "ServiceCriticalityProfile",
    "ReleaseManifest",
    "ResourceUsageAttribution",
    "Cross-store Deletion",
    "Recovery Set",
    "Mandatory Audit Backpressure",
    "Upgrade Compatibility",
    "PreparedAction 与 Tool Effect Ownership",
    "Tenant Filter Omission / Cross-tenant Hit",
    "PITR With Ahead / Behind Derived Index",
]

LIFECYCLE_FAILURES = [
    "INFRA_INDEX_CUTOVER_GENERATION_CONFLICT",
    "INFRA_DELETION_VISIBILITY_DEADLINE",
    "INFRA_RECOVERY_SET_INCONSISTENT",
    "INFRA_MANDATORY_AUDIT_BLOCK_EFFECT",
    "INFRA_CROSS_TENANT_HIT",
    "INFRA_ADAPTER_SEMANTIC_UNSUPPORTED",
    "INFRA_RELEASE_PROVENANCE_INVALID",
    "INFRA_RESOURCE_ATTRIBUTION_MISSING",
]

REGISTRY_TERMS = [
    "parallel-proposal-governance",
    "CrossModuleEnvelope",
    "SecurityConditionalWrite",
    "CredentialVersionRef",
    "SecurityAuditRequirement",
    "AuditDurabilityRequirement",
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
    "PreparedAction Ownership 决议建议",
    "Queue ACK != Tool Effect Success",
    "Failure Ownership Matrix",
    "Wave 1 合并前审计清单",
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


def _verify_numbered_registry(
    *,
    content: str,
    pattern: str,
    expected: list[int],
    prefix: str,
    finding_prefix: str,
    findings: list[Finding],
) -> None:
    numbers = [int(value) for value in re.findall(pattern, content)]
    if sorted(numbers) != expected:
        findings.append(
            Finding(f"{finding_prefix}_REQUIREMENT_REGISTRY", f"{prefix} IDs must be exactly {expected[0]:03d}..{expected[-1]:03d}")
        )
    test_prefix = prefix.replace("ARCH-", "")
    evidence_prefix = prefix.replace("ARCH-", "EV-")
    for number in expected:
        for suffix in ["UT", "IT"]:
            test_id = f"{test_prefix}-{number:03d}-{suffix}"
            if test_id not in content:
                findings.append(Finding(f"{finding_prefix}_TEST_MAPPING", f"missing {test_id}"))
        evidence_id = f"{evidence_prefix}-{number:03d}"
        if evidence_id not in content:
            findings.append(Finding(f"{finding_prefix}_EVIDENCE_MAPPING", f"missing {evidence_id}"))


def verify() -> list[Finding]:
    findings: list[Finding] = []

    for path, code in [
        (FORMAL, "INFRA_DOC_MISSING"),
        (MIRROR, "INFRA_MIRROR_MISSING"),
        (DATA_FORMAL, "INFRA_DATA_DOC_MISSING"),
        (DATA_MIRROR, "INFRA_DATA_MIRROR_MISSING"),
        (LIFECYCLE_FORMAL, "INFRA_LIFECYCLE_DOC_MISSING"),
        (LIFECYCLE_MIRROR, "INFRA_LIFECYCLE_MIRROR_MISSING"),
        (CONTRACT_REGISTRY, "INFRA_CONTRACT_REGISTRY_MISSING"),
        (FORMAL_INDEX, "INFRA_FORMAL_INDEX_MISSING"),
        (MIRROR_INDEX, "INFRA_MIRROR_INDEX_MISSING"),
    ]:
        if not path.exists():
            findings.append(Finding(code, str(path.relative_to(REPO_ROOT))))

    if findings:
        return findings

    content = _read(FORMAL)
    data_content = _read(DATA_FORMAL)
    lifecycle_content = _read(LIFECYCLE_FORMAL)
    registry_content = _read(CONTRACT_REGISTRY)

    if FORMAL.read_bytes() != MIRROR.read_bytes():
        findings.append(Finding("INFRA_MIRROR_DRIFT", "formal document and Agent mirror are not byte-identical"))
    if DATA_FORMAL.read_bytes() != DATA_MIRROR.read_bytes():
        findings.append(Finding("INFRA_DATA_MIRROR_DRIFT", "data-service appendix and Agent mirror are not byte-identical"))
    if LIFECYCLE_FORMAL.read_bytes() != LIFECYCLE_MIRROR.read_bytes():
        findings.append(
            Finding("INFRA_LIFECYCLE_MIRROR_DRIFT", "lifecycle appendix and Agent mirror are not byte-identical")
        )

    positions: list[int] = []
    for part in PARTS:
        if content.count(part) != 1:
            findings.append(Finding("INFRA_PART_INVALID", f"{part!r} must appear exactly once"))
        else:
            positions.append(content.index(part))
    if positions != sorted(positions):
        findings.append(Finding("INFRA_PART_ORDER", "normative parts are not ordered"))

    for term in [
        "Current Inventory",
        "Target Selection",
        "Future Optional",
        "Explicitly Not Selected",
        "Developer / CI Local Adapter Topology",
        "Canonical Server Product Topology",
        "服务端统一后端是产品 Target",
        "Crash Matrix",
        "Failure Taxonomy",
        "Multi-tenant Storage Isolation",
        "Encryption at Rest / in Transit",
        "Observability Hook",
        "Target → Current Evidence",
    ]:
        _require(content, term, "INFRA_COVERAGE_MISSING", findings)

    for name in REQUIRED_OBJECTS:
        _require(content, name, "INFRA_OBJECT_MISSING", findings)
    for name in REQUIRED_STATE_MACHINES:
        _require(content, name, "INFRA_STATE_MACHINE_MISSING", findings)
    for name in REQUIRED_FAULTS:
        _require(content, name, "INFRA_FAULT_TEST_MISSING", findings)
    for term in CROSS_MODULE_TERMS:
        _require(content, term, "INFRA_CROSS_MODULE_MISSING", findings)
    for term in NOT_SELECTED:
        _require(content, term, "INFRA_NOT_SELECTED_MISSING", findings)

    requirements = [int(value) for value in re.findall(r"ARCH-INFRA-(\d{3})", content)]
    controls = [int(value) for value in re.findall(r"RC-INFRA-(\d{3})", content)]
    expected = list(range(1, 49))
    if sorted(requirements) != expected:
        findings.append(Finding("INFRA_REQUIREMENT_REGISTRY", "ARCH-INFRA IDs must be exactly 001..048"))
    if sorted(controls) != expected:
        findings.append(Finding("INFRA_CONTROL_REGISTRY", "RC-INFRA IDs must be exactly 001..048"))
    for number in expected:
        for suffix in ["UT", "IT"]:
            test_id = f"INFRA-{number:03d}-{suffix}"
            if test_id not in content:
                findings.append(Finding("INFRA_TEST_MAPPING", f"missing {test_id}"))
        evidence_id = f"EV-INFRA-{number:03d}"
        if evidence_id not in content:
            findings.append(Finding("INFRA_EVIDENCE_MAPPING", f"missing {evidence_id}"))

    for appendix_content, code in [
        (data_content, "INFRA_DATA_PARENT"),
        (lifecycle_content, "INFRA_LIFECYCLE_PARENT"),
    ]:
        if "parent_document: `docs/modules/11-infrastructure.md`" not in appendix_content:
            findings.append(Finding(code, "appendix does not declare the Infrastructure parent document"))

    for term in DATA_SERVICE_TERMS:
        _require(data_content, term, "INFRA_DATA_SERVICE_COVERAGE", findings)
    for term in DATA_FAILURE_TERMS:
        _require(data_content, term, "INFRA_DATA_FAILURE_COVERAGE", findings)
    _verify_numbered_registry(
        content=data_content,
        pattern=r"ARCH-INFRA-DS-(\d{3})",
        expected=list(range(1, 13)),
        prefix="ARCH-INFRA-DS",
        finding_prefix="INFRA_DATA",
        findings=findings,
    )

    for term in LIFECYCLE_TERMS:
        _require(lifecycle_content, term, "INFRA_LIFECYCLE_COVERAGE", findings)
    for term in LIFECYCLE_FAILURES:
        _require(lifecycle_content, term, "INFRA_LIFECYCLE_FAILURE_COVERAGE", findings)
    _verify_numbered_registry(
        content=lifecycle_content,
        pattern=r"ARCH-INFRA-LC-(\d{3})",
        expected=list(range(1, 25)),
        prefix="ARCH-INFRA-LC",
        finding_prefix="INFRA_LIFECYCLE",
        findings=findings,
    )

    for term in REGISTRY_TERMS:
        _require(registry_content, term, "INFRA_CONTRACT_REGISTRY_COVERAGE", findings)
    _verify_numbered_registry(
        content=registry_content,
        pattern=r"ARCH-XMOD-(\d{3})",
        expected=list(range(1, 11)),
        prefix="ARCH-XMOD",
        finding_prefix="INFRA_XMOD",
        findings=findings,
    )

    for forbidden in [
        "PostgreSQL 已是 Current",
        "RabbitMQ 已是 Current",
        "MinIO 已是 Current",
        "Milvus 已是 Current",
        "Neo4j 已是 Current",
        "Redis 已是 Current",
        "Kubernetes 已是 Current",
        "production ready 已完成",
    ]:
        if any(forbidden in item for item in [content, data_content, lifecycle_content, registry_content]):
            findings.append(Finding("INFRA_CURRENT_PROMOTION", f"forbidden unsupported statement: {forbidden}"))

    formal_index = _read(FORMAL_INDEX)
    mirror_index = _read(MIRROR_INDEX)
    if "(./11-infrastructure.md)" not in formal_index:
        findings.append(Finding("INFRA_FORMAL_INDEX_ROUTE", "docs/modules/README.md does not route Infrastructure"))
    for path in ["11-infrastructure-data-services.md", "11-infrastructure-consistency-lifecycle.md"]:
        if path not in formal_index:
            findings.append(Finding("INFRA_FORMAL_APPENDIX_ROUTE", f"docs/modules/README.md does not route {path}"))
        if path not in mirror_index:
            findings.append(Finding("INFRA_MIRROR_APPENDIX_ROUTE", f".agent/modules/README.md does not route {path}"))
    if "wave1-cross-module-contract-registry.md" not in formal_index:
        findings.append(Finding("INFRA_CONTRACT_REGISTRY_ROUTE", "docs/modules/README.md does not route Wave 1 registry"))
    if "(./11-infrastructure.md)" not in mirror_index:
        findings.append(Finding("INFRA_MIRROR_INDEX_ROUTE", ".agent/modules/README.md does not route Infrastructure mirror"))

    return findings


def main() -> int:
    findings = verify()
    if findings:
        print("Infrastructure target protocol verification failed:")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("Infrastructure target protocol verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
