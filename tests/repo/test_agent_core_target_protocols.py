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
        raise RuntimeError("cannot load Agent Core target protocol verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_agent_core_target_protocol_contract() -> None:
    verifier = _load_verifier()
    assert verifier.verify() == []


def test_agent_core_target_docs_are_target_only() -> None:
    paths = [
        REPO_ROOT / "docs/modules/06-agent-core-planning-control.md",
        REPO_ROOT / "docs/modules/06-agent-core-control-protocols.md",
        REPO_ROOT / "docs/modules/06-agent-core-consistency-lifecycle-protocols.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)

    assert "# 35. Current Baseline" not in combined
    assert "# 36. 实现阶段" not in combined
    assert "pending_interrupt_id: str | None" not in combined
    assert "同一 Run 默认只允许一个 PENDING Interrupt" not in combined


def test_agent_core_target_docs_cover_all_requirements_once() -> None:
    paths = [
        REPO_ROOT / "docs/modules/06-agent-core-planning-control.md",
        REPO_ROOT / "docs/modules/06-agent-core-control-protocols.md",
        REPO_ROOT / "docs/modules/06-agent-core-consistency-lifecycle-protocols.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    ids = [int(value) for value in re.findall(r"ARCH-AGENT-(\d{3})", combined)]
    assert sorted(ids) == list(range(1, 81))


def test_agent_core_mirrors_are_byte_identical() -> None:
    names = [
        "06-agent-core-planning-control.md",
        "06-agent-core-control-protocols.md",
        "06-agent-core-consistency-lifecycle-protocols.md",
    ]
    for name in names:
        formal = (REPO_ROOT / "docs/modules" / name).read_bytes()
        mirror = (REPO_ROOT / ".agent/modules" / name).read_bytes()
        assert mirror == formal


def test_agent_run_graph_includes_multi_interrupt_and_publication() -> None:
    main = (REPO_ROOT / "docs/modules/06-agent-core-planning-control.md").read_text(encoding="utf-8")
    assert "pending_interrupt_refs" in main
    assert "create_final_candidate" in main
    assert "prepare_publication" in main
    assert "confirm_delivery" in main


def test_waiting_and_terminal_blocked_are_distinct() -> None:
    control = (REPO_ROOT / "docs/modules/06-agent-core-control-protocols.md").read_text(encoding="utf-8")
    assert "WAITING_CONDITION" in control
    assert "`BLOCKED` 是终态" in control
    assert "CANCELLING" in control
