from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[5]
REGISTRY_PATH = REPO_ROOT / "tools" / "evals" / "zuno" / "rag_eval" / "datasets" / "public_dataset_registry.yaml"
CACHE_ROOT = REPO_ROOT / ".local" / "eval-datasets"


def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def calculate_sha256(file_path: Path) -> str:
    sha = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def generate_download_plan(registry: dict[str, Any], max_size_mb: int = 500) -> dict[str, Any]:
    plan = {
        "status": "external_dataset_download_pending",
        "max_allowed_size_mb": max_size_mb,
        "datasets": [],
    }
    for item in registry.get("datasets", []):
        plan["datasets"].append({
            "source_id": item.get("source_id"),
            "name": item.get("official_name"),
            "license": item.get("license"),
            "cache_path": item.get("local_cache_path"),
            "download_method": item.get("download_method"),
            "expected_files": item.get("expected_files", []),
        })
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(description="Download public evaluation datasets securely and idempotently.")
    parser.add_argument("--dry-run", action="store_true", help="Generate download plan without actual download.")
    parser.add_argument("--max-size-mb", type=int, default=500, help="Maximum allowed download size in MB.")
    args = parser.parse_args()

    registry = load_registry()
    plan = generate_download_plan(registry, max_size_mb=args.max_size_mb)

    CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    plan_file = CACHE_ROOT / "download_plan.json"
    plan_file.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": "download_plan_created",
        "plan_file": str(plan_file.relative_to(REPO_ROOT)),
        "datasets_count": len(plan["datasets"]),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
