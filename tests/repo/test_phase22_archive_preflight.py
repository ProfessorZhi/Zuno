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
    assert "status: not_ready_for_archive" in text
    assert f"source_sha_at_generation: {source_sha}" in text
    assert "program archive is still blocked" in lowered
    assert "PHASE22 still in progress: True" in text
    assert "docs/evidence/goal05-phase22-verification-report.md" in text
