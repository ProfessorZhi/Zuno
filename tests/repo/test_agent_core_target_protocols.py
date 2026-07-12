from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = REPO_ROOT / "tools/scripts/verify_agent_core_target_protocols.py"
FORMAL = REPO_ROOT / "docs/modules/06-agent-core-planning-control.md"
MIRROR = REPO_ROOT / ".agent/modules/06-agent-core-planning-control.md"


def _load_verifier():
    spec = importlib.util.spec_from_file_location("verify_agent_core_target_protocols", VERIFIER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Agent Core target verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _content() -> str:
    return FORMAL.read_text(encoding="utf-8")


def test_refined_agent_core_target_contract() -> None:
    verifier = _load_verifier()
    assert verifier.verify() == []


def test_only_one_agent_core_target_document_exists() -> None:
    assert FORMAL.exists()
    assert MIRROR.exists()
    for relative in [
        "docs/modules/06-agent-core-control-protocols.md",
        "docs/modules/06-agent-core-consistency-lifecycle-protocols.md",
        ".agent/modules/06-agent-core-control-protocols.md",
        ".agent/modules/06-agent-core-consistency-lifecycle-protocols.md",
    ]:
        assert not (REPO_ROOT / relative).exists()


def test_document_parts_are_complete_and_ordered() -> None:
    content = _content()
    parts = [
        "# Part I：定位与概念架构",
        "# Part II：智能机制与运行流程",
        "# Part III：状态、恢复与一致性概览",
        "# Part IV：目标实现表面与规范索引",
        "# Part V：领域模型、状态转换与决策闭环",
        "# Part VI：规范性控制协议",
        "# Part VII：一致性与生命周期协议",
        "# Part VIII：验证与完成证据",
    ]
    positions = [content.index(part) for part in parts]
    assert positions == sorted(positions)
    assert all(content.count(part) == 1 for part in parts)


def test_unified_document_covers_all_requirements_once() -> None:
    ids = [int(value) for value in re.findall(r"ARCH-AGENT-(\d{3})", _content())]
    assert sorted(ids) == list(range(1, 81))


def test_target_only_and_program_separated() -> None:
    content = _content()
    assert "唯一的正式 Target 架构文档" in content
    assert ".agent/programs/" in content
    assert "Current Baseline" not in content
    assert "具体迁移阶段" in content
    assert "未来 Program 必须以本文及配套规范" not in content


def test_agent_core_mirror_is_byte_identical() -> None:
    assert MIRROR.read_bytes() == FORMAL.read_bytes()


def test_domain_objects_have_storage_decisions() -> None:
    content = _content()
    for object_name, table_name in {
        "ObjectiveOutcome": "agent_objective_outcomes",
        "RunCommand": "agent_run_commands",
        "ControlDecision": "agent_control_decisions",
        "EffectivePolicySnapshot": "agent_effective_policy_snapshots",
        "ResourceClaim": "agent_resource_claims",
        "DomainCommitMarker": "agent_domain_commit_markers",
        "RecoveryWatermark": "agent_recovery_watermarks",
        "ArtifactCandidate": "agent_artifact_candidates",
        "PublicationArtifactBinding": "agent_publication_artifact_bindings",
        "PublicationCorrectionDecision": "agent_publication_correction_decisions",
        "BudgetSettlement": "agent_budget_settlements",
    }.items():
        assert object_name in content
        assert table_name in content


def test_action_artifact_and_command_semantics_are_unambiguous() -> None:
    content = _content()
    assert "ActionLifecycleStatus" in content
    assert "ActionOutcome" in content
    assert "command_sequence_no" in content
    assert "RECONCILED` 代替结果" in content
    assert "发布和撤回属于 Publication 状态" in content
    assert "状态：DRAFT、VALIDATING、VALID、INVALID、SUPERSEDED、PUBLISHED、WITHDRAWN。" not in content


def test_policy_failure_budget_and_requirement_closure() -> None:
    content = _content()
    for term in [
        "Effective Policy Snapshot",
        "Failure Decision Matrix",
        "Budget Ledger",
        "Requirement Enforcement Matrix",
        "AG-NNN-*",
        "EV-AG-NNN",
    ]:
        assert term in content
