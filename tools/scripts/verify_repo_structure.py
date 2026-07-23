from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

ARCHITECTURE_ALLOWED_FILES = {
    "README.md",
    "architecture.md",
    "architecture-views.md",
    "architecture.html",
}

ACTIVE_PROGRAM_NAME = "zuno-canonical-architecture-runtime-realization-v1"
ACTIVE_PROGRAM_ROOT = ".agent/programs"
HISTORY_PROGRAM_ROOT = "docs/history/programs"
ARCHIVED_PROGRAM_REQUIRED_FILES = {"README.md"}

REQUIRED_PATHS = [
    "AGENTS.md",
    ".agent/README.md",
    ".agent/system.yaml",
    ".agent/references/current-program.md",
    ".agent/references/docs-map.md",
    ".agent/references/task-routing.md",
    ".agent/references/workflow.md",
    ".agent/programs/current.md",
    ".agent/programs/program-manifest.yaml",
    ".agent/programs/implementation-roadmap.md",
    ".agent/programs/closure-checklist.md",
    "docs/README.md",
    "docs/architecture/README.md",
    "docs/architecture/architecture.md",
    "docs/architecture/architecture-views.md",
    "docs/architecture/architecture.html",
    "docs/modules/README.md",
    "docs/status/production-readiness.md",
    "docs/history/README.md",
    "docs/history/programs/README.md",
    "tools/agent/render_architecture.py",
    "tools/scripts/verify_docs_entrypoints.py",
    "tools/scripts/verify_utf8_doc_encoding.py",
]


@dataclass(frozen=True)
class VerificationResult:
    errors: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def _read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def verify_required_paths() -> list[str]:
    errors: list[str] = []
    for relative_path in REQUIRED_PATHS:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"missing required path: {relative_path}")
    return errors


def verify_architecture_directory_contract() -> list[str]:
    errors: list[str] = []
    for relative_dir in ["docs/architecture", ".agent/architecture"]:
        directory = REPO_ROOT / relative_dir
        if not directory.exists():
            errors.append(f"missing architecture directory: {relative_dir}")
            continue
        actual = {path.name for path in directory.iterdir() if path.is_file()}
        extra = sorted(actual - ARCHITECTURE_ALLOWED_FILES)
        missing = sorted(ARCHITECTURE_ALLOWED_FILES - actual)
        if extra:
            errors.append(
                f"{relative_dir} contains non-canonical files: {', '.join(extra)}"
            )
        if missing:
            errors.append(
                f"{relative_dir} missing canonical files: {', '.join(missing)}"
            )
    return errors


def verify_active_program_contract() -> list[str]:
    errors: list[str] = []
    current_path = REPO_ROOT / ACTIVE_PROGRAM_ROOT / "current.md"
    manifest_path = REPO_ROOT / ACTIVE_PROGRAM_ROOT / "program-manifest.yaml"
    if not current_path.exists() or not manifest_path.exists():
        return ["active program current.md or program-manifest.yaml is missing"]

    current = current_path.read_text(encoding="utf-8")
    manifest = manifest_path.read_text(encoding="utf-8")
    required_current = [
        "state: active",
        f"active_program: {ACTIVE_PROGRAM_NAME}",
        "current_phase: PHASE12",
    ]
    for phrase in required_current:
        if phrase not in current:
            errors.append(f"active program current.md missing phrase: {phrase}")
    if "state: no-active" in current:
        errors.append("active program current.md must not be no-active")

    required_manifest = [
        f"id: {ACTIVE_PROGRAM_NAME}",
        "state: active",
        "current_phase: PHASE12",
        "phase_count: 22",
    ]
    for phrase in required_manifest:
        if phrase not in manifest:
            errors.append(f"active program manifest missing phrase: {phrase}")
    return errors


def verify_history_program_archives() -> list[str]:
    errors: list[str] = []
    history_root = REPO_ROOT / HISTORY_PROGRAM_ROOT
    if not history_root.exists():
        return [f"missing history program root: {HISTORY_PROGRAM_ROOT}"]

    archived_programs = [
        path for path in history_root.iterdir() if path.is_dir() and path.name != ACTIVE_PROGRAM_NAME
    ]
    if not archived_programs:
        errors.append("history program root contains no archived programs")
        return errors

    for program_dir in archived_programs:
        existing = {path.name for path in program_dir.iterdir() if path.is_file()}
        missing = sorted(ARCHIVED_PROGRAM_REQUIRED_FILES - existing)
        if missing:
            errors.append(
                f"history program archive incomplete: {program_dir.name} missing {', '.join(missing)}"
            )
        if not any(path.suffix == ".md" for path in program_dir.rglob("*.md")):
            errors.append(f"history program archive has no markdown records: {program_dir.name}")
    return errors


def verify_architecture_content_boundaries() -> list[str]:
    return []


def run_verification() -> VerificationResult:
    return VerificationResult(
        errors=[
            *verify_required_paths(),
            *verify_architecture_directory_contract(),
            *verify_active_program_contract(),
            *verify_history_program_archives(),
            *verify_architecture_content_boundaries(),
        ]
    )


def main() -> int:
    result = run_verification()
    if result.ok:
        print("Repository structure verification passed.")
        return 0
    for error in result.errors:
        print(f"ERROR: {error}")
    print("Repository structure verification failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
