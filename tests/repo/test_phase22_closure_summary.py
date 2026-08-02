from __future__ import annotations

def test_phase22_closure_summary_generation() -> None:
    from tools.scripts.generate_phase22_closure_summary import build_phase22_closure_summary

    text = build_phase22_closure_summary()

    assert "PHASE22 Closure Summary" in text
    assert "status: in_progress" in text
    assert "reviewer_approved_count=0" in text
    assert "benchmark_eligible_count=0" in text
    assert "blocked_not_measured" in text
    assert "Program archive and no-active reset are still pending." in text
