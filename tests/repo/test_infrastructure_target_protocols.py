from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = REPO_ROOT / "tools/scripts/verify_infrastructure_target_protocols.py"
FORMAL = REPO_ROOT / "docs/modules/11-infrastructure.md"
MIRROR = REPO_ROOT / ".agent/modules/11-infrastructure.md"
DATA_FORMAL = REPO_ROOT / "docs/modules/11-infrastructure-data-services.md"
DATA_MIRROR = REPO_ROOT / ".agent/modules/11-infrastructure-data-services.md"
LIFECYCLE_FORMAL = REPO_ROOT / "docs/modules/11-infrastructure-consistency-lifecycle.md"
LIFECYCLE_MIRROR = REPO_ROOT / ".agent/modules/11-infrastructure-consistency-lifecycle.md"
CONTRACT_REGISTRY = REPO_ROOT / "docs/governance/wave1-cross-module-contract-registry.md"


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


def test_formal_documents_and_agent_mirrors_are_byte_identical() -> None:
    assert FORMAL.read_bytes() == MIRROR.read_bytes()
    assert DATA_FORMAL.read_bytes() == DATA_MIRROR.read_bytes()
    assert LIFECYCLE_FORMAL.read_bytes() == LIFECYCLE_MIRROR.read_bytes()


def test_current_target_future_and_not_selected_are_explicit() -> None:
    content = FORMAL.read_text(encoding="utf-8")
    for term in [
        "Current Inventory",
        "Target Selection",
        "Future Optional",
        "Explicitly Not Selected",
        "PostgreSQL、Redis、MinIO、RabbitMQ、Kafka、Kubernetes",
    ]:
        assert term in content


def test_infrastructure_does_not_claim_domain_ownership() -> None:
    content = FORMAL.read_text(encoding="utf-8")
    for term in [
        "AgentRun、PlanVersion、StepRun 的业务状态",
        "Security Authorization / Approval / Revocation 结论",
        "Model Routing Decision",
        "Eval Verdict",
        "Infrastructure 不决定谁有权限",
    ]:
        assert term in content


def test_agent_core_storage_boundary_is_preserved() -> None:
    content = FORMAL.read_text(encoding="utf-8")
    for term in [
        "PostgreSQL 保存领域事实",
        "LangGraph Checkpointer 保存图控制状态",
        "Object Store 保存大型不可变 Payload",
        "Generation、Fencing、RecoveryWatermark 与 Outbox",
        "Checkpoint 不能替代 Domain Commit",
    ]:
        assert term in content


def test_required_state_machines_and_crash_matrix_exist() -> None:
    content = FORMAL.read_text(encoding="utf-8")
    for term in [
        "ObjectCommit State Machine",
        "QueueMessage / Delivery State Machine",
        "WorkerLease State Machine",
        "MigrationRun State Machine",
        "BackupRun State Machine",
        "RestoreRun State Machine",
        "Drain State Machine",
        "CapacityReservation",
        "Crash Matrix",
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
        "Migration Rollback",
        "Backup Corruption",
        "Restore Failure",
        "Clock Skew",
        "Drain Deadline",
        "Capacity Exhaustion",
    ]:
        assert term in content


def test_requirement_control_test_and_evidence_registry_is_complete() -> None:
    content = FORMAL.read_text(encoding="utf-8")
    for number in range(1, 49):
        assert content.count(f"ARCH-INFRA-{number:03d}") == 1
        assert content.count(f"RC-INFRA-{number:03d}") == 1
        assert f"INFRA-{number:03d}-UT" in content
        assert f"INFRA-{number:03d}-IT" in content
        assert f"EV-INFRA-{number:03d}" in content


def test_expensive_defaults_are_explicitly_not_selected() -> None:
    content = FORMAL.read_text(encoding="utf-8")
    for term in [
        "Kafka 作为默认工作队列",
        "Event Sourcing 作为全系统事实模型",
        "XA / 2PC",
        "默认多区域 Active-Active",
        "大量微服务与 Service Mesh",
        "Kubernetes 作为本模块完成标准",
    ]:
        assert term in content


def test_data_service_component_coverage_and_ownership_are_explicit() -> None:
    content = DATA_FORMAL.read_text(encoding="utf-8")
    for term in [
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
        "authoritative",
        "rebuildable",
        "Infrastructure 不能决定 AgentRun 是否成功",
    ]:
        assert term in content


def test_derived_index_lifecycle_and_cross_store_protocol_are_explicit() -> None:
    content = DATA_FORMAL.read_text(encoding="utf-8")
    for term in [
        "DerivedIndexReplica State Machine",
        "Cross-store Publish Protocol",
        "IndexWriteReceipt",
        "IndexManifest",
        "generation/CAS",
        "不使用 2PC",
        "FAILED/QUARANTINED",
        "STALE/REBUILDING",
    ]:
        assert term in content


def test_vector_graph_search_cache_failures_and_fault_tests_are_named() -> None:
    content = DATA_FORMAL.read_text(encoding="utf-8")
    for term in [
        "INFRA_VECTOR_WRITE_PARTIAL",
        "INFRA_VECTOR_SCHEMA_INCOMPATIBLE",
        "INFRA_GRAPH_WRITE_PARTIAL",
        "INFRA_GRAPH_SCHEMA_INCOMPATIBLE",
        "INFRA_LEXICAL_INDEX_CORRUPT",
        "INFRA_CACHE_STALE_GENERATION",
        "INFRA_CROSS_STORE_VERSION_DIVERGENCE",
        "Milvus Write-Then-Crash Before Manifest Commit",
        "Neo4j Commit-Then-Crash Before Manifest Commit",
        "Tenant Filter Omission / Cross-tenant Hit",
        "PITR with Stale Derived Indexes",
    ]:
        assert term in content


def test_data_service_requirement_registry_is_complete() -> None:
    content = DATA_FORMAL.read_text(encoding="utf-8")
    for number in range(1, 13):
        assert content.count(f"ARCH-INFRA-DS-{number:03d}") == 1
        assert f"INFRA-DS-{number:03d}-UT" in content
        assert f"INFRA-DS-{number:03d}-IT" in content
        assert f"EV-INFRA-DS-{number:03d}" in content


def test_lifecycle_contracts_cover_publish_delete_recovery_and_audit() -> None:
    content = LIFECYCLE_FORMAL.read_text(encoding="utf-8")
    for term in [
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
    ]:
        assert term in content


def test_lifecycle_contracts_cover_isolation_upgrade_conformance_and_release() -> None:
    content = LIFECYCLE_FORMAL.read_text(encoding="utf-8")
    for term in [
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
        "Network Plane",
        "SBOM",
    ]:
        assert term in content


def test_lifecycle_failure_and_fault_catalog_is_complete() -> None:
    content = LIFECYCLE_FORMAL.read_text(encoding="utf-8")
    for term in [
        "INFRA_INDEX_CUTOVER_GENERATION_CONFLICT",
        "INFRA_DELETION_VISIBILITY_DEADLINE",
        "INFRA_RECOVERY_SET_INCONSISTENT",
        "INFRA_MANDATORY_AUDIT_BLOCK_EFFECT",
        "INFRA_CROSS_TENANT_HIT",
        "INFRA_ADAPTER_SEMANTIC_UNSUPPORTED",
        "INFRA_RELEASE_PROVENANCE_INVALID",
        "INFRA_RESOURCE_ATTRIBUTION_MISSING",
        "Cutover Receipt Lost After Alias Switch",
        "Legal Hold Arrives During Purge",
        "PITR With Ahead / Behind Derived Index",
        "Audit Committed Before Tool Effect Crash",
        "Network Partition With Stale Worker",
    ]:
        assert term in content


def test_lifecycle_requirement_registry_is_complete() -> None:
    content = LIFECYCLE_FORMAL.read_text(encoding="utf-8")
    for number in range(1, 25):
        assert content.count(f"ARCH-INFRA-LC-{number:03d}") == 1
        assert f"INFRA-LC-{number:03d}-UT" in content
        assert f"INFRA-LC-{number:03d}-IT" in content
        assert f"EV-INFRA-LC-{number:03d}" in content


def test_wave1_contract_registry_has_shared_contract_ownership() -> None:
    content = CONTRACT_REGISTRY.read_text(encoding="utf-8")
    for term in [
        "status: confirmed-target",
        "previous_status: field-frozen-pending-merge",
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
    ]:
        assert term in content


def test_wave1_registry_resolves_receipt_and_prepared_action_boundaries() -> None:
    content = CONTRACT_REGISTRY.read_text(encoding="utf-8")
    for term in [
        "PreparedAction Ownership 决议建议",
        "CONFLICT_REQUIRES_DECISION",
        "Queue ACK != Tool Effect Success",
        "Lease Release != Tool Effect Success",
        "Checkpoint Commit != Domain Commit",
        "Failure Ownership Matrix",
        "Wave 1 合并前审计清单",
        "ALIGNED_PENDING_FIELDS",
    ]:
        assert term in content


def test_wave1_contract_requirement_registry_is_complete() -> None:
    content = CONTRACT_REGISTRY.read_text(encoding="utf-8")
    for number in range(1, 11):
        assert content.count(f"ARCH-XMOD-{number:03d}") == 1
        assert f"XMOD-{number:03d}-UT" in content
        assert f"XMOD-{number:03d}-IT" in content
        assert f"EV-XMOD-{number:03d}" in content
