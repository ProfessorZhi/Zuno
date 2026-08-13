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
        "## Part A — Architecture Narrative",
        "## Part B — Detailed Architecture Specification",
        "### 这套架构要解决的业务问题",
        "### 一个完整的案件分析场景",
        "### 责任边界与不拥有的事实",
        "### 最危险的失败与恢复",
        "### 取舍与反转条件",
        "### Cross-layer Contract Registry",
        "### Service、通信与队列边界",
        "### State、Version 与 Recovery Contract",
        "### Owner Registry",
        "### Security、Deployment 与验证要求",
        "### Implementation / Measurement / External Gaps",
    ]
    required_terms = [
        "Python-only", "Microservice", "edge-api", "platform-domain-service",
        "agent-runtime-service", "knowledge-service", "tool-sandbox-service",
        "FastAPI", "LangGraph", "PostgreSQL", "Checkpoint", "Reconciliation",
        "Current", "Target", "History", "Why service?", "Why not library?",
        "Logical Capability Architecture", "Physical Service / Deployment Architecture",
    ]
    errors: list[str] = []
    for marker in required_sections + required_terms:
        if marker not in content:
            errors.append(f"architecture.md missing required marker: {marker}")
    for marker in ("docs/project/history/", "docs/project/status/", "docs/project/architecture/"):
        if marker not in content:
            errors.append(f"architecture.md does not route to canonical project layer: {marker}")
    if "11 Logical Modules + 1 Architecture" not in content or "History" not in content:
        errors.append("architecture.md must record the old 11-module taxonomy as History")
    if "五个候选服务角色，不是冻结的服务数量，也不是 Current" not in content:
        errors.append("architecture.md must distinguish candidate service roles from Current and fixed count")
    if "architecture_state: ACCEPTED_TARGET" not in content:
        errors.append("architecture.md must record ACCEPTED_TARGET")
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
        MERMAID_MODULE_URL, "../history/README.md", "../status/target-status.md",
        "../../evidence/README.md", "../status/production-readiness.md", "diagram-dialog", "Mermaid source",
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
        "docs/project/README.md",
        "docs/project/history/README.md",
        "docs/project/status/README.md",
        "docs/project/status/current-reality.md",
        "docs/project/status/target-status.md",
        "docs/project/status/production-readiness.md",
    ):
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"missing canonical project entrypoint: {relative_path}")
    archive = REPO_ROOT / "docs/history/superseded-document-taxonomy/README.md"
    if not archive.exists():
        errors.append("missing Superseded document taxonomy archive README")
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
