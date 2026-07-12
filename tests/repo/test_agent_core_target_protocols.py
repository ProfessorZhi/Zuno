from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = REPO_ROOT / "tools/scripts/verify_agent_core_target_protocols.py"


def _load_verifier():
    spec = importlib.util.spec_from_file_location("verify_agent_core_target_protocols", VERIFIER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Agent Core target verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_unified_agent_core_target_contract() -> None:
    verifier = _load_verifier()
    assert verifier.verify() == []


def test_only_one_agent_core_target_document_exists() -> None:
    assert (REPO_ROOT / "docs/modules/06-agent-core-planning-control.md").exists()
    assert (REPO_ROOT / ".agent/modules/06-agent-core-planning-control.md").exists()
    for relative in [
        "docs/modules/06-agent-core-control-protocols.md",
        "docs/modules/06-agent-core-consistency-lifecycle-protocols.md",
        ".agent/modules/06-agent-core-control-protocols.md",
        ".agent/modules/06-agent-core-consistency-lifecycle-protocols.md",
    ]:
        assert not (REPO_ROOT / relative).exists()


def test_unified_document_covers_all_requirements_once() -> None:
    content = (REPO_ROOT / "docs/modules/06-agent-core-planning-control.md").read_text(encoding="utf-8")
    ids = [int(value) for value in re.findall(r"ARCH-AGENT-(\d{3})", content)]
    assert sorted(ids) == list(range(1, 81))


def test_unified_document_is_target_only_and_program_separated() -> None:
    content = (REPO_ROOT / "docs/modules/06-agent-core-planning-control.md").read_text(encoding="utf-8")
    assert "唯一的正式 Target 架构文档" in content
    assert ".agent/programs/" in content
    assert "# 35. Current Baseline" not in content
    assert "# 36. 实现阶段" not in content
    assert "pending_interrupt_id: str | None" not in content


def test_agent_core_mirror_is_byte_identical() -> None:
    formal = (REPO_ROOT / "docs/modules/06-agent-core-planning-control.md").read_bytes()
    mirror = (REPO_ROOT / ".agent/modules/06-agent-core-planning-control.md").read_bytes()
    assert mirror == formal


def test_unified_document_keeps_control_and_consistency_protocols() -> None:
    content = (REPO_ROOT / "docs/modules/06-agent-core-planning-control.md").read_text(encoding="utf-8")
    for term in [
        "# Part VI：规范性控制协议",
        "# Part VII：一致性与生命周期协议",
        "WAITING_CONDITION",
        "PreparedAction",
        "RecoveryWatermark",
        "ResultValidity",
        "RunOrphanReconciler",
        "prepare_publication",
    ]:
        assert term in content
