from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = REPO_ROOT / "tools/scripts/verify_infrastructure_target_protocols.py"
FORMAL = REPO_ROOT / "docs/modules/11-infrastructure.md"
MIRROR = REPO_ROOT / ".agent/modules/11-infrastructure.md"


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


def test_formal_document_and_agent_mirror_are_byte_identical() -> None:
    assert FORMAL.read_bytes() == MIRROR.read_bytes()


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
