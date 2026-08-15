from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
COMMON_CASE = "复杂案件分析"
DOCUMENT_REQUIREMENTS = {
    "docs/architecture/architecture.md": (
        "Application & Integration", "Legal Domain & Work Product", "Knowledge & Evidence",
        "Agent Runtime & Control", "Tool Runtime & Effects", "Security & Governance",
        "模块化 Python 后端", "FastAPI", "LangGraph", "Reconciliation", "Current", "Target", "History",
    ),
}


def verify() -> list[str]:
    errors: list[str] = []
    for relative_path, required_tokens in DOCUMENT_REQUIREMENTS.items():
        path = REPO_ROOT / relative_path
        if not path.exists():
            errors.append(f"missing deep-dive document: {relative_path}")
            continue
        text = path.read_text(encoding="utf-8")
        if COMMON_CASE not in text and not any(marker in text for marker in ("Matter", "New Evidence", "A/B/C", "Target flow")):
            errors.append(f"{relative_path} missing unified case: {COMMON_CASE}")
        if not any(marker in text for marker in ("Target", "Current", "Hypothesis")):
            errors.append(f"{relative_path} must retain an explicit status boundary")
        text_lower = text.lower()
        for token in required_tokens:
            if token.lower() not in text_lower:
                errors.append(f"{relative_path} missing deep-dive contract token: {token}")
    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("deep dive architecture verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
