from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DESIGN_PATH = REPO_ROOT / "docs/architecture/architecture.md"
VIEWS_PATH = REPO_ROOT / "docs/architecture/architecture-views.md"
HTML_PATH = REPO_ROOT / "docs/architecture/architecture.html"

EXPECTED_VIEWS = [
    "Product Context View",
    "Business Flow View",
    "Logical Capability View",
    "Provider Boundary View",
    "Domain State View",
    "Staleness and Review View",
    "Agent Runtime View",
    "Runtime and Domain State View",
    "Physical Deployment Decision View",
    "Deployment Profiles View",
    "Data Ownership View",
    "Failure and Recovery View",
    "A/B/C Eval View",
    "Security Verification View",
]
CANONICAL_ARCHITECTURE_FILES = {"README.md", "architecture.md", "architecture-views.md", "architecture.html"}
MERMAID_MODULE_URL = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs"
STALE_OUTPUTS = [
    REPO_ROOT / "docs/architecture/overview.html",
    REPO_ROOT / "docs/architecture.md",
    REPO_ROOT / "docs/architecture/overall-architecture.md",
]


def _section(content: str, title: str) -> str:
    marker = f"### {title}"
    start = content.find(marker)
    if start < 0:
        return ""
    next_positions = [content.find(f"### {item}", start + len(marker)) for item in EXPECTED_VIEWS]
    next_positions = [position for position in next_positions if position >= 0]
    return content[start : min(next_positions) if next_positions else len(content)]


def validate_design(content: str) -> list[str]:
    required_sections = [
        "# Zuno 总体 Target 架构",
        "## Part A — Architecture Narrative",
        "## Part B — Detailed Architecture Specification",
        "### 1. Zuno 要解决的到底是什么问题",
        "### 2. 不是所有法律任务都需要同样复杂的系统",
        "### 3.1 为什么按“事实谁负责”切架构，而不是按技术栈切",
        "### 4. 一次复杂法律任务怎样完整运行",
        "### 7. 为什么系统里的状态不能全部放在一起",
        "### 8.1 九个责任域不是九段必须依次经过的流水线",
        "### 9. 一次系统故障以后怎样恢复",
        "### 11.1 一项复杂机制什么时候应该主动删除",
        "### 12. 当前哪些能力仍然没有证明",
        "### B1 Scope and Global Invariants",
        "### B2 Responsibility / Ownership Map",
        "### B3 Cross-boundary Contracts",
        "### B5 State Machines",
        "### B6 Retry / Replan / Reconcile",
        "### B7 Failure Semantics",
        "### B8 Security / Approval / Audit",
        "### B9 Recovery and Idempotency",
        "### B10 Persistence Boundaries",
        "### B11 Observability / Evaluation",
        "### B12 Current / Target / Gap",
        "### B13 Evidence / Verification",
        "### B14 Code / Database / Migration Constraints",
    ]
    required_terms = [
        "模块化 Python 后端",
        "独立网络服务",
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
        "责任层",
        "可选上下文边界",
        "FastAPI",
        "LangGraph",
        "PostgreSQL",
        "Checkpoint",
        "Reconciliation",
        "Current",
        "Target",
        "History",
        "为什么必须独立服务",
        "不是库或 Worker",
        "Logical Responsibility",
        "Target Status Boundary",
        "KnowledgeGeneration lifecycle != task-level ReadinessDecision",
        "EvidenceCandidate != Evidence",
        "CitationLineage != WorkProductCitationBinding",
    ]
    errors: list[str] = []
    for marker in required_sections + required_terms:
        if marker not in content:
            errors.append(f"architecture.md missing required marker: {marker}")

    for marker in ("docs/project/project.md", "docs/architecture/"):
        if marker not in content:
            errors.append(f"architecture.md does not route to canonical project layer: {marker}")

    if "9 个 Target Logical Modules" not in content or "Round 02" not in content:
        errors.append("architecture.md must record the frozen nine-module target and its Round 02 source")

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
        if marker not in content:
            errors.append(f"architecture.md missing governance marker: {marker}")

    if content.count("```mermaid") > 8:
        errors.append("architecture.md must remain text-first with at most eight diagrams")
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
        errors.append(
            f"architecture visual source must contain exactly {len(EXPECTED_VIEWS)} Mermaid diagrams"
        )

    for term in (
        "Python-only",
        "Modular Python Backend",
        "Independent Workers",
        "Evidence Gate",
        "Physical Deployment Decision",
        "EffectReceipt",
        "AdmissionReceipt",
        "A/B/C",
        "Optional Context Provider",
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
        "../project/project.md",
        "./architecture.md#target-status-boundary",
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
        errors.append(
            f"{root.relative_to(REPO_ROOT)} must contain exactly "
            f"{sorted(CANONICAL_ARCHITECTURE_FILES)}, got {sorted(files)}"
        )
    if directories:
        errors.append(f"{root.relative_to(REPO_ROOT)} must not contain subdirectories: {directories}")
    return errors


def validate_taxonomy() -> list[str]:
    errors: list[str] = []
    for relative_path in (
        "docs/README.md",
        "docs/project/project.md",
        "docs/architecture/architecture.md",
        "docs/modules/README.md",
        "docs/evidence/README.md",
    ):
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"missing canonical project entrypoint: {relative_path}")
    if not (REPO_ROOT / "docs/history/red-blue/README.md").exists():
        errors.append("missing Red/Blue history archive README")
    return errors


def write_outputs() -> None:
    errors = [
        *validate_taxonomy(),
        *validate_design(DESIGN_PATH.read_text(encoding="utf-8")),
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
    errors.extend(validate_design(DESIGN_PATH.read_text(encoding="utf-8")))
    errors.extend(validate_source(VIEWS_PATH.read_text(encoding="utf-8")))
    errors.extend(validate_html(HTML_PATH.read_text(encoding="utf-8")))
    for path in STALE_OUTPUTS:
        if path.exists():
            errors.append(f"stale architecture output exists: {path.relative_to(REPO_ROOT)}")
    return errors


def build_html() -> str:
    return HTML_PATH.read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Zuno cross-layer architecture and visual source.")
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
