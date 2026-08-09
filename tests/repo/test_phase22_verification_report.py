from __future__ import annotations


def test_phase22_verification_report_generation() -> None:
    from tools.scripts.generate_phase22_verification_report import build_phase22_verification_report

    text = build_phase22_verification_report()

    assert "PHASE22 Verification Report" in text
    assert "status: in_progress" in text
    assert "Fixed benchmark remains `BLOCKED / blocked_not_measured`." in text
    assert "Public benchmark review pack is `PASS` with `80/80` approved and `80/80` eligible cases." in text
    assert "program archive / no-active reset" in text
    assert "This report does not claim PHASE22 completed." in text
