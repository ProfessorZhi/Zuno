from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_PUBLIC_DOC_LINKS = [
    "./src/backend/zuno/evals/rag_eval/runs/",
    "/src/backend/zuno/evals/rag_eval/runs/",
]

PUBLIC_DOC_FILES = [
    REPO_ROOT / "README.md",
    REPO_ROOT / "docs" / "README.md",
    REPO_ROOT / "docs" / "architecture" / "current-architecture.md",
    REPO_ROOT / "docs" / "development" / "public-demo-runbook.md",
    REPO_ROOT / "docs" / "development" / "public-demo-evidence.md",
    REPO_ROOT / "docs" / "development" / "public-demo-acceptance.md",
]

FORBIDDEN_PUBLIC_INDEX_MENTIONS = {
    REPO_ROOT / "README.md": [
        "./superpowers/README.md",
        "└─ superpowers/",
    ],
    REPO_ROOT / "docs" / "README.md": [
        "./superpowers/README.md",
    ],
}

SUSPICIOUS_STATUS_PREFIXES = [
    ".agent/",
    ".agentmd",
    ".local/",
    "docs/superpowers/specs/",
    "apps/web/AGENTS.md",
    "infra/docker/docker_config.local.yaml",
    ".local/config/zuno/",
    ".local/evals/zuno/rag_eval/runs/",
    ".local/evals/zuno/rag_eval/corpus/",
]


@dataclass
class AuditResult:
    errors: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def audit_public_docs() -> AuditResult:
    errors: list[str] = []
    warnings: list[str] = []

    for path in PUBLIC_DOC_FILES:
        if not path.exists():
            errors.append(f"missing public doc: {path.relative_to(REPO_ROOT)}")
            continue

        content = _read_text(path)
        for forbidden in FORBIDDEN_PUBLIC_DOC_LINKS:
            if forbidden in content:
                errors.append(
                    f"{path.relative_to(REPO_ROOT)} links ignored local eval output: {forbidden}"
                )
        for forbidden in FORBIDDEN_PUBLIC_INDEX_MENTIONS.get(path, []):
            if forbidden in content:
                errors.append(
                    f"{path.relative_to(REPO_ROOT)} presents excluded local docs as public entrypoints: {forbidden}"
                )

    return AuditResult(errors=errors, warnings=warnings)


def _parse_git_status_lines(output: str) -> list[str]:
    entries: list[str] = []
    for raw_line in output.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if len(line) < 4:
            continue
        entries.append(line[3:])
    return entries


def audit_git_status() -> AuditResult:
    errors: list[str] = []
    warnings: list[str] = []

    try:
        proc = subprocess.run(
            ["git", "status", "--short"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        warnings.append(f"could not run git status --short: {exc}")
        return AuditResult(errors=errors, warnings=warnings)

    if proc.returncode != 0:
        warnings.append(
            "git status --short failed: "
            + (proc.stderr.strip() or proc.stdout.strip() or f"exit {proc.returncode}")
        )
        return AuditResult(errors=errors, warnings=warnings)

    changed_paths = _parse_git_status_lines(proc.stdout)
    if not changed_paths:
        warnings.append("working tree is clean")
        return AuditResult(errors=errors, warnings=warnings)

    warnings.append(f"working tree has {len(changed_paths)} changed path(s)")

    for path in changed_paths:
        normalized = path.replace("\\", "/")
        for prefix in SUSPICIOUS_STATUS_PREFIXES:
            if normalized.startswith(prefix):
                errors.append(f"suspicious changed path for public release: {normalized}")
                break

    return AuditResult(errors=errors, warnings=warnings)


def run_audit() -> AuditResult:
    doc_result = audit_public_docs()
    status_result = audit_git_status()
    return AuditResult(
        errors=[*doc_result.errors, *status_result.errors],
        warnings=[*doc_result.warnings, *status_result.warnings],
    )


def main() -> int:
    result = run_audit()

    for warning in result.warnings:
        print(f"WARNING: {warning}")
    for error in result.errors:
        print(f"ERROR: {error}")

    if result.ok:
        print("Public release audit passed.")
        return 0

    print("Public release audit failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
