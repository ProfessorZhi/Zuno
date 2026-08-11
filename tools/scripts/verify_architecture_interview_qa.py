from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
QA_ROOT = REPO_ROOT / "docs/verification/interview-qa"
DEEP_DIVE_PATH = QA_ROOT / "deep-dive-chains.md"
QA_FILES = {
    "zuno-agentic-graphrag-qa.md": "knowledge",
    "zuno-tool-mcp-security-qa.md": "tool",
    "zuno-memory-context-qa.md": "memory",
    "zuno-memory-information-extraction-qa.md": "memory-extraction",
    "zuno-agent-core-qa.md": "agent",
    "zuno-cross-module-system-design-qa.md": "cross-module",
}
EXPECTED_DOMAIN_COUNTS = {
    "knowledge": 65,
    "tool": 58,
    "memory": 44,
    "memory-extraction": 35,
    "agent": 45,
    "cross-module": 20,
}
EXPECTED_ARCHITECTURE_FILES = {
    "README.md",
    "architecture.md",
    "architecture-views.md",
    "architecture.html",
}
SOURCE_TYPES = {"REAL", "DERIVED", "ARCHITECTURE_STRESS"}
COVERAGE_VALUES = {"FULL", "PARTIAL", "MISSING", "CONFLICTING"}
REQUIRED_FIELDS = (
    "source_type",
    "source_ref",
    "primary_domain",
    "difficulty",
    "interview_probability",
    "resume_trigger",
    "architecture_refs",
    "initial_coverage_status",
    "coverage_status",
    "gap_id",
    "status",
)
REQUIRED_HEADINGS = (
    "### 面试官问题",
    "### 他真正想考什么",
    "### 30 秒回答",
    "### 深挖回答",
    "### 可能继续追问",
    "### Architecture Evidence",
    "### 当前文档是否足够回答",
    "### 如果不够，缺什么",
)
DEEP_DIVE_REQUIRED_FIELDS = (
    "target_documents",
    "architecture_coverage",
    "human_explainability",
    "gap_type",
    "resolution_state",
)


def _question_blocks(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"^## (Q\d{3}) (.+)$", text, re.MULTILINE))
    return [
        (
            match.group(1),
            text[match.start() : matches[index + 1].start() if index + 1 < len(matches) else len(text)],
        )
        for index, match in enumerate(matches)
    ]


def verify() -> list[str]:
    errors: list[str] = []
    if not QA_ROOT.exists():
        return ["missing QA root: docs/verification/interview-qa"]

    if not DEEP_DIVE_PATH.exists():
        errors.append("missing red-team deep-dive chain file: docs/verification/interview-qa/deep-dive-chains.md")
    else:
        deep_dive_text = DEEP_DIVE_PATH.read_text(encoding="utf-8")
        deep_dive_chains = list(re.finditer(r"^## (RT-[A-Z]+-\d{3}) (.+)$", deep_dive_text, re.MULTILINE))
        if len(deep_dive_chains) != 10:
            errors.append(f"expected exactly 10 red-team deep-dive chains, got {len(deep_dive_chains)}")
        for index, match in enumerate(deep_dive_chains):
            end = deep_dive_chains[index + 1].start() if index + 1 < len(deep_dive_chains) else len(deep_dive_text)
            block = deep_dive_text[match.start() : end]
            for field in DEEP_DIVE_REQUIRED_FIELDS:
                if not re.search(rf"^- {re.escape(field)}:\s*.+$", block, re.MULTILINE):
                    errors.append(f"{match.group(1)} missing field: {field}")
            for heading in ("### Attack Chain", "### Weakness Record"):
                if heading not in block:
                    errors.append(f"{match.group(1)} missing section: {heading}")

    architecture_root = REPO_ROOT / "docs/project/architecture"
    architecture_files = {path.name for path in architecture_root.iterdir() if path.is_file()}
    architecture_dirs = [path.name for path in architecture_root.iterdir() if path.is_dir()]
    if architecture_files != EXPECTED_ARCHITECTURE_FILES:
        errors.append(f"docs/project/architecture file set changed: {sorted(architecture_files)}")
    if architecture_dirs:
        errors.append(f"docs/project/architecture must not contain subdirectories: {architecture_dirs}")
    if (REPO_ROOT / "docs/validation/architecture-interview-qa").exists():
        errors.append("retired docs/validation/architecture-interview-qa path must not exist")

    all_questions: list[tuple[str, str, str]] = []
    chain_count = 0
    for filename, expected_domain in QA_FILES.items():
        path = QA_ROOT / filename
        if not path.exists():
            errors.append(f"missing QA file: {path.relative_to(REPO_ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        chain_count += len(re.findall(r"^### Interview Drill Chain ", text, re.MULTILINE))
        for qid, block in _question_blocks(text):
            all_questions.append((qid, block, expected_domain))
            for field in REQUIRED_FIELDS:
                if not re.search(rf"^- {re.escape(field)}:\s*.+$", block, re.MULTILINE):
                    errors.append(f"{qid} missing field: {field}")
            for heading in REQUIRED_HEADINGS:
                if heading not in block:
                    errors.append(f"{qid} missing section: {heading}")
            source_type_match = re.search(r"^- source_type:\s*(\S+)$", block, re.MULTILINE)
            if source_type_match and source_type_match.group(1) not in SOURCE_TYPES:
                errors.append(f"{qid} has invalid source_type: {source_type_match.group(1)}")
            domain_match = re.search(r"^- primary_domain:\s*(\S+)$", block, re.MULTILINE)
            if domain_match and domain_match.group(1) != expected_domain:
                errors.append(f"{qid} domain mismatch: {domain_match.group(1)} != {expected_domain}")
            difficulty_match = re.search(r"^- difficulty:\s*(L[1-8])$", block, re.MULTILINE)
            if not difficulty_match:
                errors.append(f"{qid} has invalid difficulty")
            coverage_match = re.search(r"^- coverage_status:\s*(\S+)$", block, re.MULTILINE)
            if coverage_match and coverage_match.group(1) not in COVERAGE_VALUES:
                errors.append(f"{qid} has invalid coverage_status: {coverage_match.group(1)}")
            initial_match = re.search(r"^- initial_coverage_status:\s*(FULL|PARTIAL|MISSING|CONFLICTING)$", block, re.MULTILINE)
            gap_match = re.search(r"^- gap_id:\s*(\S+)$", block, re.MULTILINE)
            if initial_match and initial_match.group(1) != "FULL" and (not gap_match or gap_match.group(1) == "None"):
                errors.append(f"{qid} initial non-FULL coverage has no gap_id")
            if coverage_match and coverage_match.group(1) != "FULL" and (not gap_match or gap_match.group(1) == "None"):
                errors.append(f"{qid} non-FULL coverage has no gap_id")
            for ref_file, heading in re.findall(r"^  - (.+?) — § (.+)$", block, re.MULTILINE):
                target = REPO_ROOT / ref_file
                if not target.exists():
                    errors.append(f"{qid} references missing canonical file: {ref_file}")
                elif heading not in target.read_text(encoding="utf-8"):
                    errors.append(f"{qid} references missing heading: {ref_file} — § {heading}")
            followup_match = re.search(r"### 可能继续追问\n\n(.+?)(?=\n\n### )", block, re.DOTALL)
            if followup_match and len(re.findall(r"^\d+\. ", followup_match.group(1), re.MULTILINE)) < 2:
                errors.append(f"{qid} must have at least two follow-up questions")

    ids = [int(qid[1:]) for qid, _, _ in all_questions]
    if len(all_questions) != 267:
        errors.append(f"expected exactly 267 QA questions, got {len(all_questions)}")
    if len(set(ids)) != len(ids):
        errors.append("QA question IDs are not unique")
    if sorted(ids) != list(range(1, 268)):
        errors.append("QA question IDs must be continuous Q001..Q267")
    counts: dict[str, int] = {}
    for _, _, domain in all_questions:
        counts[domain] = counts.get(domain, 0) + 1
    if counts != EXPECTED_DOMAIN_COUNTS:
        errors.append(f"domain quota mismatch: expected {EXPECTED_DOMAIN_COUNTS}, got {counts}")
    if chain_count < 20:
        errors.append(f"expected at least 20 Interview Drill Chains, got {chain_count}")

    if "docs/verification/interview-qa" in (REPO_ROOT / "docs/project/architecture/README.md").read_text(encoding="utf-8"):
        errors.append("QA corpus must not be registered as canonical architecture")
    if "docs/verification/interview-qa" in (REPO_ROOT / ".agent/system.yaml").read_text(encoding="utf-8"):
        errors.append("QA corpus must not be registered as an architecture fact source in system.yaml")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("architecture interview QA verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
