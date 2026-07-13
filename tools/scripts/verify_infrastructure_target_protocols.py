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
    ]:
        if not path.exists():
            findings.append(Finding(code, str(path.relative_to(REPO_ROOT))))

    if findings:
        return findings

    content = _read(FORMAL)

    if FORMAL.read_bytes() != MIRROR.read_bytes():
        findings.append(Finding("INFRA_MIRROR_DRIFT", "formal document and Agent mirror are not byte-identical"))

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
        "Local-first Topology",
        "Enterprise Topology",
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

    for forbidden in [
        "PostgreSQL 已是 Current",
        "RabbitMQ 已是 Current",
        "MinIO 已是 Current",
        "Kubernetes 已是 Current",
        "production ready 已完成",
    ]:
        if forbidden in content:
            findings.append(Finding("INFRA_CURRENT_PROMOTION", f"forbidden unsupported statement: {forbidden}"))

    formal_index = _read(FORMAL_INDEX)
    mirror_index = _read(MIRROR_INDEX)
    if "[11-infrastructure.md](./11-infrastructure.md)" not in formal_index:
        findings.append(Finding("INFRA_FORMAL_INDEX_ROUTE", "docs/modules/README.md does not route Infrastructure"))
    if "[11-infrastructure.md](./11-infrastructure.md)" not in mirror_index:
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
