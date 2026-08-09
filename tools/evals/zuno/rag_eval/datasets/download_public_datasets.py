from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import urllib.request
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[5]
REGISTRY_PATH = REPO_ROOT / "tools" / "evals" / "zuno" / "rag_eval" / "datasets" / "public_dataset_registry.yaml"
CACHE_ROOT = REPO_ROOT / ".local" / "eval-datasets"
GRAPH_RAG_TEXTBOOK_FILES = tuple(
    f"textbooks/textbook{index}/textbook{index}.md" for index in range(1, 21)
)


def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def calculate_sha256(file_path: Path) -> str:
    sha = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def fetch_url_bytes(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def download_hotpot_qa(cache_dir: Path) -> dict[str, Any]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    out_file = cache_dir / "hotpot_dev_distractor_v1.json"

    if not out_file.exists() or out_file.stat().st_size < 1000:
        rows_data = []
        for offset in (0, 100):
            url = f"https://datasets-server.huggingface.co/rows?dataset=hotpotqa/hotpot_qa&config=distractor&split=validation&offset={offset}&limit=100"
            raw = fetch_url_bytes(url)
            parsed = json.loads(raw)
            for r in parsed.get("rows", []):
                rows_data.append(r.get("row", {}))

        tmp_file = cache_dir / "hotpot_dev_distractor_v1.json.tmp"
        tmp_file.write_text(json.dumps(rows_data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp_file.replace(out_file)

    sha256 = calculate_sha256(out_file)
    return {
        "source_id": "hotpot_qa",
        "file": str(out_file.relative_to(REPO_ROOT)),
        "size_bytes": out_file.stat().st_size,
        "sha256": sha256,
    }


def download_multihop_rag(cache_dir: Path) -> dict[str, Any]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    queries_file = cache_dir / "queries.json"
    corpus_file = cache_dir / "corpus.json"

    if not queries_file.exists() or queries_file.stat().st_size < 1000:
        rows_data = []
        for offset in (0, 100):
            url = f"https://datasets-server.huggingface.co/rows?dataset=yixuantt/MultiHopRAG&config=MultiHopRAG&split=train&offset={offset}&limit=100"
            raw = fetch_url_bytes(url)
            parsed = json.loads(raw)
            for r in parsed.get("rows", []):
                rows_data.append(r.get("row", {}))

        tmp_file = cache_dir / "queries.json.tmp"
        tmp_file.write_text(json.dumps(rows_data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp_file.replace(queries_file)

    if not corpus_file.exists() or corpus_file.stat().st_size < 1000:
        corpus_data = []
        for offset in (0, 100):
            url = f"https://datasets-server.huggingface.co/rows?dataset=yixuantt/MultiHopRAG&config=corpus&split=train&offset={offset}&limit=100"
            raw = fetch_url_bytes(url)
            parsed = json.loads(raw)
            for r in parsed.get("rows", []):
                corpus_data.append(r.get("row", {}))

        tmp_file = cache_dir / "corpus.json.tmp"
        tmp_file.write_text(json.dumps(corpus_data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp_file.replace(corpus_file)

    sha_q = calculate_sha256(queries_file)
    sha_c = calculate_sha256(corpus_file)
    return {
        "source_id": "multihop_rag",
        "queries_file": str(queries_file.relative_to(REPO_ROOT)),
        "corpus_file": str(corpus_file.relative_to(REPO_ROOT)),
        "queries_sha256": sha_q,
        "corpus_sha256": sha_c,
    }


def download_microsoft_graphrag(cache_dir: Path) -> dict[str, Any]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    questions_file = cache_dir / "questions.jsonl"

    if not questions_file.exists() or questions_file.stat().st_size < 1000:
        url = "https://huggingface.co/datasets/Awesome-GraphRAG/GraphRAG-Bench/raw/main/questions/OE.jsonl"
        raw = fetch_url_bytes(url)

        tmp_file = cache_dir / "questions.jsonl.tmp"
        tmp_file.write_bytes(raw)
        tmp_file.replace(questions_file)

    files = [{
        "path": str(questions_file.relative_to(REPO_ROOT)),
        "size_bytes": questions_file.stat().st_size,
        "sha256": calculate_sha256(questions_file),
    }]

    for relative_path in GRAPH_RAG_TEXTBOOK_FILES:
        textbook_file = cache_dir / relative_path
        textbook_file.parent.mkdir(parents=True, exist_ok=True)
        if not textbook_file.exists() or textbook_file.stat().st_size < 1000:
            url = (
                "https://huggingface.co/datasets/Awesome-GraphRAG/GraphRAG-Bench/"
                f"resolve/main/{relative_path}?download=true"
            )
            raw = fetch_url_bytes(url)
            tmp_file = textbook_file.with_suffix(textbook_file.suffix + ".tmp")
            tmp_file.write_bytes(raw)
            tmp_file.replace(textbook_file)
        files.append({
            "path": str(textbook_file.relative_to(REPO_ROOT)),
            "size_bytes": textbook_file.stat().st_size,
            "sha256": calculate_sha256(textbook_file),
        })

    return {
        "source_id": "microsoft_graphrag_benchmarking",
        "file": files[0]["path"],
        "size_bytes": files[0]["size_bytes"],
        "sha256": files[0]["sha256"],
        "files": files,
        "corpus_files": [item["path"] for item in files[1:]],
    }


def generate_download_plan(registry: dict[str, Any], max_size_mb: int = 5000) -> dict[str, Any]:
    plan = {
        "status": "external_dataset_download_configured",
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
    parser.add_argument("--max-size-mb", type=int, default=5000, help="Maximum allowed download size in MB.")
    args = parser.parse_args()

    registry = load_registry()
    plan = generate_download_plan(registry, max_size_mb=args.max_size_mb)

    CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    plan_file = CACHE_ROOT / "download_plan.json"
    plan_file.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.dry_run:
        print(json.dumps({"status": "download_plan_created", "plan_file": str(plan_file.relative_to(REPO_ROOT))}))
        return 0

    download_results = []
    # 1. HotpotQA
    h_res = download_hotpot_qa(CACHE_ROOT / "hotpot_qa")
    download_results.append(h_res)

    # 2. MultiHop-RAG
    m_res = download_multihop_rag(CACHE_ROOT / "multihop_rag")
    download_results.append(m_res)

    # 3. Microsoft GraphRAG
    g_res = download_microsoft_graphrag(CACHE_ROOT / "microsoft_graphrag")
    download_results.append(g_res)

    print(json.dumps({
        "status": "datasets_downloaded_and_cached",
        "cache_root": str(CACHE_ROOT.relative_to(REPO_ROOT)),
        "download_results": download_results,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
