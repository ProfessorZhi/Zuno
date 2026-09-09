from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DESIGN_PATH = REPO_ROOT / "docs/architecture/README.md"
REFERENCE_PATH = REPO_ROOT / "docs/architecture/reference.md"
VIEWS_PATH = REPO_ROOT / "docs/architecture/architecture-views.md"
HTML_PATH = REPO_ROOT / "docs/architecture/architecture.html"

EXPECTED_VIEWS = [
    "Case Timeline View",
    "Fact Authority View",
    "Boundary Transition View",
    "Responsibility View",
    "Recovery View",
    "Deployment and Evolution View",
]
CANONICAL_ARCHITECTURE_FILES = {
    "README.md",
    "architecture-views.md",
    "architecture.html",
    "reference.md",
}
MERMAID_MODULE_URL = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs"
STALE_OUTPUTS = [
    REPO_ROOT / "docs/architecture/overview.html",
    REPO_ROOT / "docs/architecture.md",
    REPO_ROOT / "docs/architecture/overall-architecture.md",
    REPO_ROOT / "docs/architecture/architecture.md",
]


def _section(content: str, title: str) -> str:
    marker = f"## {title}"
    start = content.find(marker)
    if start < 0:
        return ""
    next_positions = [content.find(f"## {item}", start + len(marker)) for item in EXPECTED_VIEWS]
    next_positions = [position for position in next_positions if position >= 0]
    return content[start : min(next_positions) if next_positions else len(content)]


def validate_design(human: str, reference: str | None = None) -> list[str]:
    if reference is None:
        reference = REFERENCE_PATH.read_text(encoding="utf-8")
    combined = human + "\n" + reference
    errors: list[str] = []

    for marker in (
        "# Zuno 目标架构",
        "## Part A — Human Narrative（人类技术叙事）",
        "reference.md",
    ):
        if marker not in human:
            errors.append(f"architecture README missing required marker: {marker}")
    if "## Part B — Engineering / Agent Reference（工程 / Agent 参考）" in human:
        errors.append("architecture README must not retain Part B")

    for marker in (
        "## Part B — Engineering / Agent Reference（工程 / Agent 参考）",
        "### B1. Scope / Global Invariants",
        "### B2. Authority / Ownership Matrix",
        "### B3. Cross-boundary Contract Map",
        "### B6. Completion Proof / Non-proof",
        "### B7. Failure Taxonomy / Recovery Order",
        "### B10. Security / Approval / Human Authority",
        "### B13. Current / Target / Evidence / Unknown",
        "### B14. Machine Navigation / Source Precedence",
    ):
        if marker not in reference:
            errors.append(f"architecture reference missing required marker: {marker}")

    for marker in (
        "Application & Integration",
        "Legal Domain & Work Product",
        "Knowledge & Evidence",
        "Agent Runtime & Control",
        "Capability & Skill",
        "Tool Runtime & Effects",
        "Model Gateway",
        "Security & Governance",
        "Observability & Evaluation",
        "Platform / Infrastructure",
        "Single Controller",
        "AdmissionReceipt",
        "KnowledgeGeneration lifecycle != task-level ReadinessDecision",
        "EvidenceCandidate != Evidence",
        "CitationLineage != WorkProductCitationBinding",
        "Retry != Replan != Reconcile",
        "PreparedAction",
        "EffectReceipt",
        "Reconcile",
        "模块化 Python 后端",
        "独立网络服务",
        "Target Architecture",
    ):
        if marker not in combined:
            errors.append(f"architecture split views missing required term: {marker}")

    for marker in ("docs/modules/", "docs/decisions/", "docs/evidence/", "docs/research/"):
        if marker not in combined:
            errors.append(f"architecture split views missing canonical route: {marker}")

    for marker in (
        "final_module_count: 9",
        "overall_architecture_state: ROUND_02_FROZEN",
        "module_decomposition_gate: OPEN",
        "module_design_baseline: AVAILABLE_V1",
        "module_deep_design: AVAILABLE_V2",
        "module_deep_design_coverage: 9/9",
        "module_detail_freeze: NOT_YET",
        "implementation_authorization: NO",
        "architecture_state: ACCEPTED_TARGET",
    ):
        if marker not in human:
            errors.append(f"architecture README missing governance marker: {marker}")

    if human.count("```mermaid") > 2:
        errors.append("architecture README should remain prose-first; diagrams belong in architecture-views.md")
    return errors


def validate_source(content: str) -> list[str]:
    errors: list[str] = []
    for title in EXPECTED_VIEWS:
        section = _section(content, title)
        if not section:
            errors.append(f"missing canonical architecture view: {title}")
        elif section.count("```mermaid") < 1:
            errors.append(f"canonical view has no Mermaid diagram: {title}")
    if content.count("```mermaid") != len(EXPECTED_VIEWS):
        errors.append(f"architecture visual source must contain exactly {len(EXPECTED_VIEWS)} Mermaid diagrams")
    for term in (
        "Modular Python Backend",
        "Independent Workers",
        "EffectReceipt",
        "AdmissionReceipt",
        "Optional Context Provider",
        "Evidence Gate",
    ):
        if term.lower() not in content.lower():
            errors.append(f"architecture-views.md missing visual term: {term}")
    return errors


def validate_html(content: str) -> list[str]:
    required = [
        "Zuno Target Architecture",
        '<script type="module">',
        'fetch("./architecture-views.md")',
        MERMAID_MODULE_URL,
        "../project/README.md",
        "./README.md",
        "../evidence/README.md",
        "diagram-dialog",
        "Mermaid source",
    ]
    errors = [f"architecture.html missing marker: {marker}" for marker in required if marker not in content]
    if "offline-svg" in content or "offline-diagram" in content:
        errors.append("architecture.html must not use the retired simplified renderer")
    return errors


def _directory_errors(root: Path) -> list[str]:
    files = {path.name for path in root.iterdir() if path.is_file()}
    directories = [path.name for path in root.iterdir() if path.is_dir()]
    errors: list[str] = []
    if files != CANONICAL_ARCHITECTURE_FILES:
        errors.append(f"{root.relative_to(REPO_ROOT)} must contain exactly {sorted(CANONICAL_ARCHITECTURE_FILES)}, got {sorted(files)}")
    if directories:
        errors.append(f"{root.relative_to(REPO_ROOT)} must not contain subdirectories: {directories}")
    return errors


def validate_taxonomy() -> list[str]:
    errors: list[str] = []
    for relative_path in (
        "docs/README.md",
        "docs/project/README.md",
        "docs/architecture/README.md",
        "docs/architecture/reference.md",
        "docs/modules/README.md",
        "docs/modules/reference.md",
        "docs/evidence/README.md",
        "docs/red-blue/README.md",
    ):
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"missing canonical project entrypoint: {relative_path}")
    if not (REPO_ROOT / "docs/red-blue/archive/legacy/README.md").exists():
        errors.append("missing Red/Blue legacy archive README")
    return errors


def write_outputs() -> None:
    errors = [
        *validate_taxonomy(),
        *validate_design(DESIGN_PATH.read_text(encoding="utf-8"), REFERENCE_PATH.read_text(encoding="utf-8")),
        *validate_source(VIEWS_PATH.read_text(encoding="utf-8")),
        *validate_html(HTML_PATH.read_text(encoding="utf-8")),
    ]
    if errors:
        raise ValueError("\n".join(errors))


def check_outputs() -> list[str]:
    errors = _directory_errors(REPO_ROOT / "docs/architecture")
    errors.extend(validate_taxonomy())
    for mirror in (REPO_ROOT / ".agent/architecture", REPO_ROOT / ".agent/modules"):
        if mirror.exists():
            errors.append(f"documentation mirror must not exist: {mirror.relative_to(REPO_ROOT)}")
    errors.extend(validate_design(DESIGN_PATH.read_text(encoding="utf-8"), REFERENCE_PATH.read_text(encoding="utf-8")))
    errors.extend(validate_source(VIEWS_PATH.read_text(encoding="utf-8")))
    errors.extend(validate_html(HTML_PATH.read_text(encoding="utf-8")))
    for path in STALE_OUTPUTS:
        if path.exists():
            errors.append(f"stale architecture output exists: {path.relative_to(REPO_ROOT)}")
    return errors


def build_html() -> str:
    return HTML_PATH.read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Zuno target architecture and visual source.")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.write:
            write_outputs()
        if args.check:
            errors = check_outputs()
            if errors:
                for error in errors:
                    print(f"ERROR: {error}", file=sys.stderr)
                return 1
            print("architecture render check passed.")
        if not args.write and not args.check:
            print(build_html())
        return 0
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
