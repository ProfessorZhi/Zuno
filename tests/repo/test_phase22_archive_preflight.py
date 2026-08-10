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


def test_phase22_archive_preflight_generation() -> None:
    from tools.scripts.generate_phase22_archive_preflight import build_phase22_archive_preflight

    text = build_phase22_archive_preflight()
    lowered = text.lower()
    source_sha = _git_rev_parse("HEAD")

    assert "PHASE22 Archive Preflight" in text
    assert "status: completed" in text
    assert f"source_sha_at_generation: {source_sha}" in text
    assert "closure_kind: engineering_program_closure" in text
    assert "current program state: no-active" in text
    assert "PHASE22 engineering closure complete: True" in text
    assert "docs/evidence/goal05-phase22-verification-report.md" in text
