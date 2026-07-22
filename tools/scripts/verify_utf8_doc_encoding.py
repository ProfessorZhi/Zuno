from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_SCAN_PATHS = [
    ".agent/programs/PHASE11_durable-ingestion-and-source-lineage.md",
    ".agent/programs/README.md",
    ".agent/programs/closure-checklist.md",
    ".agent/programs/current.md",
    ".agent/programs/implementation-roadmap.md",
    ".agent/programs/work-products/goal01-closure-matrix.md",
    ".agent/references/current-program.md",
    "docs/evidence/phase07-coordinator-closure.md",
    "docs/evidence/phase11-coordinator-closure.md",
    "docs/evidence/phase11-ingestion-source-lineage.md",
    "docs/evidence/phase11-pre-closure.md",
    "docs/status/production-readiness.md",
]

TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".py"}

MOJIBAKE_TOKENS = [
    "\ufffd",
    "\u951f",  # common replacement mojibake prefix
    "\u9286",
    "\u9306",
    "\u940d",
    "\u9428",
    "\u95bf",
    "\u95b5",
    "\u95bc",
    "\u9435",
    "\u9420",
    "\u745c",
    "\u5a75",
    "\u6fde",
    "\u9207",
    "\u4e75",
    "\u4e7b",
    "\u4e27",
    "\u4e28",
    "\u4e34",
]

MOJIBAKE_PATTERNS = [
    "銆",
    "锛",
    "鐨",
    "鍜",
    "涓€",
    "鏈",
    "閲",
    "绾",
    "垮",
    "乭",
    "丱",
    "並",
]


@dataclass(frozen=True)
class EncodingIssue:
    path: str
    reason: str


def _iter_text_files(relative_paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for relative_path in relative_paths:
        path = REPO_ROOT / relative_path
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            files.append(path)
        elif path.is_dir():
            files.extend(
                child
                for child in path.rglob("*")
                if child.is_file() and child.suffix.lower() in TEXT_SUFFIXES
            )
    return files


def _has_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def _mojibake_hits(text: str) -> list[str]:
    return [token for token in [*MOJIBAKE_TOKENS, *MOJIBAKE_PATTERNS] if token in text]


def _mojibake_density(text: str) -> float:
    if not text:
        return 0.0
    hit_count = sum(text.count(token) for token in MOJIBAKE_TOKENS)
    return hit_count / max(len(text), 1)


def verify_utf8_doc_encoding(paths: list[str] | None = None) -> list[EncodingIssue]:
    scan_paths = paths or DEFAULT_SCAN_PATHS
    issues: list[EncodingIssue] = []
    for path in _iter_text_files(scan_paths):
        relative = path.relative_to(REPO_ROOT).as_posix()
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            issues.append(EncodingIssue(relative, "UTF-8 BOM is not allowed"))
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            issues.append(EncodingIssue(relative, f"not valid UTF-8: {exc}"))
            continue
        hits = _mojibake_hits(text)
        if hits and _has_cjk(text):
            unique_hits = ", ".join(f"U+{ord(token):04X}" for token in sorted(set(hits))[:8])
            issues.append(EncodingIssue(relative, f"possible mojibake tokens: {unique_hits}"))
        if _mojibake_density(text) > 0.002:
            issues.append(EncodingIssue(relative, "abnormal mojibake token density"))
    return issues


def main() -> int:
    issues = verify_utf8_doc_encoding()
    if not issues:
        print("UTF-8 document encoding verification passed.")
        return 0
    for issue in issues:
        print(f"ERROR: {issue.path}: {issue.reason}")
    print("UTF-8 document encoding verification failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
