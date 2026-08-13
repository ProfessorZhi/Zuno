from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

REPO_ROOT = Path(__file__).resolve().parents[2]
EXCLUDED_PREFIXES = (
    "tests/fixtures/",
    # Superseded raw documents are retained for audit; their historical links
    # may intentionally point to paths that no longer exist as active sources.
    "docs/history/superseded-document-taxonomy/",
    # Red/Blue protocol and prompt archives preserve the paths and vocabulary
    # of their original execution context; active routing must not read them.
    "project-reconstruction-lab/05-red-blue/history/",
)
MARKDOWN_LINK = re.compile(
    r"!?\[[^\]]*\]\(\s*(?P<target><[^>]*>|[^\s)]+)(?:\s+[^)]*)?\s*\)"
)


def _tracked_markdown_files() -> list[Path]:
    result = subprocess.run(
        ["git", "-c", "core.quotepath=false", "ls-files", "-z", "--", "*.md"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    paths = result.stdout.split(b"\0")
    tracked = [path.decode("utf-8") for path in paths if path]
    return [
        REPO_ROOT / path
        for path in tracked
        if not path.replace("\\", "/").startswith(EXCLUDED_PREFIXES)
    ]


def _is_external(target: str) -> bool:
    lowered = target.lower()
    return (
        not target
        or target.startswith("#")
        or target.startswith("//")
        or lowered.startswith(("http:", "https:", "mailto:", "tel:", "ftp:", "file:"))
    )


def _target_path(source: Path, target: str) -> Path | None:
    target = target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    target = unquote(target.split("#", 1)[0].split("?", 1)[0])
    if _is_external(target):
        return None
    if target.startswith("/"):
        return REPO_ROOT / target.lstrip("/")
    return source.parent / target


def verify() -> list[str]:
    errors: list[str] = []
    for source in _tracked_markdown_files():
        lines = source.read_text(encoding="utf-8").splitlines()
        in_fence = False
        for line_number, line in enumerate(lines, start=1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for match in MARKDOWN_LINK.finditer(line):
                target = match.group("target")
                path = _target_path(source, target)
                if path is not None and not path.exists():
                    relative_source = source.relative_to(REPO_ROOT).as_posix()
                    errors.append(
                        f"{relative_source}:{line_number}: broken internal link: {target}"
                    )
    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"markdown internal-link verification failed: {len(errors)} error(s).")
        return 1
    print("markdown internal-link verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
