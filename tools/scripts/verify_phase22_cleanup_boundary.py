from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
WORK_PRODUCT = (
    REPO_ROOT / ".agent" / "programs" / "work-products" / "phase22-removal-candidates.yaml"
)
PRODUCT_RUNTIME_BATCH = REPO_ROOT / "src" / "backend" / "zuno" / "product" / "runtime_batch.py"
PRODUCT_COMMAND_SERVICE = (
    REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "product" / "command_service.py"
)
WORKSPACE_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "workspace.py"
ATTACHMENT_SERVICE = (
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "workspace" / "attachment_service.py"
)
STORAGE_FACADE = (
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "storage" / "__init__.py"
)
TEXT_TO_IMAGE_ACTION = (
    REPO_ROOT / "src" / "backend" / "zuno" / "capability" / "tools" / "text2image" / "action.py"
)
CURRENT_PROGRAM = REPO_ROOT / ".agent" / "programs" / "current.md"
MANIFEST = REPO_ROOT / ".agent" / "programs" / "program-manifest.yaml"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify_phase22_cleanup_boundary() -> list[str]:
    errors: list[str] = []

    if not WORK_PRODUCT.exists():
        errors.append("missing phase22 removal candidates work product")
    else:
        candidates = _read(WORK_PRODUCT)
        for phrase in [
            "status: frozen_from_phase21_runtime_and_phase22_startup_scan",
            "src/backend/zuno/platform/compatibility/legacy_aliases.py",
            "tests/legacy_guards/",
            "legacy_general_agent_completion_rollback",
            "src/backend/zuno/product/runtime_batch.py",
            "src/backend/zuno/api/services/product/command_service.py",
            "src/backend/zuno/api/services/workspace.py",
            "src/backend/zuno/platform/services/workspace/attachment_service.py",
            "remaining_not_closed:",
        ]:
            if phrase not in candidates:
                errors.append(f"phase22 removal candidates missing phrase: {phrase}")

    runtime_batch = _read(PRODUCT_RUNTIME_BATCH)
    if "from zuno.schema.workspace import" in runtime_batch:
        errors.append("product runtime batch still imports workspace DTO through zuno.schema alias")
    if "from zuno.api.dto.workspace import" not in runtime_batch:
        errors.append("product runtime batch missing canonical workspace DTO import")

    command_service = _read(PRODUCT_COMMAND_SERVICE)
    if "from zuno.database import engine" in command_service:
        errors.append("product command service still imports engine through zuno.database alias")
    if "from zuno.platform.database import engine" not in command_service:
        errors.append("product command service missing canonical platform database import")

    alias_imports = [
        "from zuno.schema.",
        "import zuno.schema.",
        "from zuno.services.",
        "import zuno.services.",
        "from zuno.tools.",
        "import zuno.tools.",
        "from zuno.utils.",
        "import zuno.utils.",
        "from zuno.resources.",
        "import zuno.resources.",
    ]
    for label, path in [
        ("workspace service", WORKSPACE_SERVICE),
        ("workspace attachment service", ATTACHMENT_SERVICE),
        ("storage facade", STORAGE_FACADE),
        ("text2image action", TEXT_TO_IMAGE_ACTION),
    ]:
        text = _read(path)
        for alias_import in alias_imports:
            if alias_import in text:
                errors.append(f"{label} still imports through legacy alias: {alias_import}")

    current = _read(CURRENT_PROGRAM)
    manifest = _read(MANIFEST)
    for label, text in [("current.md", current), ("program-manifest.yaml", manifest)]:
        if "current_phase: PHASE22" not in text:
            errors.append(f"{label} missing PHASE22 current phase")

    return errors


def main() -> int:
    errors = verify_phase22_cleanup_boundary()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE22 cleanup boundary verification failed.")
        return 1
    print("PHASE22 cleanup boundary verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
