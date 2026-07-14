from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_MODULES = REPO_ROOT / "docs/modules"
AGENT_MODULES = REPO_ROOT / ".agent/modules"
DOCS_ARCH = REPO_ROOT / "docs/architecture"
AGENT_ARCH = REPO_ROOT / ".agent/architecture"

MODULE_DOCS = [
    "01-product-surface.md",
    "02-input-document-ingestion.md",
    "03-knowledge-agentic-graphrag.md",
    "04-model-gateway.md",
    "05-memory-context.md",
    "06-agent-core-planning-control.md",
    "07-capability-skill.md",
    "08-tool-runtime.md",
    "09-security.md",
    "10-observability-eval.md",
    "11-infrastructure.md",
]
RETIRED_MODULE_DOCS = [
    "04-model-gateway-contract-freeze.md",
    "04-model-gateway-operations-conformance.md",
    "10-observability-eval-rag-agent-evaluation.md",
    "11-infrastructure-data-services.md",
    "11-infrastructure-consistency-lifecycle.md",
]
CANONICAL_ARCH_SUPPORT = {"README.md", "architecture.md", "architecture-views.md", "architecture.html"}


def verify() -> list[str]:
    errors: list[str] = []

    formal_candidates = sorted(path.name for path in DOCS_MODULES.glob("[0-9][0-9]-*.md"))
    mirror_candidates = sorted(path.name for path in AGENT_MODULES.glob("[0-9][0-9]-*.md"))
    if formal_candidates != MODULE_DOCS:
        errors.append(f"formal module document set must be exactly {MODULE_DOCS}, got {formal_candidates}")
    if mirror_candidates != MODULE_DOCS:
        errors.append(f"Agent module mirror set must be exactly {MODULE_DOCS}, got {mirror_candidates}")

    for index, file_name in enumerate(MODULE_DOCS, start=1):
        formal = DOCS_MODULES / file_name
        mirror = AGENT_MODULES / file_name
        if not formal.exists() or not mirror.exists():
            errors.append(f"missing formal/mirror module document: {file_name}")
            continue
        if formal.read_bytes() != mirror.read_bytes():
            errors.append(f"module formal and Agent mirror differ: {file_name}")
        content = formal.read_text(encoding="utf-8")
        if f"module_number: {index:02d}" not in content:
            errors.append(f"module metadata mismatch for {file_name}")
        if "Target" not in content:
            errors.append(f"module document does not declare Target boundary: {file_name}")
        if "production ready" not in content.lower():
            errors.append(f"module document lacks production-readiness boundary: {file_name}")

    for retired in RETIRED_MODULE_DOCS:
        if (DOCS_MODULES / retired).exists() or (AGENT_MODULES / retired).exists():
            errors.append(f"retired split module document still exists: {retired}")

    docs_arch_files = {p.name for p in DOCS_ARCH.iterdir() if p.is_file()}
    agent_arch_files = {p.name for p in AGENT_ARCH.iterdir() if p.is_file()}
    if docs_arch_files != CANONICAL_ARCH_SUPPORT:
        errors.append(f"docs/architecture file set mismatch: {sorted(docs_arch_files)}")
    if agent_arch_files != CANONICAL_ARCH_SUPPORT:
        errors.append(f".agent/architecture file set mismatch: {sorted(agent_arch_files)}")
    if [p for p in DOCS_ARCH.iterdir() if p.is_dir()]:
        errors.append("docs/architecture must not contain subdirectories")
    if [p for p in AGENT_ARCH.iterdir() if p.is_dir()]:
        errors.append(".agent/architecture must not contain subdirectories")

    for name in ["architecture.md", "architecture-views.md", "architecture.html"]:
        formal = DOCS_ARCH / name
        mirror = AGENT_ARCH / name
        if formal.read_bytes() != mirror.read_bytes():
            errors.append(f"architecture formal and Agent mirror differ: {name}")

    design = (DOCS_ARCH / "architecture.md").read_text(encoding="utf-8")
    html = (DOCS_ARCH / "architecture.html").read_text(encoding="utf-8")
    modules_index = (DOCS_MODULES / "README.md").read_text(encoding="utf-8")
    agent_index = (AGENT_MODULES / "README.md").read_text(encoding="utf-8")
    architecture_index = (DOCS_ARCH / "README.md").read_text(encoding="utf-8")

    for file_name in MODULE_DOCS:
        for label, content in [
            ("architecture.md", design),
            ("docs/modules/README.md", modules_index),
            (".agent/modules/README.md", agent_index),
        ]:
            if file_name not in content:
                errors.append(f"{label} does not route to {file_name}")

    for label, content in [
        ("docs/modules/README.md", modules_index),
        (".agent/modules/README.md", agent_index),
        ("docs/architecture/README.md", architecture_index),
    ]:
        for phrase in ["十一", "architecture.md", "architecture.html"]:
            if phrase not in content:
                errors.append(f"{label} missing architecture-set explanation: {phrase}")

    for retired in RETIRED_MODULE_DOCS:
        active_files = [
            DOCS_MODULES / "README.md",
            AGENT_MODULES / "README.md",
            DOCS_ARCH / "architecture.md",
            DOCS_ARCH / "architecture-views.md",
            DOCS_ARCH / "architecture.html",
        ]
        for path in active_files:
            if retired in path.read_text(encoding="utf-8"):
                errors.append(f"active architecture surface references retired split doc {retired}: {path.relative_to(REPO_ROOT)}")

    if "11 × docs/modules" not in design or "1 × docs/architecture/architecture.md" not in design:
        errors.append("architecture.md must declare the 11+2 formal design set")
    if "../modules/README.md" not in html:
        errors.append("architecture.html must route to the eleven module documents")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("architecture document set verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
