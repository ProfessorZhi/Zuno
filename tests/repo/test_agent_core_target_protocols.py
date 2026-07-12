from __future__ import annotations

import importlib.util
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


def test_agent_core_target_protocol_is_target_only_and_complete() -> None:
    formal = (REPO_ROOT / "docs/modules/06-agent-core-control-protocols.md").read_text(encoding="utf-8")

    assert "本文只定义 Target" in formal
    assert "GeneralAgent" not in formal
    assert "Legacy Adapter" not in formal

    for requirement_no in range(33, 61):
        assert f"ARCH-AGENT-{requirement_no:03d}" in formal


def test_agent_core_target_protocol_mirror_is_byte_identical() -> None:
    formal = (REPO_ROOT / "docs/modules/06-agent-core-control-protocols.md").read_bytes()
    mirror = (REPO_ROOT / ".agent/modules/06-agent-core-control-protocols.md").read_bytes()
    assert mirror == formal
