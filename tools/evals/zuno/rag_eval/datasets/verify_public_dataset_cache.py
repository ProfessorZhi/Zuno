from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[5]
REGISTRY_PATH = REPO_ROOT / "tools" / "evals" / "zuno" / "rag_eval" / "datasets" / "public_dataset_registry.yaml"


def verify_dataset_cache(registry_path: Path = REGISTRY_PATH) -> dict[str, Any]:
    with registry_path.open("r", encoding="utf-8") as f:
        registry = yaml.safe_load(f)

    results: list[dict[str, Any]] = []
    missing_count = 0

    for item in registry.get("datasets", []):
        source_id = item.get("source_id")
        cache_dir = REPO_ROOT / item.get("local_cache_path", "")
        expected_files = item.get("expected_files", [])

        file_status: dict[str, bool] = {}
        all_present = True
        for fname in expected_files:
            fpath = cache_dir / fname
            exists = fpath.exists()
            file_status[fname] = exists
            if not exists:
                all_present = False

        if not all_present:
            missing_count += 1

        results.append({
            "source_id": source_id,
            "cache_dir": str(cache_dir.relative_to(REPO_ROOT)) if cache_dir.is_relative_to(REPO_ROOT) else str(cache_dir),
            "status": "ready" if all_present else "missing_files",
            "files": file_status,
        })

    return {
        "verified_at": "pretest_readiness",
        "total_datasets": len(results),
        "missing_datasets": missing_count,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify public evaluation dataset local cache status.")
    args = parser.parse_args()

    report = verify_dataset_cache()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
