from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = REPO_ROOT / "tools/scripts/verify_infrastructure_target_protocols.py"
FORMAL = REPO_ROOT / "docs/modules/11-infrastructure.md"
MIRROR = REPO_ROOT / ".agent/modules/11-infrastructure.md"
RETIRED_APPENDICES = [
    REPO_ROOT / "docs/modules/11-infrastructure-data-services.md",
    REPO_ROOT / ".agent/modules/11-infrastructure-data-services.md",
    REPO_ROOT / "docs/modules/11-infrastructure-consistency-lifecycle.md",
    REPO_ROOT / ".agent/modules/11-infrastructure-consistency-lifecycle.md",
]


def _load_verifier():
    spec = importlib.util.spec_from_file_location("verify_infrastructure_target_protocols", VERIFIER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_infrastructure_target_verifier_passes() -> None:
    verifier = _load_verifier()
    assert verifier.verify() == []


def test_single_formal_document_and_mirror_are_byte_identical() -> None:
    assert FORMAL.read_bytes() == MIRROR.read_bytes()
    for appendix in RETIRED_APPENDICES:
        assert not appendix.exists()


def test_document_is_single_detailed_target_architecture() -> None:
    content = FORMAL.read_text(encoding="utf-8")
    for term in [
        "唯一正式 Target 架构文档",
        "原主文档、数据服务附录和一致性生命周期附录中的全部有效设计",
        "# Part I：定位、目标与架构选择",
        "# Part II：概念架构、拓扑与完整流程",
        "# Part III：核心 Contract 与事实边界",
        "# Part IV：数据服务组件设计",
        "# Part V：状态机与一致性生命周期",
        "# Part VI：失败、安全、恢复与运维",
        "# Part VII：目标实现规格",
        "# Part VIII：Requirement、测试与完成证据",
    ]:
        assert term in content


def test_current_target_future_and_not_selected_are_explicit() -> None:
    content = FORMAL.read_text(encoding="utf-8")
    for term in [
        "Current Inventory",
        "Target Selection",
        "Future Optional",
        "Explicitly Not Selected",
        "Kafka 作为默认工作队列",
        "Event Sourcing 作为全系统事实模型",
        "XA / 2PC",
        "默认多区域 Active-Active",
        "大量微服务与 Service Mesh",
        "Kubernetes 作为本模块完成标准",
    ]:
        assert term in content


def test_components_are_connected_by_complete_flows() -> None:
    content = FORMAL.read_text(encoding="utf-8")
    for term in [
        "PostgreSQL",
        "RabbitMQ",
        "Object Store / MinIO",
        "LangGraph Checkpointer",
        "Milvus",
        "Neo4j",
        "BM25 / Search",
        "Redis",
        "文档摄取与索引构建流程",
        "在线查询流程",
        "异步工作流程",
        "Cross-store Publish Protocol",
        "Cross-store Deletion",
        "Recovery Set 与灾难恢复流程",
    ]:
        assert term in content


def test_infrastructure_does_not_claim_domain_ownership() -> None:
    content = FORMAL.read_text(encoding="utf-8")
    for term in [
        "AgentRun、PlanVersion、StepRun 与 RunOutcome 的业务状态",
        "Security Authorization、Approval、Revocation 与 Policy 结论",
        "KnowledgeVersion、MemoryVersion 和 IndexManifest 的领域 Acceptance",
        "Tool 是否允许执行以及 Effect 是否业务成功",
        "Infrastructure owns the capability to run a service reliably",
        "Domain modules own the meaning of facts",
    ]:
        assert term in content


def test_storage_and_checkpoint_boundaries_are_preserved() -> None:
    content = FORMAL.read_text(encoding="utf-8")
    for term in [
        "PostgreSQL 保存领域事实",
        "LangGraph Checkpointer 保存图控制状态",
        "Object Store 保存大型不可变 Payload",
        "Generation、Fencing、RecoveryWatermark 与 Outbox",
        "Checkpoint 不能替代 Domain Commit",
        "Queue ACK != Tool Effect Success",
        "IndexWriteReceipt != IndexManifest Accepted",
    ]:
        assert term in content


def test_core_contracts_and_ports_are_complete() -> None:
    content = FORMAL.read_text(encoding="utf-8")
    for term in [
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
        "DeletionVerification",
        "RecoverySetManifest",
        "AuditDurabilityRequirement",
        "TenantIsolationProfile",
        "ServiceCompatibilityEntry",
        "AdapterConformanceProfile",
        "ReleaseManifest",
        "ResourceUsageAttribution",
        "VectorIndexRuntimePort",
        "GraphIndexRuntimePort",
        "LexicalIndexRuntimePort",
        "CacheAccelerationPort",
    ]:
        assert term in content


def test_state_machines_and_crash_matrix_are_complete() -> None:
    content = FORMAL.read_text(encoding="utf-8")
    for term in [
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
        "Crash Matrix",
    ]:
        assert term in content


def test_vector_graph_search_cache_failures_are_explicit() -> None:
    content = FORMAL.read_text(encoding="utf-8")
    for term in [
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
    ]:
        assert term in content


def test_required_fault_tests_are_named() -> None:
    content = FORMAL.read_text(encoding="utf-8")
    for term in [
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
    ]:
        assert term in content


def test_requirement_control_test_and_evidence_registry_is_complete() -> None:
    content = FORMAL.read_text(encoding="utf-8")
    for number in range(1, 65):
        assert content.count(f"ARCH-INFRA-{number:03d}") == 1
        assert content.count(f"RC-INFRA-{number:03d}") == 1
        assert f"INFRA-{number:03d}-UT" in content
        assert f"INFRA-{number:03d}-IT" in content
        assert f"EV-INFRA-{number:03d}" in content


def test_target_code_mapping_uses_platform_boundary() -> None:
    content = FORMAL.read_text(encoding="utf-8")
    assert "src/backend/zuno/platform/" in content
    assert "不新增 `zuno/infrastructure` 顶层" in content
    for term in [
        "database/",
        "storage/",
        "jobs/",
        "checkpoint/",
        "coordination/",
        "data_services/",
        "operations/",
        "network/",
        "release/",
    ]:
        assert term in content
