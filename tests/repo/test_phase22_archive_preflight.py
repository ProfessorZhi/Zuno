from __future__ import annotations


def test_phase22_archive_preflight_generation() -> None:
    from tools.scripts.generate_phase22_archive_preflight import build_phase22_archive_preflight

    text = build_phase22_archive_preflight()
    lowered = text.lower()

    assert "PHASE22 Archive Preflight" in text
    assert "status: not_ready_for_archive" in text
    assert "program archive is still blocked" in lowered
    assert "PHASE22 still in progress: True" in text
    assert "docs/evidence/goal05-phase22-verification-report.md" in text
