from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-verification-report.md"
PROGRAM = REPO_ROOT / ".agent" / "programs" / "PHASE22_fixed-benchmark-production-readiness-and-closure.md"
CLOSURE_SUMMARY = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-closure-summary.md"
COMPLETION_BLOCKERS = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-completion-blockers.md"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_phase22_verification_report() -> str:
    program_text = _read_text(PROGRAM)
    closure_text = _read_text(CLOSURE_SUMMARY)
    blockers_text = _read_text(COMPLETION_BLOCKERS)

    return "\n".join(
        [
            "# PHASE22 Verification Report",
            "",
            "status: in_progress",
            "report_kind: verification_snapshot",
            "",
            "## Verified Current Facts",
            "",
            "- PHASE22 remains `in_progress`.",
            "- Fixed benchmark remains `BLOCKED / blocked_not_measured`.",
            "- Public benchmark review pack remains `REVIEW_REQUIRED`.",
            "- Program remains `active`.",
            "- No archive / no-active reset has been performed.",
            "",
            "## Evidence Sources",
            "",
            f"- `{CLOSURE_SUMMARY.relative_to(REPO_ROOT).as_posix()}`",
            f"- `{COMPLETION_BLOCKERS.relative_to(REPO_ROOT).as_posix()}`",
            f"- `{PROGRAM.relative_to(REPO_ROOT).as_posix()}`",
            "",
            "## Completion Boundary",
            "",
            f"- program boundary phrase: {'PHASE22 remains `in_progress`' if 'PHASE22 remains `in_progress`' in program_text else 'missing'}",
            f"- closure boundary phrase: {'Program archive and no-active reset are still pending.' if 'Program archive and no-active reset are still pending.' in closure_text else 'missing'}",
            f"- blocker boundary phrase: {'PHASE22 当前不能关闭为 `completed`' if 'PHASE22 当前不能关闭为 `completed`' in blockers_text else 'missing'}",
            "",
            "## Verification Commands",
            "",
            "```bash",
            "python tools/scripts/verify_current_program.py",
            "python tools/scripts/verify_phase22_completion_blockers.py",
            "python tools/scripts/verify_docs_entrypoints.py",
            "python -m pytest -q tests/repo/test_phase22_closure_summary.py tests/platform/test_langsmith_trace_adapter.py tests/platform/test_langsmith_adapter_factory.py tests/evals/test_canonical_profile_runners.py::test_09f_standard_adapter_trace_delivery_failure_fails_closed -p no:cacheprovider --tb=short",
            "```",
            "",
            "## Known Remaining Blockers",
            "",
            "- fixed benchmark measured pass",
            "- reviewer-approved eligible case set",
            "- full final verification",
            "- program archive / no-active reset",
            "",
            "## Boundary",
            "",
            "- This report does not claim PHASE22 completed.",
            "- It is a reproducible snapshot of the current verification boundary.",
            "",
        ]
    )


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(build_phase22_verification_report(), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
