from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    errors: list[str] = []
    for pattern in ("*.db", "*.sqlite", "*.sqlite3"):
        for path in ROOT.glob(pattern):
            errors.append(f"root database artifact: {path.name}")

    for path in (ROOT / "src" / "backend").rglob("*.py"):
        content = path.read_text(encoding="utf-8", errors="ignore")
        if "WorkspaceTaskRuntimeService" in content or "workspace_task_runtime" in content:
            errors.append(f"retired runtime owner reference: {path.relative_to(ROOT)}")

    for path in (ROOT / "tools" / "scripts").glob("*.py"):
        if re.search(r"(?:phase|legacy|cutover)", path.name, re.IGNORECASE):
            errors.append(f"retired verifier filename: {path.relative_to(ROOT)}")
    for path in (ROOT / "tests").rglob("*.py"):
        if re.search(r"(?:^|[_\\-])(phase|legacy|cutover)(?:[_\\-]|$)", path.stem, re.IGNORECASE):
            errors.append(f"retired test filename: {path.relative_to(ROOT)}")

    source_files = list((ROOT / "src").rglob("*.py")) + list((ROOT / "apps").rglob("*.ts"))
    floating = re.compile(r"#\s*(TODO|FIXME|HACK)\b|//\s*(TODO|FIXME|HACK)\b")
    for path in source_files:
        for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if floating.search(line):
                errors.append(f"floating cleanup marker: {path.relative_to(ROOT)}:{line_number}")

    if errors:
        print("REPO_HYGIENE_INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("REPO_HYGIENE_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
