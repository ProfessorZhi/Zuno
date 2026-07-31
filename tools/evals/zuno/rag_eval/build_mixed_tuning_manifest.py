from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def _referenced_file_names(dataset_path: Path) -> list[str]:
    names: set[str] = set()
    for sample in _read_jsonl(dataset_path):
        for evidence in sample.get("gold_evidence") or []:
            file_name = str(evidence.get("file_contains") or "").strip()
            if file_name:
                names.add(Path(file_name).name)
    return sorted(names)


def _load_manifest_rows(csv_path: Path) -> dict[str, dict[str, str]]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        return {
            row["sample_name"]: row
            for row in csv.DictReader(file)
            if row.get("sample_name")
        }


def build_manifest(*, dataset_path: Path, sample_manifest_csv: Path, source_root: Path) -> dict[str, Any]:
    rows_by_name = _load_manifest_rows(sample_manifest_csv)
    missing: list[str] = []
    files: list[dict[str, Any]] = []

    for file_name in _referenced_file_names(dataset_path):
        row = rows_by_name.get(file_name)
        if not row:
            missing.append(file_name)
            continue

        prepared_path = source_root / row["category"] / row["sample_name"]
        if not prepared_path.exists():
            missing.append(file_name)
            continue

        files.append(
            {
                "file_name": file_name,
                "prepared_path": str(prepared_path.resolve()),
                "category": row.get("category"),
                "extension": row.get("extension"),
                "size_bytes": int(row.get("size_bytes") or prepared_path.stat().st_size),
                "relative_path": row.get("relative_path"),
            }
        )

    return {
        "source": "mixed_tuning_v2",
        "dataset": str(dataset_path.resolve()),
        "sample_manifest_csv": str(sample_manifest_csv.resolve()),
        "source_root": str(source_root.resolve()),
        "referenced_file_count": len(files),
        "missing_file_count": len(missing),
        "missing_files": missing,
        "files": files,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a Zuno rag_eval manifest for mixed_tuning_v2 referenced files.")
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--sample-manifest-csv", required=True, type=Path)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    manifest = build_manifest(
        dataset_path=args.dataset,
        sample_manifest_csv=args.sample_manifest_csv,
        source_root=args.source_root,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "referenced_file_count": manifest["referenced_file_count"],
                "missing_file_count": manifest["missing_file_count"],
                "output": str(args.output),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
