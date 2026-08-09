from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-closure-summary.md"
PHASE22_PROGRAM = REPO_ROOT / ".agent" / "programs" / "PHASE22_fixed-benchmark-production-readiness-and-closure.md"
COMPLETION_BLOCKERS = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-completion-blockers.md"
REVIEW_PACK_INTEGRITY = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-public-benchmark-review-pack" / "integrity_report.json"
REVIEW_PACK_APPROVAL = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-public-benchmark-review-pack" / "approval_summary.json"
REVIEW_PACK_REVIEWED_SUMMARY = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-public-benchmark-review-pack" / "reviewed" / "review_summary.json"
BLOCKED_BENCHMARK_MANIFEST = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-blocked-benchmark" / "benchmark_manifest.json"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(_read_text(path))


def _git_rev_parse(ref: str) -> str:
    result = subprocess.run(
        ["git", "rev-parse", ref],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _extract_phrase(text: str, phrase: str) -> str:
    return phrase if phrase in text else "missing"


def build_phase22_closure_summary() -> str:
    program_text = _read_text(PHASE22_PROGRAM)
    blockers_text = _read_text(COMPLETION_BLOCKERS)
    integrity = _read_json(REVIEW_PACK_INTEGRITY)
    approval = _read_json(REVIEW_PACK_APPROVAL)
    reviewed_summary = _read_json(REVIEW_PACK_REVIEWED_SUMMARY)
    benchmark = _read_json(BLOCKED_BENCHMARK_MANIFEST)

    source_sha = _git_rev_parse("HEAD")
    origin_main_sha = _git_rev_parse("origin/main")

    lines = [
        "# PHASE22 Closure Summary",
        "",
        "status: in_progress",
        f"source_sha_at_generation: {source_sha}",
        f"origin_main_sha_at_generation: {origin_main_sha}",
        "",
        "## Current Truth",
        "",
        f"- PHASE22 status phrase: {_extract_phrase(program_text, 'PHASE22 remains `in_progress`')}",
        f"- full final verification phrase: {_extract_phrase(program_text, 'full final verification')}",
        f"- program archive phrase: {_extract_phrase(program_text, 'program archive')}",
        f"- blocked benchmark status: {benchmark.get('status')}",
        f"- blocked benchmark measurement_status: {benchmark.get('measurement_status')}",
        f"- review pack integrity_status: {integrity.get('overall_status')}",
        f"- review pack overall_status: {reviewed_summary.get('overall_status')}",
        f"- review pack measurement_state: {reviewed_summary.get('measurement_state')}",
        f"- review pack reviewer_approved_count: {reviewed_summary.get('reviewer_approved_count')}",
        f"- review pack benchmark_eligible_count: {reviewed_summary.get('benchmark_eligible_count')}",
        f"- review pack rejected_or_incomplete_count: {reviewed_summary.get('rejected_or_incomplete_count')}",
        "",
        "## Remaining Blockers",
        "",
        f"- benchmark blocker: {_extract_phrase(blockers_text, 'Fixed Benchmark 仍为 `BLOCKED / blocked_not_measured`')}",
        f"- review blocker: reviewer_approved_count={reviewed_summary.get('reviewer_approved_count')}, benchmark_eligible_count={reviewed_summary.get('benchmark_eligible_count')}",
        f"- completion blocker gate: {_extract_phrase(blockers_text, 'PHASE22 当前不能关闭为 `completed`')}",
        f"- program archive blocker: {_extract_phrase(blockers_text, 'Program 仍为 `active`')}",
        "",
        "## Evidence",
        "",
        f"- `{BLOCKED_BENCHMARK_MANIFEST.relative_to(REPO_ROOT).as_posix()}`",
        f"- `{COMPLETION_BLOCKERS.relative_to(REPO_ROOT).as_posix()}`",
        f"- `{REVIEW_PACK_INTEGRITY.relative_to(REPO_ROOT).as_posix()}`",
        f"- `{REVIEW_PACK_APPROVAL.relative_to(REPO_ROOT).as_posix()}`",
        f"- `{REVIEW_PACK_REVIEWED_SUMMARY.relative_to(REPO_ROOT).as_posix()}`",
        f"- `{PHASE22_PROGRAM.relative_to(REPO_ROOT).as_posix()}`",
        "",
        "## Known Limitations",
        "",
        "- This report does not claim PHASE22 completed.",
        "- It is a reproducible closure snapshot for the current in-progress state.",
        "- `source_sha_at_generation` records the source tree used to generate this file; the commit that stores this evidence may be newer.",
        "- Program archive and no-active reset are still pending.",
        "- Current review is partial because 28 cases remain incomplete.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(build_phase22_closure_summary(), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
