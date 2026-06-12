from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from agentchat.evals.rag_eval.paths import default_corpus_root


DEFAULT_INCLUDE_NAMES = {
    "Python 关键字.md",
    "Python 变量、命名空间与对象绑定.md",
    "Python 如何读函数与方法签名.md",
    "Python 深拷贝与浅拷贝.md",
    "collections.md",
    "dataclasses.md",
    "contextlib.md",
    "functools.md",
}


def collect_markdown_files(source: Path, limit_files: int | None = None) -> list[Path]:
    files = [
        path
        for path in source.rglob("*.md")
        if path.name != "AGENTS.md" and not path.name.lower().startswith("map")
    ]
    preferred = [path for path in files if path.name in DEFAULT_INCLUDE_NAMES]
    remaining = [path for path in files if path.name not in DEFAULT_INCLUDE_NAMES]
    ordered = []
    seen_names = set()
    for path in preferred + remaining:
        if path.name in seen_names:
            continue
        seen_names.add(path.name)
        ordered.append(path)
    return ordered[:limit_files] if limit_files else ordered


def prepare_corpus(source: Path, output_dir: Path, limit_files: int | None = None) -> dict:
    if not source.exists():
        raise FileNotFoundError(f"source path does not exist: {source}")

    output_dir.mkdir(parents=True, exist_ok=True)
    files_dir = output_dir / "files"
    files_dir.mkdir(parents=True, exist_ok=True)
    for stale_file in files_dir.glob("*.md"):
        stale_file.unlink()

    manifest_rows = []
    for index, source_file in enumerate(collect_markdown_files(source, limit_files), start=1):
        safe_name = f"{index:03d}_{source_file.name}"
        target_file = files_dir / safe_name
        shutil.copy2(source_file, target_file)
        manifest_rows.append(
            {
                "source_path": str(source_file),
                "relative_source_path": str(source_file.relative_to(source)),
                "prepared_path": str(target_file),
                "file_name": source_file.name,
                "size_bytes": target_file.stat().st_size,
            }
        )

    manifest = {
        "source": str(source),
        "output_dir": str(output_dir),
        "file_count": len(manifest_rows),
        "files": manifest_rows,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare local Python notes for Zuno RAG eval.")
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output-dir", default=default_corpus_root() / "python_notes", type=Path)
    parser.add_argument("--limit-files", type=int, default=40)
    args = parser.parse_args()

    manifest = prepare_corpus(args.source, args.output_dir, args.limit_files)
    print(json.dumps({"file_count": manifest["file_count"], "output_dir": manifest["output_dir"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
