from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FORMAL = REPO_ROOT / "docs/modules/11-infrastructure.md"
MIRROR = REPO_ROOT / ".agent/modules/11-infrastructure.md"
FORMAL_INDEX = REPO_ROOT / "docs/modules/README.md"
MIRROR_INDEX = REPO_ROOT / ".agent/modules/README.md"
CONTRACT_REGISTRY = REPO_ROOT / "docs/governance/wave1-cross-module-contract-registry.md"

RETIRED_APPENDICES = [
    REPO_ROOT / "docs/modules/11-infrastructure-data-services.md",
    REPO_ROOT / ".agent/modules/11-infrastructure-data-services.md",
    REPO_ROOT / "docs/modules/11-infrastructure-consistency-lifecycle.md",
    REPO_ROOT / ".agent/modules/11-infrastructure-consistency-lifecycle.md",
]

PARTS = [
    "# Part I：定位、目标与架构选择",
    "# Part II：概念架构、拓扑与完整流程",
    "# Part III：核心 Contract 与事实边界",
    "# Part IV：数据服务组件设计",
    "# Part V：状态机与一致性生命周期",
    "# Part VI：失败、安全、恢复与运维",
    "# Part VII：目标实现规格",
    "# Part VIII：Requirement、测试与完成证据",
]

REQUIRED_COMPONENTS = [
    "PostgreSQL",
    "RabbitMQ",
    "Object Store / MinIO",
    "LangGraph Checkpointer",
    "Milvus",
    "Neo4j",
    "BM25 / Search",
    "Redis",
    "Trace/Audit persistence",
    "Secret/KMS",
]

REQUIRED_CONTRACTS = [
    "InfrastructureCapabilityProfile",
    "DataServiceCapability",
    "DatabaseTransaction",
    "StorageObject",
    "ObjectCommit",
    "QueueMessage",
    "InboxRecord",
    "OutboxRecord",
    "WorkerLease",
    "FencingToken",
    "CapacityReservation",
    "CheckpointRecord",
    "RecoveryWatermark",
    "IndexBuildRun",
    "IndexWriteBatch",
    "IndexWriteReceipt",
    "WriteVisibilityReceipt",
    "IndexVerification",
    "DerivedIndexReplica",
    "IndexCutover",
    "ServingWatermark",
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
]

REQUIRED_PORTS = [
    "TransactionalStorePort",
    "ObjectStorePort",
    "CheckpointStorePort",
    "QueuePort",
    "InboxOutboxPort",
    "LeaseFencingPort",
    "ClockPort",
    "MigrationRuntimePort",
    "BackupRestorePort",
    "RetentionLegalHoldPort",
    "SecretDeliveryPort",
    "HealthReadinessPort",
    "CapacityAdmissionPort",
    "InfrastructureTelemetryPort",
    "VectorIndexRuntimePort",
    "GraphIndexRuntimePort",
    "LexicalIndexRuntimePort",
    "CacheAccelerationPort",
]

REQUIRED_STATE_MACHINES = [
    "ObjectCommit State Machine",
    "QueueMessage / Delivery State Machine",
    "WorkerLease State Machine",
    "MigrationRun State Machine",
    "BackupRun 与 RestoreRun State Machine",
    "DerivedIndexReplica State Machine",
    "Deletion State Machine",
    "Recovery Set State Machine",
    "Mandatory Audit Backpressure State Machine",
    "Upgrade Compatibility State Machine",
    "Drain 与 CapacityReservation State Machine",
]

REQUIRED_FLOWS = [
    "文档摄取与索引构建流程",
    "在线查询流程",
    "异步工作流程",
    "Cross-store Publish Protocol",
    "Cross-store Deletion",
    "Recovery Set 与灾难恢复流程",
]

REQUIRED_BOUNDARIES = [
    "PostgreSQL 保存领域事实",
    "LangGraph Checkpointer 保存图控制状态",
    "Object Store 保存大型不可变 Payload",
    "Generation、Fencing、RecoveryWatermark 与 Outbox",
    "Checkpoint 不能替代 Domain Commit",
    "Queue ACK != Tool Effect Success",
    "IndexWriteReceipt != IndexManifest Accepted",
    "Security 决定允许访问什么",
]

REQUIRED_FAULTS = [
    "Outbox Crash",
    "Inbox Duplicate",
    "Object Commit Crash",
    "Lease Expiry",
    "Stale Fencing Token",
    "Checkpoint / Domain Divergence",
    "Queue Redelivery",
    "Publisher Confirm Loss",
    "Migration Rollback",
    "Backup Corruption",
    "Restore Failure",
    "Clock Skew",
    "Drain Deadline",
    "Capacity Exhaustion",
    "Milvus Write-Then-Crash Before Manifest Commit",
    "Neo4j Commit-Then-Crash Before Manifest Commit",
    "Tenant Filter Omission / Cross-tenant Hit",
    "PITR with Stale Derived Indexes",
    "Audit Committed Before Tool Effect Crash",
    "Network Partition With Stale Worker",
]

REQUIRED_FAILURES = [
    "INFRA_VECTOR_WRITE_PARTIAL",
    "INFRA_VECTOR_SCHEMA_INCOMPATIBLE",
    "INFRA_GRAPH_WRITE_PARTIAL",
    "INFRA_GRAPH_SCHEMA_INCOMPATIBLE",
    "INFRA_LEXICAL_INDEX_CORRUPT",
    "INFRA_CACHE_STALE_GENERATION",
    "INFRA_CROSS_STORE_VERSION_DIVERGENCE",
    "INFRA_INDEX_CUTOVER_CONFLICT",
    "INFRA_DELETION_VISIBILITY_DEADLINE",
    "INFRA_RECOVERY_SET_INCONSISTENT",
    "INFRA_MANDATORY_AUDIT_BLOCK_EFFECT",
    "INFRA_CROSS_TENANT_HIT",
    "INFRA_ADAPTER_SEMANTIC_UNSUPPORTED",
    "INFRA_RELEASE_PROVENANCE_INVALID",
    "INFRA_RESOURCE_ATTRIBUTION_MISSING",
]

NOT_SELECTED = [
    "Kafka 作为默认工作队列",
    "Event Sourcing 作为全系统事实模型",
    "XA / 2PC",
    "默认多区域 Active-Active",
    "大量微服务与 Service Mesh",
    "Kubernetes 作为本模块完成标准",
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
        (FORMAL, "INFRA_DOC_MISSING"),
        (MIRROR, "INFRA_MIRROR_MISSING"),
        (FORMAL_INDEX, "INFRA_FORMAL_INDEX_MISSING"),
        (MIRROR_INDEX, "INFRA_MIRROR_INDEX_MISSING"),
        (CONTRACT_REGISTRY, "INFRA_CONTRACT_REGISTRY_MISSING"),
    ]:
        if not path.exists():
            findings.append(Finding(code, str(path.relative_to(REPO_ROOT))))

    for appendix in RETIRED_APPENDICES:
        if appendix.exists():
            findings.append(Finding("INFRA_RETIRED_APPENDIX_PRESENT", str(appendix.relative_to(REPO_ROOT))))

    if findings:
        return findings

    content = _read(FORMAL)
    formal_index = _read(FORMAL_INDEX)
    mirror_index = _read(MIRROR_INDEX)
    registry_content = _read(CONTRACT_REGISTRY)

    if FORMAL.read_bytes() != MIRROR.read_bytes():
        findings.append(Finding("INFRA_MIRROR_DRIFT", "formal document and Agent mirror are not byte-identical"))

    for term in [
        "唯一正式 Target 架构文档",
        "原主文档、数据服务附录和一致性生命周期附录中的全部有效设计",
        "Current Inventory",
        "Target Selection",
        "Future Optional",
        "Explicitly Not Selected",
        "Developer / CI Local Adapter Topology",
        "Canonical Server Product Topology",
        "服务端统一后端是产品 Target",
        "Failure Taxonomy",
        "Crash Matrix",
        "Multi-tenant Storage Isolation",
        "Target Code Mapping",
        "Target → Current Evidence",
    ]:
        _require(content, term, "INFRA_COVERAGE_MISSING", findings)

    positions: list[int] = []
    for part in PARTS:
        if content.count(part) != 1:
            findings.append(Finding("INFRA_PART_INVALID", f"{part!r} must appear exactly once"))
        else:
            positions.append(content.index(part))
    if positions != sorted(positions):
        findings.append(Finding("INFRA_PART_ORDER", "normative parts are not ordered"))

    for term in REQUIRED_COMPONENTS:
        _require(content, term, "INFRA_COMPONENT_MISSING", findings)
    for term in REQUIRED_CONTRACTS:
        _require(content, term, "INFRA_CONTRACT_MISSING", findings)
    for term in REQUIRED_PORTS:
        _require(content, term, "INFRA_PORT_MISSING", findings)
    for term in REQUIRED_STATE_MACHINES:
        _require(content, term, "INFRA_STATE_MACHINE_MISSING", findings)
    for term in REQUIRED_FLOWS:
        _require(content, term, "INFRA_FLOW_MISSING", findings)
    for term in REQUIRED_BOUNDARIES:
        _require(content, term, "INFRA_BOUNDARY_MISSING", findings)
    for term in REQUIRED_FAULTS:
        _require(content, term, "INFRA_FAULT_TEST_MISSING", findings)
    for term in REQUIRED_FAILURES:
        _require(content, term, "INFRA_FAILURE_MISSING", findings)
    for term in NOT_SELECTED:
        _require(content, term, "INFRA_NOT_SELECTED_MISSING", findings)

    requirement_ids = [int(value) for value in re.findall(r"ARCH-INFRA-(\d{3})", content)]
    control_ids = [int(value) for value in re.findall(r"RC-INFRA-(\d{3})", content)]
    expected = list(range(1, 65))
    if sorted(requirement_ids) != expected:
        findings.append(Finding("INFRA_REQUIREMENT_REGISTRY", "ARCH-INFRA IDs must be exactly 001..064"))
    if sorted(control_ids) != expected:
        findings.append(Finding("INFRA_CONTROL_REGISTRY", "RC-INFRA IDs must be exactly 001..064"))

    for number in expected:
        for suffix in ["UT", "IT"]:
            test_id = f"INFRA-{number:03d}-{suffix}"
            if test_id not in content:
                findings.append(Finding("INFRA_TEST_MAPPING", f"missing {test_id}"))
        evidence_id = f"EV-INFRA-{number:03d}"
        if evidence_id not in content:
            findings.append(Finding("INFRA_EVIDENCE_MAPPING", f"missing {evidence_id}"))

    if "[`11-infrastructure.md`](./11-infrastructure.md)" not in formal_index:
        findings.append(Finding("INFRA_FORMAL_INDEX_ROUTE", "docs/modules/README.md does not route the single Infrastructure document"))
    if "[`11-infrastructure.md`](./11-infrastructure.md)" not in mirror_index:
        findings.append(Finding("INFRA_MIRROR_INDEX_ROUTE", ".agent/modules/README.md does not route the single Infrastructure mirror"))

    for retired_name in [
        "11-infrastructure-data-services.md",
        "11-infrastructure-consistency-lifecycle.md",
    ]:
        for index_content, label in [(formal_index, "formal index"), (mirror_index, "mirror index")]:
            if retired_name in index_content:
                findings.append(Finding("INFRA_RETIRED_ROUTE", f"{label} still routes {retired_name}"))

    for term in ["单一完整实施级 Target", "唯一正式 Target", "不再维护"]:
        if term not in formal_index:
            findings.append(Finding("INFRA_FORMAL_SINGLE_DOC_GOVERNANCE", f"formal index missing {term}"))

    for term in ["单一完整实施级 Target", "唯一 Target 镜像", "不得寻找或重新创建"]:
        if term not in mirror_index:
            findings.append(Finding("INFRA_MIRROR_SINGLE_DOC_GOVERNANCE", f"mirror index missing {term}"))

    if "status: confirmed-target" not in registry_content:
        findings.append(Finding("INFRA_REGISTRY_STATUS", "Wave 1 registry is not confirmed-target"))

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
