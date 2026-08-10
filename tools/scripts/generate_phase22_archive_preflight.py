from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-archive-preflight.md"

PROGRAM_ROOT = REPO_ROOT / ".agent" / "programs"
HISTORY_ROOT = REPO_ROOT / "docs" / "history" / "programs" / "zuno-canonical-architecture-runtime-realization-v1"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _program_file(name: str) -> Path:
    active = PROGRAM_ROOT / name
    if active.exists():
        return active
    return HISTORY_ROOT / name


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
    current = _read_text(_program_file("current.md"))
    checklist = _read_text(_program_file("closure-checklist.md"))
    phase22 = _read_text(_program_file("PHASE22_fixed-benchmark-production-readiness-and-closure.md"))
    source_sha = _git_rev_parse("HEAD")
    no_active = "state: no-active" in current
    completed = "status: completed" in phase22 and "engineering_closure: completed" in phase22

    return "\n".join(
        [
            "# PHASE22 Archive Preflight",
            "",
            f"status: {'completed' if completed and no_active else 'preflight_incomplete'}",
            "closure_kind: engineering_program_closure",
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
            f"- current program state: {'no-active' if no_active else 'active_or_missing'}",
            f"- closure checklist no-active reset complete: {'[x] `.agent/programs/` 恢复' in checklist}",
            f"- PHASE22 engineering closure complete: {completed}",
            "",
            "## Boundary",
            "",
            "- This is a bounded archive boundary snapshot.",
            "- `source_sha_at_generation` records the source tree used to generate this file; the commit that stores this evidence may be newer.",
            "- It records the engineering archive boundary; it does not convert external qualification gaps into PASS.",
            "- External formal runtime, credentials, attestation, production-scale load, DR, and external security/budget qualification remain BLOCKED_EXTERNAL.",
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
