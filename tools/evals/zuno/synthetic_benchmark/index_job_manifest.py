from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.evals.zuno.synthetic_benchmark.dataset_contract import sha256_json


INDEX_KINDS = ("elasticsearch_bm25", "milvus_vector", "neo4j_graph")


@dataclass
class IndexJobManifestValidation:
    passed: bool
    errors: list[str] = field(default_factory=list)
    index_job_count: int = 0
    elasticsearch_job_count: int = 0
    milvus_job_count: int = 0
    neo4j_job_count: int = 0
    index_job_manifest_hash: str | None = None


def build_index_job_manifest(canonical_ir_manifest: dict[str, Any]) -> dict[str, Any]:
    canonical_ir_hash = canonical_ir_manifest["canonical_ir_hash"]
    tenant_ids = sorted({doc["tenant_id"] for doc in canonical_ir_manifest["documents"]})
    workspace_ids = sorted({doc["workspace_id"] for doc in canonical_ir_manifest["documents"]})
    chunks = canonical_ir_manifest["chunks"]
    entities = canonical_ir_manifest["entities"]
    relations = canonical_ir_manifest["relations"]
    jobs: list[dict[str, Any]] = []

    for kind in INDEX_KINDS:
        payload_refs = {
            "elasticsearch_bm25": [chunk["chunk_id"] for chunk in chunks],
            "milvus_vector": [chunk["chunk_id"] for chunk in chunks],
            "neo4j_graph": [entity["entity_ref"] for entity in entities]
            + [relation["relation_id"] for relation in relations],
        }[kind]
        jobs.append(
            {
                "index_job_id": f"index-job::{kind}::{canonical_ir_hash[:16]}",
                "index_kind": kind,
                "tenant_ids": tenant_ids,
                "workspace_ids": workspace_ids,
                "canonical_ir_hash": canonical_ir_hash,
                "payload_ref_count": len(payload_refs),
                "payload_refs_hash": sha256_json(payload_refs),
                "state": "prepared",
                "submitted_to_worker": False,
                "write_read_verified": False,
                "visibility_receipt_ref": None,
                "idempotency_key": f"phase22-index-job::{kind}::{canonical_ir_hash}",
            }
        )

    manifest = {
        "schema_version": "1.0.0",
        "track_id": "machine_attested_synthetic_regression",
        "status": "INDEX_JOBS_PREPARED",
        "canonical_ir_hash": canonical_ir_hash,
        "index_job_count": len(jobs),
        "index_kinds": list(INDEX_KINDS),
        "jobs": jobs,
        "indexes_visible": False,
        "visibility_receipt_refs": [],
        "snapshot_activation_allowed": False,
        "snapshot_activation_block_reason": "index_visibility_receipts_missing",
    }
    manifest["index_job_manifest_hash"] = sha256_json(
        {key: value for key, value in manifest.items() if key != "index_job_manifest_hash"}
    )
    return manifest


def validate_index_job_manifest(manifest: dict[str, Any]) -> IndexJobManifestValidation:
    errors: list[str] = []
    if manifest.get("track_id") != "machine_attested_synthetic_regression":
        errors.append("index job manifest track_id mismatch")
    if manifest.get("status") != "INDEX_JOBS_PREPARED":
        errors.append("index job manifest status mismatch")
    if tuple(manifest.get("index_kinds", [])) != INDEX_KINDS:
        errors.append("index job manifest index_kinds mismatch")
    if manifest.get("indexes_visible") is not False:
        errors.append("indexes_visible must remain false before write/read verification")
    if manifest.get("visibility_receipt_refs") != []:
        errors.append("visibility_receipt_refs must be empty before adapter visibility")
    if manifest.get("snapshot_activation_allowed") is not False:
        errors.append("snapshot_activation_allowed must remain false before all visibility receipts")
    if manifest.get("snapshot_activation_block_reason") != "index_visibility_receipts_missing":
        errors.append("snapshot_activation_block_reason mismatch")
    jobs = manifest.get("jobs")
    if not isinstance(jobs, list):
        errors.append("jobs must be a list")
        jobs = []
    if manifest.get("index_job_count") != len(jobs):
        errors.append("index_job_count must match jobs length")
    job_ids: set[str] = set()
    job_counts = {kind: 0 for kind in INDEX_KINDS}
    for job in jobs:
        if not isinstance(job, dict):
            errors.append("index job entry must be an object")
            continue
        kind = job.get("index_kind")
        if kind not in INDEX_KINDS:
            errors.append(f"{job.get('index_job_id', '<missing>')}: unsupported index_kind")
            continue
        job_counts[kind] += 1
        job_id = job.get("index_job_id")
        if job_id in job_ids:
            errors.append(f"{job_id}: duplicate index_job_id")
        job_ids.add(str(job_id))
        for field_name in [
            "tenant_ids",
            "workspace_ids",
            "canonical_ir_hash",
            "payload_ref_count",
            "payload_refs_hash",
            "idempotency_key",
        ]:
            if not job.get(field_name):
                errors.append(f"{job_id}: missing {field_name}")
        if job.get("state") != "prepared":
            errors.append(f"{job_id}: state must be prepared")
        for field_name in ["submitted_to_worker", "write_read_verified"]:
            if job.get(field_name) is not False:
                errors.append(f"{job_id}: {field_name} must be false")
        if job.get("visibility_receipt_ref") is not None:
            errors.append(f"{job_id}: visibility_receipt_ref must be null before visibility")
    for kind, count in job_counts.items():
        if count != 1:
            errors.append(f"{kind}: expected exactly one prepared job")
    expected_hash = sha256_json(
        {key: value for key, value in manifest.items() if key != "index_job_manifest_hash"}
    )
    if manifest.get("index_job_manifest_hash") != expected_hash:
        errors.append("index_job_manifest_hash mismatch")
    return IndexJobManifestValidation(
        passed=not errors,
        errors=errors,
        index_job_count=len(jobs),
        elasticsearch_job_count=job_counts["elasticsearch_bm25"],
        milvus_job_count=job_counts["milvus_vector"],
        neo4j_job_count=job_counts["neo4j_graph"],
        index_job_manifest_hash=manifest.get("index_job_manifest_hash"),
    )


def write_index_job_manifest(out_root: Path, *, canonical_ir_manifest_path: Path) -> dict[str, Any]:
    out_root.mkdir(parents=True, exist_ok=True)
    canonical_ir_manifest = json.loads(canonical_ir_manifest_path.read_text(encoding="utf-8"))
    manifest = build_index_job_manifest(canonical_ir_manifest)
    validation = validate_index_job_manifest(manifest)
    (out_root / "index_job_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    (out_root / "index_job_manifest_report.json").write_text(
        json.dumps(validation.__dict__, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    return validation.__dict__


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-root", required=True, type=Path)
    parser.add_argument("--canonical-ir-manifest", required=True, type=Path)
    args = parser.parse_args()
    result = write_index_job_manifest(args.out_root, canonical_ir_manifest_path=args.canonical_ir_manifest)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
