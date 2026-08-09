from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-archive-preflight.md"

PROGRAM_ROOT = REPO_ROOT / ".agent" / "programs"
HISTORY_ROOT = REPO_ROOT / "docs" / "history" / "programs" / "zuno-canonical-architecture-runtime-realization-v1"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _git_rev_parse(ref: str) -> str:
    result = subprocess.run(
        ["git", "rev-parse", ref],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def build_phase22_archive_preflight() -> str:
    current = _read_text(PROGRAM_ROOT / "current.md")
    checklist = _read_text(PROGRAM_ROOT / "closure-checklist.md")
    phase22 = _read_text(PROGRAM_ROOT / "PHASE22_fixed-benchmark-production-readiness-and-closure.md")
    source_sha = _git_rev_parse("HEAD")

    return "\n".join(
        [
            "# PHASE22 Archive Preflight",
            "",
            "status: not_ready_for_archive",
            f"source_sha_at_generation: {source_sha}",
            "",
            "## Archive Target",
            "",
            f"- program_root: `{PROGRAM_ROOT.relative_to(REPO_ROOT).as_posix()}`",
            f"- history_root: `{HISTORY_ROOT.relative_to(REPO_ROOT).as_posix()}`",
            "",
            "## Required Copy Set",
            "",
            "- .agent/programs/current.md",
            "- .agent/programs/closure-checklist.md",
            "- .agent/programs/implementation-roadmap.md",
            "- .agent/programs/program-manifest.yaml",
            "- .agent/programs/PHASE01_*.md ... PHASE22_*.md",
            "- .agent/programs/work-products/**",
            "- docs/evidence/goal05-phase22-closure-summary.md",
            "- docs/evidence/goal05-phase22-verification-report.md",
            "- docs/evidence/goal05-phase22-archive-preflight.md",
            "",
            "## Current Blockers",
            "",
            f"- current program state: {'active' if 'state: active' in current else 'missing'}",
            f"- closure checklist no-active reset unchecked: {'[ ] `.agent/programs/` 恢复 no-active' in checklist}",
            f"- PHASE22 still in progress: {'PHASE22 remains `in_progress`' in phase22}",
            "",
            "## Boundary",
            "",
            "- This is a preflight snapshot only.",
            "- `source_sha_at_generation` records the source tree used to generate this file; the commit that stores this evidence may be newer.",
            "- It does not mutate program state or perform archive copy.",
            "- Program archive is still blocked by missing measured runtime, formal credentials/attestations, incomplete final verification, and unresolved worktree ownership.",
            "",
        ]
    )


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        build_phase22_archive_preflight(), encoding="utf-8", newline="\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
