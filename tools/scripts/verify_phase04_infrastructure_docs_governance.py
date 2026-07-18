from __future__ import annotations

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_ARCH = REPO_ROOT / "docs" / "architecture"
AGENT_ARCH = REPO_ROOT / ".agent" / "architecture"
DOCS_INFRA = REPO_ROOT / "docs" / "modules" / "11-infrastructure.md"
AGENT_INFRA = REPO_ROOT / ".agent" / "modules" / "11-infrastructure.md"
DOCS_ENTRYPOINTS_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_docs_entrypoints.py"
)
ARCH_DOC_SET_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_architecture_document_set.py"
)
INFRA_TARGET_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_infrastructure_target_protocols.py"
)

CANONICAL_ARCHITECTURE_FILES = {
    "README.md",
    "architecture.md",
    "architecture-views.md",
    "architecture.html",
}


def _load_module(path: Path, module_name: str):
    spec = spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {module_name}")
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _architecture_file_set_errors() -> list[str]:
    errors: list[str] = []
    for root in [DOCS_ARCH, AGENT_ARCH]:
        files = {path.name for path in root.iterdir() if path.is_file()}
        dirs = sorted(path.name for path in root.iterdir() if path.is_dir())
        if files != CANONICAL_ARCHITECTURE_FILES:
            errors.append(
                f"{root.relative_to(REPO_ROOT)} file set mismatch: {sorted(files)}"
            )
        if dirs:
            errors.append(f"{root.relative_to(REPO_ROOT)} has subdirectories: {dirs}")
    return errors


def verify_phase04_infrastructure_docs_governance() -> list[str]:
    errors: list[str] = []

    docs_entrypoints = _load_module(
        DOCS_ENTRYPOINTS_VERIFIER,
        "verify_docs_entrypoints",
    )
    for error in docs_entrypoints.verify():
        errors.append(f"docs entrypoint verification failed: {error}")

    architecture_set = _load_module(
        ARCH_DOC_SET_VERIFIER,
        "verify_architecture_document_set",
    )
    for error in architecture_set.verify():
        errors.append(f"architecture document set verification failed: {error}")

    infrastructure_target = _load_module(
        INFRA_TARGET_VERIFIER,
        "verify_infrastructure_target_protocols",
    )
    for finding in infrastructure_target.verify():
        errors.append(f"infrastructure target protocol failed: {finding}")

    errors.extend(_architecture_file_set_errors())

    if not DOCS_INFRA.exists() or not AGENT_INFRA.exists():
        errors.append("Infrastructure formal document or Agent mirror is missing")
        return errors
    if DOCS_INFRA.read_bytes() != AGENT_INFRA.read_bytes():
        errors.append("Infrastructure formal document and Agent mirror differ")

    infra = _read(DOCS_INFRA)
    for phrase in [
        "Current Inventory",
        "Target Selection",
        "Future Optional",
        "Explicitly Not Selected",
        "唯一正式 Target 架构文档",
        "Target → Current Evidence",
        "Kafka 作为默认工作队列",
        "XA / 2PC",
        "Kubernetes 作为本模块完成标准",
    ]:
        if phrase not in infra:
            errors.append(f"Infrastructure target document missing phrase: {phrase}")

    for formal, mirror in [
        ("architecture.md", "architecture.md"),
        ("architecture-views.md", "architecture-views.md"),
        ("architecture.html", "architecture.html"),
    ]:
        if (DOCS_ARCH / formal).read_bytes() != (AGENT_ARCH / mirror).read_bytes():
            errors.append(f"architecture mirror differs: {mirror}")

    status = _read(REPO_ROOT / "docs" / "status" / "production-readiness.md")
    for phrase in [
        "## Current",
        "## Future Optional",
        "target_not_current",
        "blocked、prepared、runtime observed 和 measured 必须严格区分",
    ]:
        if phrase not in status:
            errors.append(f"production readiness boundary missing phrase: {phrase}")

    return errors


def main() -> int:
    errors = verify_phase04_infrastructure_docs_governance()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 infrastructure docs governance verification failed.")
        return 1
    print("PHASE04 infrastructure docs governance verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
