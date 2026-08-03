from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.evals.zuno.synthetic_benchmark.dataset_contract import sha256_json


REQUIRED_SOURCE_FIELDS = (
    "source_id",
    "document_id",
    "tenant_id",
    "workspace_id",
    "security_scope",
    "source_hash",
    "content_type",
    "source_path",
    "idempotency_key",
    "initial_state",
)


@dataclass
class SourceUploadManifestValidation:
    passed: bool
    errors: list[str] = field(default_factory=list)
    source_count: int = 0
    duplicate_source_count: int = 0
    source_manifest_hash: str | None = None


def _parse_front_matter_lines(body: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in body.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        normalized_key = key.strip()
        if normalized_key in {"document_id", "tenant_id", "workspace_id", "security_scope"}:
            metadata[normalized_key] = value.strip()
    return metadata


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_source_upload_manifest(corpus_root: Path) -> dict[str, Any]:
    sources: list[dict[str, Any]] = []
    for path in sorted(corpus_root.glob("*.md")):
        body = path.read_text(encoding="utf-8")
        metadata = _parse_front_matter_lines(body)
        document_id = metadata.get("document_id", path.stem)
        tenant_id = metadata.get("tenant_id")
        workspace_id = metadata.get("workspace_id")
        source_hash = _sha256_text(body)
        source_id = f"source::{tenant_id or 'missing_tenant'}::{workspace_id or 'missing_workspace'}::{document_id}"
        sources.append(
            {
                "source_id": source_id,
                "document_id": document_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "security_scope": metadata.get("security_scope"),
                "source_hash": source_hash,
                "content_type": "text/markdown; charset=utf-8",
                "source_path": f"corpus/{path.name}",
                "idempotency_key": f"phase22-source-upload::{tenant_id}::{workspace_id}::{source_hash}",
                "initial_state": "accepted",
            }
        )
    manifest = {
        "schema_version": "1.0.0",
        "track_id": "machine_attested_synthetic_regression",
        "status": "SOURCE_UPLOAD_INPUTS_PREPARED",
        "source_count": len(sources),
        "sources": sources,
        "runtime_ingested": False,
        "object_store_verified": False,
        "postgres_facts_verified": False,
    }
    manifest["source_manifest_hash"] = sha256_json(
        {key: value for key, value in manifest.items() if key != "source_manifest_hash"}
    )
    return manifest


def validate_source_upload_manifest(manifest: dict[str, Any]) -> SourceUploadManifestValidation:
    errors: list[str] = []
    duplicate_source_count = 0
    if manifest.get("track_id") != "machine_attested_synthetic_regression":
        errors.append("source upload manifest track_id mismatch")
    if manifest.get("status") != "SOURCE_UPLOAD_INPUTS_PREPARED":
        errors.append("source upload manifest status mismatch")
    for field_name in ["runtime_ingested", "object_store_verified", "postgres_facts_verified"]:
        if manifest.get(field_name) is not False:
            errors.append(f"{field_name} must remain false before real ingestion")
    sources = manifest.get("sources")
    if not isinstance(sources, list):
        errors.append("sources must be a list")
        sources = []
    if manifest.get("source_count") != len(sources):
        errors.append("source_count must match sources length")
    source_ids: set[str] = set()
    idempotency_keys: set[str] = set()
    for source in sources:
        if not isinstance(source, dict):
            errors.append("source entry must be an object")
            continue
        missing = [field_name for field_name in REQUIRED_SOURCE_FIELDS if field_name not in source]
        if missing:
            errors.append(f"{source.get('source_id', '<missing>')}: missing fields {missing}")
        source_id = source.get("source_id")
        if source_id in source_ids:
            duplicate_source_count += 1
            errors.append(f"{source_id}: duplicate source_id")
        source_ids.add(str(source_id))
        idempotency_key = source.get("idempotency_key")
        if idempotency_key in idempotency_keys:
            errors.append(f"{source_id}: duplicate idempotency_key")
        idempotency_keys.add(str(idempotency_key))
        for field_name in ["document_id", "tenant_id", "workspace_id", "security_scope", "source_hash"]:
            if not source.get(field_name):
                errors.append(f"{source_id}: missing {field_name}")
        if source.get("initial_state") != "accepted":
            errors.append(f"{source_id}: initial_state must be accepted")
        if not str(source.get("source_path", "")).startswith("corpus/"):
            errors.append(f"{source_id}: source_path must be corpus-relative")
    expected_hash = sha256_json(
        {key: value for key, value in manifest.items() if key != "source_manifest_hash"}
    )
    if manifest.get("source_manifest_hash") != expected_hash:
        errors.append("source_manifest_hash mismatch")
    return SourceUploadManifestValidation(
        passed=not errors,
        errors=errors,
        source_count=len(sources),
        duplicate_source_count=duplicate_source_count,
        source_manifest_hash=manifest.get("source_manifest_hash"),
    )


def write_source_upload_manifest(out_root: Path, *, corpus_root: Path) -> dict[str, Any]:
    out_root.mkdir(parents=True, exist_ok=True)
    manifest = build_source_upload_manifest(corpus_root)
    validation = validate_source_upload_manifest(manifest)
    (out_root / "source_upload_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    (out_root / "source_upload_manifest_report.json").write_text(
        json.dumps(validation.__dict__, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    return validation.__dict__


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-root", required=True, type=Path)
    parser.add_argument("--corpus-root", required=True, type=Path)
    args = parser.parse_args()
    result = write_source_upload_manifest(args.out_root, corpus_root=args.corpus_root)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
