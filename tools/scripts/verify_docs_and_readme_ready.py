from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_GROUP_PATHS = {
    "README.md",
    "docs/README.md",
    "docs/architecture/",
    "docs/architecture/README.md",
    "docs/architecture/current-architecture.md",
    "docs/architecture/decisions/README.md",
    "docs/architecture/decisions/0002-rename-zuno-to-zuno.md",
    "docs/architecture/decisions/0002-retire-compat-namespace.md",
    "docs/architecture/phases/README.md",
    "docs/architecture/plans/rag-local-eval-scheme.md",
    "docs/architecture/phases/phase-04-local-eval-strengthening.md",
    "docs/architecture/phases/phase-05-docs-and-public-explanation-sync.md",
    "docs/architecture/phases/phase-06-agent-graphrag-pluginization.md",
    "docs/architecture/specs/architecture-upgrade-2026-06.md",
    "docs/architecture/specs/enterprise-retrieval-governance.md",
    "docs/architecture/specs/platform-evolution-and-future-direction.md",
    "docs/development/README.md",
    "docs/development/backend-layering-guidelines.md",
    "docs/development/github-publish-boundary.md",
    "docs/development/public-demo-acceptance.md",
    "docs/development/public-demo-evidence.md",
    "docs/development/public-demo-runbook.md",
    "docs/development/public-release-checklist.md",
    "docs/development/public-release-staging-plan.md",
    "docs/reference/core.md",
    "docs/reference/zuno.md",
}
EXCLUDED_LOCAL_PATHS = {
    "docs/superpowers/",
    "docs/prototypes/",
    "apps/web/AGENTS.md",
}


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _extract_preview_paths(output: str) -> set[str]:
    paths: set[str] = set()
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            paths.add(stripped[2:])
    return paths


def _extract_stage_dry_run_paths(output: str) -> set[str]:
    paths: set[str] = set()
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            item = stripped[2:].strip()
            status, sep, remainder = item.partition(" ")
            if sep and set(status) <= {"M", "A", "D", "R", "C", "U", "?"}:
                item = remainder.strip()
            paths.add(item)
    return paths


def _strip_excluded_local(paths: set[str]) -> set[str]:
    return {
        path
        for path in paths
        if not any(path == prefix or path.startswith(prefix) for prefix in EXCLUDED_LOCAL_PATHS)
    }


def main() -> int:
    preview = _run(["python", "tools/scripts/preview_public_release_group.py", "docs_and_readme"])
    preview_stat = _run(
        ["python", "tools/scripts/preview_public_release_group.py", "docs_and_readme", "--stat"]
    )
    dry_run = _run(
        ["python", "tools/scripts/preview_public_release_stage_dry_run.py", "docs_and_readme"]
    )
    audit = _run(["python", "tools/scripts/audit_public_release.py"])

    if preview.returncode != 0:
        print(preview.stderr.strip() or preview.stdout.strip() or "preview failed")
        return 1
    if preview_stat.returncode != 0:
        print(preview_stat.stderr.strip() or preview_stat.stdout.strip() or "preview --stat failed")
        return 1
    if dry_run.returncode != 0:
        print(dry_run.stderr.strip() or dry_run.stdout.strip() or "stage dry run failed")
        return 1
    if audit.returncode != 0:
        print(audit.stdout.strip() or audit.stderr.strip() or "public release audit failed")
        return 1

    preview_paths = _strip_excluded_local(_extract_preview_paths(preview.stdout))
    dry_run_paths = _strip_excluded_local(_extract_stage_dry_run_paths(dry_run.stdout))

    errors: list[str] = []
    unexpected_preview = sorted(preview_paths - EXPECTED_GROUP_PATHS)
    unexpected_dry_run = sorted(dry_run_paths - EXPECTED_GROUP_PATHS)
    if unexpected_preview:
        errors.append(
            "preview paths escaped docs_and_readme allowed set: "
            f"unexpected={unexpected_preview}"
        )
    if unexpected_dry_run:
        errors.append(
            "stage dry run paths escaped docs_and_readme allowed set: "
            f"unexpected={unexpected_dry_run}"
        )
    for excluded in EXCLUDED_LOCAL_PATHS:
        if excluded in preview_paths or excluded in dry_run_paths:
            errors.append(f"excluded local path appeared in docs_and_readme readiness check: {excluded}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("docs_and_readme readiness check failed.")
        return 1

    print("docs_and_readme readiness check passed.")
    print(f"preview_count={len(preview_paths)}")
    print(f"stage_dry_run_count={len(dry_run_paths)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
