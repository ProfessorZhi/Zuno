from __future__ import annotations


def test_phase22_verification_report_generation() -> None:
    from tools.scripts.generate_phase22_verification_report import build_phase22_verification_report

    text = build_phase22_verification_report()

    assert "PHASE22 Verification Report" in text
    assert "status: completed" in text
    assert "| Fixed benchmark measurement | BLOCKED_EXTERNAL" in text
    assert "| Public review pack | PASS | 80/80 approved; 80/80 eligible" in text
    assert "Program archive and no-active reset" in text
    assert "engineering_closure: completed" in text
