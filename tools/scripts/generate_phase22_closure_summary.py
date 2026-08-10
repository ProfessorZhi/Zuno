from __future__ import annotations

import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = REPO_ROOT / "docs/evidence/goal05-phase22-closure-summary.md"
ARCHIVE_ROOT = REPO_ROOT / "docs/history/programs/zuno-canonical-architecture-runtime-realization-v1"
PHASE22_PROGRAM = REPO_ROOT / ".agent/programs/PHASE22_fixed-benchmark-production-readiness-and-closure.md"
REVIEW_PACK_REVIEWED_SUMMARY = REPO_ROOT / "docs/evidence/goal05-phase22-public-benchmark-review-pack/reviewed/review_summary.json"
BLOCKED_BENCHMARK_MANIFEST = REPO_ROOT / "docs/evidence/goal05-phase22-blocked-benchmark/benchmark_manifest.json"


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_rev_parse(ref: str) -> str:
    result = subprocess.run(
        ["git", "rev-parse", ref], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def build_phase22_closure_summary() -> str:
    phase22 = PHASE22_PROGRAM if PHASE22_PROGRAM.exists() else ARCHIVE_ROOT / PHASE22_PROGRAM.name
    reviewed = _read_json(REVIEW_PACK_REVIEWED_SUMMARY)
    benchmark = _read_json(BLOCKED_BENCHMARK_MANIFEST)
    source_sha = _git_rev_parse("HEAD")
    origin_main_sha = _git_rev_parse("origin/main")
    total = reviewed.get("total_cases", 0)
    approved = reviewed.get("reviewer_approved_count", 0)
    eligible = reviewed.get("benchmark_eligible_count", 0)
    rejected = reviewed.get("rejected_or_incomplete_count", 0)
    return "\n".join(
        [
            "# PHASE22 Closure Summary",
            "",
            "status: completed",
            "closure_kind: engineering_program_closure",
            "engineering_closure: completed",
            "measurement: blocked_external",
            "quality: not_yet_proven",
            "production_readiness: not_established",
            "repository_owned_blockers: 0",
            f"source_sha_at_generation: {source_sha}",
            f"origin_main_sha_at_generation: {origin_main_sha}",
            "",
            "## Final Truth",
            "",
            "- PHASE22: `completed`; Program: `completed / archived`; phases: `22/22 completed`.",
            "- Formal Benchmark execution path: available.",
            f"- Fixed Benchmark: `{benchmark.get('status')} / {benchmark.get('measurement_status')}`, actual_case_count={benchmark.get('actual_case_count')}; no formal measured profile.",
            f"- Public Review Pack: {approved}/{total} approved, {eligible}/{total} eligible, {rejected} rejected/incomplete.",
            "- Quality: `not_yet_proven`.",
            "- Production Readiness: `NOT_ESTABLISHED`.",
            "",
            "## Evidence",
            "",
            "- `docs/evidence/goal05-phase22-completion-blockers.md`",
            "- `docs/evidence/goal05-phase22-verification-report.md`",
            "- `docs/evidence/goal05-phase22-blocked-benchmark/benchmark_manifest.json`",
            "- `docs/evidence/goal05-phase22-public-benchmark-review-pack/reviewed/review_summary.json`",
            f"- `{phase22.relative_to(REPO_ROOT).as_posix()}`",
            "- `docs/history/programs/zuno-canonical-architecture-runtime-realization-v1/`",
            "",
            "## Handoff",
            "",
            "当前 Program 已归档。下一阶段独立于 PHASE22：Repository Consolidation + Canonical Target Architecture Deep Design。设计确认后才决定是否建立新的实现 Program；本轮不创建 PHASE23 或新的 Runtime Program。",
            "",
        ]
    )


def main() -> int:
    OUTPUT_PATH.write_text(build_phase22_closure_summary(), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
