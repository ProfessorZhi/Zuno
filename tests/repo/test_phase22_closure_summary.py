from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _git_rev_parse(ref: str) -> str:
    result = subprocess.run(
        ["git", "rev-parse", ref],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def test_phase22_closure_summary_generation() -> None:
    from tools.scripts.generate_phase22_closure_summary import build_phase22_closure_summary

    text = build_phase22_closure_summary()
    source_sha = _git_rev_parse("HEAD")
    origin_main_sha = _git_rev_parse("origin/main")

    assert "PHASE22 Closure Summary" in text
    assert "status: completed" in text
    assert f"source_sha_at_generation: {source_sha}" in text
    assert f"origin_main_sha_at_generation: {origin_main_sha}" in text
    assert "Public Review Pack: 80/80 approved, 80/80 eligible, 0 rejected/incomplete." in text
    assert "blocked_not_measured" in text
    assert "Program: `completed / archived`" in text
