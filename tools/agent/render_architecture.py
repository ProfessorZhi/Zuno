from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DESIGN_PATH = REPO_ROOT / "docs/project/architecture/architecture.md"
VIEWS_PATH = REPO_ROOT / "docs/project/architecture/architecture-views.md"
HTML_PATH = REPO_ROOT / "docs/project/architecture/architecture.html"

EXPECTED_VIEWS = [
    "Product Context View",
    "Business Flow View",
    "Logical Capability View",
    "Provider Boundary View",
    "Domain State View",
    "Staleness and Review View",
    "Agent Runtime View",
    "Runtime and Domain State View",
    "Microservice View",
    "Deployment Profiles View",
    "Data Ownership View",
    "Failure and Recovery View",
    "A/B/C Eval View",
    "Security Verification View",
]
CANONICAL_TAXONOMY = [
    "docs/project/product/product-architecture.md",
    "docs/project/domain/legal-domain-model.md",
    "docs/project/domain/domain-state-lifecycle.md",
    "docs/project/agents/agent-platform.md",
    "docs/project/agents/multi-agent-runtime.md",
    "docs/project/knowledge/knowledge-evidence-architecture.md",
    "docs/project/services/service-architecture.md",
    "docs/project/data/data-ownership-and-recovery.md",
    "docs/project/security/security-architecture.md",
    "docs/project/eval/legal-eval-and-benchmark.md",
    "docs/project/deployment/microservice-deployment.md",
]
CANONICAL_ARCHITECTURE_FILES = {"README.md", "architecture.md", "architecture-views.md", "architecture.html"}
MERMAID_MODULE_URL = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs"
STALE_OUTPUTS = [
    REPO_ROOT / "docs/project/architecture/overview.html",
    REPO_ROOT / "docs/project/architecture.md",
    REPO_ROOT / "docs/project/architecture/overall-architecture.md",
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
        "## 0. 这次重构改变了什么",
        "## 1. 产品与领域核心",
        "## 2. Python-only Target",
        "## 3. 五个 Network-facing Python Services",
        "## 4. 逻辑能力如何落到服务",
        "## 5. FastAPI 与 LangGraph 的硬边界",
        "## 6. 同步、异步与队列",
        "## 7. Domain State 与 Runtime State",
        "## 8. Deployment Profiles",
        "## 9. Current / Target / History",
        "## 10. Canonical Reading Order",
    ]
    required_terms = [
        "Python-only", "Microservice", "edge-api", "platform-domain-service",
        "agent-runtime-service", "knowledge-service", "tool-sandbox-service",
        "FastAPI", "LangGraph", "PostgreSQL", "Checkpoint", "Reconciliation",
        "Current", "Target", "History", "Why service?", "Why not library?",
    ]
    errors: list[str] = []
    for marker in required_sections + required_terms:
        if marker not in content:
            errors.append(f"architecture.md missing required marker: {marker}")
    for path in CANONICAL_TAXONOMY:
        marker = path.split("docs/project/", 1)[-1]
        if marker not in content and Path(path).name not in content:
            errors.append(f"architecture.md does not route to canonical document: {path}")
    if "11 Logical Modules + 1 Architecture" not in content:
        errors.append("architecture.md must record the old 11-module taxonomy as History")
    if "五个服务的 Target Candidate，不是 Current" not in content:
        errors.append("architecture.md must distinguish service Target from Current")
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
    for term in [
        "Python-only", "edge-api", "platform-domain-service", "agent-runtime-service",
        "knowledge-service", "tool-sandbox-service", "FastAPI", "LangGraph",
        "PostgreSQL", "Checkpoint", "Reconciliation", "EvidenceRequirement",
        "ConflictProposal", "EffectReceipt", "A/B/C",
    ]:
        if term.lower() not in content.lower():
            errors.append(f"architecture-views.md missing visual term: {term}")
    return errors


def validate_html(content: str) -> list[str]:
    required = [
        "Zuno Target Architecture", '<script type="module">', 'fetch("./architecture-views.md")',
        MERMAID_MODULE_URL, "../product/product-architecture.md", "../services/service-architecture.md",
        "../../status/production-readiness.md", "diagram-dialog", "Mermaid source",
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
    for relative_path in CANONICAL_TAXONOMY:
        path = REPO_ROOT / relative_path
        if not path.exists():
            errors.append(f"missing canonical taxonomy document: {relative_path}")
    for path in (REPO_ROOT / "docs/project/modules").glob("[0-9][0-9]-*.md"):
        content = path.read_text(encoding="utf-8")
        if "status: superseded-legacy-reference" not in content:
            errors.append(f"legacy module lacks superseded status: {path.relative_to(REPO_ROOT)}")
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
    errors = _directory_errors(REPO_ROOT / "docs/project/architecture")
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
