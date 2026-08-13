"""Verify the Part A/Part B document-quality gate for V3.1."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from verify_architecture_human_readability import verify as verify_human_readability
from verify_document_normalization_v311 import verify as verify_normalization
from verify_document_normalization_v311 import _contains_process_trace


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SESSION = ROOT / "project-reconstruction-lab" / "sessions" / "RB-WORKFLOW-V3-ROUND-003"
CANONICAL_COUNT = 12
ROW_RE = re.compile(
    r"^\|\s*docs/project/[^|]+\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*PASS\s*\|",
    re.MULTILINE,
)


def verify_quality(session: Path) -> list[str]:
    errors = verify_human_readability() + verify_normalization()
    scorecard = session / "document-quality-scorecard.md"
    if not scorecard.exists():
        errors.append("missing document-quality-scorecard.md")
        return errors
    content = scorecard.read_text(encoding="utf-8")
    rows = ROW_RE.findall(content)
    if len(rows) != CANONICAL_COUNT:
        errors.append(f"document quality scorecard must contain {CANONICAL_COUNT} PASS rows, got {len(rows)}")
    for index, (before_a, after_a, before_b, after_b) in enumerate(rows, start=1):
        if int(after_a) < 85:
            errors.append(f"scorecard row {index} Part A after score is below 85")
        if int(after_b) < 85:
            errors.append(f"scorecard row {index} Part B after score is below 85")
        if int(before_a) > int(after_a) or int(before_b) > int(after_b):
            errors.append(f"scorecard row {index} regresses from before to after")
    if "DOC_QUALITY_COMPLETE" not in content:
        errors.append("scorecard must state DOC_QUALITY_COMPLETE")
    for path in (
        ROOT / "docs/project/architecture/architecture.md",
        ROOT / "docs/history/superseded-document-taxonomy/project-topics/product/product-architecture.md",
        ROOT / "docs/history/superseded-document-taxonomy/project-topics/domain/legal-domain-model.md",
        ROOT / "docs/history/superseded-document-taxonomy/project-topics/domain/domain-state-lifecycle.md",
        ROOT / "docs/history/superseded-document-taxonomy/project-topics/agents/agent-platform.md",
        ROOT / "docs/history/superseded-document-taxonomy/project-topics/agents/multi-agent-runtime.md",
        ROOT / "docs/history/superseded-document-taxonomy/project-topics/knowledge/knowledge-evidence-architecture.md",
        ROOT / "docs/history/superseded-document-taxonomy/project-topics/services/service-architecture.md",
        ROOT / "docs/history/superseded-document-taxonomy/project-topics/data/data-ownership-and-recovery.md",
        ROOT / "docs/history/superseded-document-taxonomy/project-topics/security/security-architecture.md",
        ROOT / "docs/history/superseded-document-taxonomy/project-topics/eval/legal-eval-and-benchmark.md",
        ROOT / "docs/history/superseded-document-taxonomy/project-topics/deployment/microservice-deployment.md",
    ):
        content = path.read_text(encoding="utf-8")
        if _contains_process_trace(content):
            errors.append(f"{path.relative_to(ROOT)} contains Round/D/Q process trace")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify V3.1 Part A/Part B document quality")
    parser.add_argument("session", nargs="?", type=Path, default=DEFAULT_SESSION)
    args = parser.parse_args(argv)
    session = args.session if args.session.is_absolute() else ROOT / args.session
    errors = verify_quality(session)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("document quality V3.1 verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
