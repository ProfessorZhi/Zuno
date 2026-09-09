from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

MODULES = {
    "01-application-integration.md": "application/README.md",
    "02-legal-domain-work-product.md": "domain/README.md",
    "03-knowledge-evidence.md": "knowledge/README.md",
    "04-agent-runtime-control.md": "runtime/README.md",
    "05-capability-skill.md": "capability/README.md",
    "06-tool-runtime-effects.md": "effects/README.md",
    "07-model-gateway.md": "model-gateway/README.md",
    "08-security-governance.md": "security/README.md",
    "09-observability-evaluation.md": "evaluation/README.md",
}

MODULE_READMES = [ROOT / "docs/modules" / value for value in MODULES.values()]
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".html"}
SKIP_PREFIXES = (ROOT / "docs/red-blue/archive/legacy",)


def replace(path: Path, pairs: list[tuple[str, str]]) -> bool:
    text = path.read_text(encoding="utf-8")
    updated = text
    for old, new in pairs:
        updated = updated.replace(old, new)
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def under(path: Path, prefix: Path) -> bool:
    try:
        path.relative_to(prefix)
        return True
    except ValueError:
        return False


def migrate_module_readmes() -> None:
    common = [
        ("../evidence/", "../../evidence/"),
        ("../decisions/", "../../decisions/"),
        ("../research/", "../../research/"),
        ("../governance/", "../../governance/"),
        ("../red-blue/", "../../red-blue/"),
        ("../architecture/architecture.md", "../../architecture/README.md"),
        ("../architecture/README.md", "../../architecture/README.md"),
        ("../project/project.md", "../../project/README.md"),
        ("../project/README.md", "../../project/README.md"),
    ]
    absolute = [(f"docs/modules/{old}", f"docs/modules/{new}") for old, new in MODULES.items()]
    sibling = [(old, f"../{new}") for old, new in MODULES.items()]
    for path in MODULE_READMES:
        replace(path, common + absolute + sibling)


def migrate_active_text() -> None:
    pairs = [
        ("docs/project/project.md", "docs/project/README.md"),
        ("project/project.md", "project/README.md"),
        ("docs/architecture/architecture.md", "docs/architecture/README.md"),
        ("architecture/architecture.md", "architecture/README.md"),
        ("./architecture.md", "./README.md"),
    ]
    pairs += [(old, new) for old, new in MODULES.items()]

    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if path in MODULE_READMES or path == Path(__file__).resolve():
            continue
        if any(under(path, prefix) for prefix in SKIP_PREFIXES):
            continue
        replace(path, pairs)


def structural_fixes() -> None:
    replace(ROOT / "tools/scripts/verify_docs_entrypoints.py", [
        ('    "docs/project/project.md",\n', ''),
        ('    "architecture.md",\n', ''),
    ])
    replace(ROOT / "tools/scripts/verify_architecture_document_set.py", [
        ('    "architecture.md",\n', ''),
    ])
    replace(ROOT / "tools/agent/render_architecture.py", [
        ('    "architecture.md",\n', ''),
    ])
    replace(ROOT / ".agent/scripts/verify_doc_boundaries.py", [
        ('    "docs/project/project.md",\n', ''),
        ('    "architecture.md",\n', ''),
    ])
    replace(ROOT / "tools/scripts/verify_repo_structure.py", [
        ('    "docs/project/project.md",\n', ''),
        ('"README.md", "architecture.md", "architecture-views.md", "architecture.html", "reference.md"',
         '"README.md", "architecture-views.md", "architecture.html", "reference.md"'),
    ])
    replace(ROOT / "tools/scripts/verify_architecture_human_readability.py", [
        ('    "project.md": (9000, 10, 24),', '    "README.md": (9000, 10, 24),'),
    ])
    replace(ROOT / "tests/repo/test_docs_entrypoints.py", [
        ('CANONICAL_ARCHITECTURE_FILES = {\n    "README.md", "architecture.md", "architecture-views.md", "architecture.html", "reference.md"\n}',
         'CANONICAL_ARCHITECTURE_FILES = {\n    "README.md", "architecture-views.md", "architecture.html", "reference.md"\n}'),
        ('CANONICAL_PROJECT_FILES = {"README.md", "project.md", "reference.md"}',
         'CANONICAL_PROJECT_FILES = {"README.md", "reference.md"}'),
        ('assert {p.name for p in root.iterdir() if p.is_file()} == CANONICAL_MODULE_FILES',
         'assert {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()} == CANONICAL_MODULE_FILES'),
        ('    assert "project.md" in readme\n', ''),
        ('    assert "project.md" in reference\n', ''),
    ])
    replace(ROOT / "tests/repo/test_architecture_human_readability.py", [
        ('"project.md"', '"README.md"'),
    ])


def main() -> None:
    migrate_module_readmes()
    migrate_active_text()
    structural_fixes()


if __name__ == "__main__":
    main()
