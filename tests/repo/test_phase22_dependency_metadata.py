"""PHASE22 dependency metadata truth tests (Task I item 12b).

The committed evidence must reference the CURRENT DeepSeek1 PR #112
candidate head (ce495af2…), never the stale bf4b2cb…, and must keep
dependency_accepted=false while the coordinator state is
REQUEST_WORKER_CHANGES.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = (
    ROOT
    / "docs"
    / "evidence"
    / "goal05-phase22-machine-attested-synthetic-regression"
    / "deepseek2-cc-b34c"
)

CURRENT_DEEPSEEK1_HEAD = "ce495af2a39c01379878a9e2c1bb58d876456b1e"
STALE_DEEPSEEK1_HEAD = "bf4b2cb11b53e78b3a7242df5996e4aed2cc1a4b"


def _evidence(name: str) -> dict:
    return json.loads((EVIDENCE_DIR / name).read_text(encoding="utf-8"))


def test_snapshot_evidence_dependency_metadata() -> None:
    evidence = _evidence("snapshot_activation_evidence.json")
    dependency = evidence["dependency"]
    assert dependency["dependency_pr"] == "112"
    assert dependency["dependency_head_sha"] == CURRENT_DEEPSEEK1_HEAD
    assert dependency["dependency_head_sha"] != STALE_DEEPSEEK1_HEAD
    assert dependency["dependency_accepted"] is False
    assert dependency["knowledge_version_id"] is None


def test_four_profile_evidence_dependency_metadata() -> None:
    evidence = _evidence("four_profile_runtime_evidence.json")
    dependency = evidence["dependency"]
    assert dependency["dependency_pr"] == "112"
    assert dependency["dependency_head_sha"] == CURRENT_DEEPSEEK1_HEAD
    assert dependency["dependency_head_sha"] != STALE_DEEPSEEK1_HEAD
    assert dependency["dependency_accepted"] is False
