"""Deterministic structural gate for Canonical Part A/Part B normalization."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = [
    ROOT / "docs/project/architecture/architecture.md",
    ROOT / "docs/project/product/product-architecture.md",
    ROOT / "docs/project/domain/legal-domain-model.md",
    ROOT / "docs/project/domain/domain-state-lifecycle.md",
    ROOT / "docs/project/agents/agent-platform.md",
    ROOT / "docs/project/agents/multi-agent-runtime.md",
    ROOT / "docs/project/knowledge/knowledge-evidence-architecture.md",
    ROOT / "docs/project/services/service-architecture.md",
    ROOT / "docs/project/data/data-ownership-and-recovery.md",
    ROOT / "docs/project/security/security-architecture.md",
    ROOT / "docs/project/eval/legal-eval-and-benchmark.md",
    ROOT / "docs/project/deployment/microservice-deployment.md",
]
PART_A = "## Part A — Architecture Narrative"
PART_B = "## Part B — Detailed Architecture Specification"
PROCESS_MARKERS = re.compile(
    r"(?im)Round-\d+|\bD\d{3}\b|\bQ\d{3}\b|Target Refinement|Red Finding|Blue Decision|Score\s+\d+/\d+"
)
LEGACY_TOP_LEVEL = {
    "Scope", "Target flow", "Canonical / non-canonical", "Part-A acceptance boundary",
    "Definition", "Minimum Canonical Objects", "Provider rule", "Part-A owner and mutation boundary",
    "Version and authority", "New Evidence protocol", "Failure and recovery", "PlanVersion / DomainVersion contract",
    "Boundary", "Flow", "Domain-aware Runtime Contract", "Runtime provider", "Part-A execution model",
    "Capability and Skill", "Levels", "Shared Kernel", "Service rule", "Eval", "Service set",
    "Why not 11 services", "Contract rules", "Ownership map", "Physical policy", "Store classification",
    "Recovery", "Required gates", "Verifiability target", "A/B/C", "Metrics", "Legal Evaluation Layers",
    "Worker boundary", "Profiles", "Scaling reasons", "Communication and rollout",
}


def _nonempty_lines(value: str) -> list[str]:
    return [line for line in value.splitlines() if line.strip()]


def _has_any(value: str, markers: tuple[str, ...]) -> bool:
    return any(marker in value for marker in markers)


def split_parts(text: str) -> tuple[str, str, list[str]]:
    errors: list[str] = []
    if text.count(PART_A) != 1:
        errors.append(f"must contain exactly one {PART_A}")
    if text.count(PART_B) != 1:
        errors.append(f"must contain exactly one {PART_B}")
    if errors:
        return "", "", errors
    a_position = text.index(PART_A)
    b_position = text.index(PART_B)
    if a_position > b_position:
        errors.append("Part A must occur before Part B")
        return "", "", errors
    prefix = text[:a_position]
    if re.search(r"(?m)^##\s+", prefix):
        errors.append("a second-level section appears before Part A")
    part_a = text[a_position + len(PART_A):b_position]
    part_b = text[b_position + len(PART_B):]
    if re.search(r"(?im)^##\s+Part\s*-?A\b", part_b):
        errors.append("Part A heading appears after Part B")
    for match in re.finditer(r"(?m)^##\s+(.+?)\s*$", part_b):
        if match.group(1).strip() in LEGACY_TOP_LEVEL:
            errors.append(f"legacy top-level section remains after Part B: {match.group(1).strip()}")
    if PROCESS_MARKERS.search(text):
        errors.append("Canonical document contains Round/Delta/Question or Red/Blue process trace")
    if re.search(r"(?im)^##\s+Part-A\b", text):
        errors.append("legacy Part-A subsection heading remains")
    return part_a, part_b, errors


def verify_canonical(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not path.exists():
        return [f"missing canonical Markdown: {path.relative_to(ROOT)}"], []
    text = path.read_text(encoding="utf-8")
    label = str(path.relative_to(ROOT))
    part_a, part_b, split_errors = split_parts(text)
    errors.extend(f"{label}: {error}" for error in split_errors)
    for marker in ("status:", "Current", "Target", "Gap"):
        if marker not in text:
            errors.append(f"{label}: missing metadata or boundary marker {marker}")
    if path != ROOT / "docs/project/architecture/architecture.md":
        for marker in ("canonical_question:", "owner:"):
            if marker not in text:
                errors.append(f"{label}: missing metadata {marker}")
    if not part_a or not part_b:
        return errors, warnings

    a_lines = _nonempty_lines(part_a)
    if len(a_lines) < 12:
        errors.append(f"{label}: Part A is too short for a narrative")
    bullet_lines = [line for line in a_lines if line.lstrip().startswith(("- ", "* "))]
    table_lines = [line for line in a_lines if line.lstrip().startswith("|")]
    if len(bullet_lines) > max(8, len(a_lines) * 0.55):
        errors.append(f"{label}: Part A is dominated by bullet lists")
    if len(table_lines) > max(5, len(a_lines) * 0.55):
        errors.append(f"{label}: Part A is dominated by tables")

    concerns = {
        "problem/why": ("为什么", "问题", "动机", "价值", "解决"),
        "target scenario": ("Target Scenario", "场景", "案件", "材料", "任务"),
        "responsibility": ("负责", "职责", "Owner", "Ownership"),
        "non-responsibility": ("不负责", "不拥有", "不能", "不应", "不自动"),
        "boundary/flow": ("边界", "上游", "下游", "→", "流程", "路径"),
        "happy path": ("Happy Path", "正常", "先", "然后", "提交"),
        "failure story": ("失败", "Failure", "timeout", "stale", "恢复", "异常"),
        "reasoning/tradeoff": ("取舍", "代价", "成本", "收益", "复杂度", "因为"),
        "alternative/reversal": ("替代", "删除", "缩减", "如果", "若", "反转"),
        "status boundary": ("Current", "Target", "Hypothesis", "Gap"),
    }
    for concern, markers in concerns.items():
        if not _has_any(part_a, markers):
            errors.append(f"{label}: Part A lacks {concern}")

    spec_concerns = {
        "contract": ("Contract", "契约", "Schema", "Input", "Output"),
        "state/version": ("State", "状态", "Version", "版本", "CAS", "Generation"),
        "failure propagation": ("Failure", "失败", "异常", "typed failure"),
        "retry/recovery": ("Retry", "Recovery", "重试", "恢复", "reconciliation", "对账"),
        "idempotency": ("Idempot", "幂等", "去重", "重复"),
        "security": ("Security", "权限", "授权", "Secret", "Policy", "隔离"),
        "audit/observability": ("Audit", "Trace", "Observability", "审计", "观测"),
        "ownership/storage": ("Owner", "Ownership", "所有权", "Storage", "保存", "Domain"),
        "testing/evidence": ("Test", "Testing", "Benchmark", "Evidence", "验证", "测量"),
    }
    for concern, markers in spec_concerns.items():
        if not _has_any(part_b, markers):
            errors.append(f"{label}: Part B lacks {concern}")

    prose = [line for line in a_lines if not line.lstrip().startswith(("- ", "* ", "|"))]
    if len(prose) < 8:
        errors.append(f"{label}: Part A lacks enough prose paragraphs")
    heading_lines = [line.strip() for line in a_lines if line.startswith("### ")]
    if heading_lines and len(set(heading_lines)) < len(heading_lines) * 0.75:
        warnings.append(f"{label}: Part A contains repeated subsection headings")
    return errors, warnings


def verify() -> list[str]:
    errors: list[str] = []
    for path in CANONICAL:
        doc_errors, _warnings = verify_canonical(path)
        errors.extend(doc_errors)
    views = ROOT / "docs/project/architecture/architecture-views.md"
    html = ROOT / "docs/project/architecture/architecture.html"
    if not views.exists() or not html.exists():
        errors.append("architecture diagram presentation pair must remain present")
    elif 'fetch("./architecture-views.md")' not in html.read_text(encoding="utf-8"):
        errors.append("architecture.html must continue to consume architecture-views.md")
    for forbidden in ROOT.glob("docs/**/*-human.md"):
        errors.append(f"human/spec mirror document must not exist: {forbidden.relative_to(ROOT)}")
    for forbidden in ROOT.glob("docs/**/*-spec.md"):
        errors.append(f"human/spec mirror document must not exist: {forbidden.relative_to(ROOT)}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify V3.1.1 Canonical document normalization")
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args(argv)
    paths = args.paths or CANONICAL
    errors: list[str] = []
    warnings: list[str] = []
    for path in paths:
        resolved = path if path.is_absolute() else ROOT / path
        doc_errors, doc_warnings = verify_canonical(resolved)
        errors.extend(doc_errors)
        warnings.extend(doc_warnings)
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("document normalization V3.1.1 verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
