from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.evals.zuno.synthetic_benchmark.dataset_contract import sha256_json


REQUIRED_RECEIPT_KINDS = (
    "elasticsearch_bm25_visibility",
    "milvus_vector_visibility",
    "neo4j_graph_visibility",
)


@dataclass
class SnapshotActivationManifestValidation:
    passed: bool
    errors: list[str] = field(default_factory=list)
    required_receipt_count: int = 0
    provided_receipt_count: int = 0
    missing_receipt_count: int = 0
    activation_allowed: bool = False
    snapshot_activation_manifest_hash: str | None = None


def build_snapshot_activation_manifest(index_job_manifest: dict[str, Any]) -> dict[str, Any]:
    provided_receipts = [
        receipt
        for receipt in index_job_manifest.get("visibility_receipt_refs", [])
        if isinstance(receipt, dict)
    ]
    provided_kinds = {receipt.get("receipt_kind") for receipt in provided_receipts}
    missing = [kind for kind in REQUIRED_RECEIPT_KINDS if kind not in provided_kinds]
    activation_allowed = not missing and index_job_manifest.get("indexes_visible") is True
    manifest = {
        "schema_version": "1.0.0",
        "track_id": "machine_attested_synthetic_regression",
        "status": "snapshot_activation_ready" if activation_allowed else "snapshot_activation_blocked",
        "index_job_manifest_hash": index_job_manifest.get("index_job_manifest_hash"),
        "required_receipt_kinds": list(REQUIRED_RECEIPT_KINDS),
        "provided_receipt_count": len(provided_receipts),
        "missing_receipt_kinds": missing,
        "activation_allowed": activation_allowed,
        "snapshot_id": "pending_runtime_snapshot" if activation_allowed else None,
        "snapshot_content_hash": None,
        "activation_receipt_ref": None,
        "block_reason": None if activation_allowed else "index_visibility_receipts_missing",
    }
    manifest["snapshot_activation_manifest_hash"] = sha256_json(
        {key: value for key, value in manifest.items() if key != "snapshot_activation_manifest_hash"}
    )
    return manifest


def validate_snapshot_activation_manifest(manifest: dict[str, Any]) -> SnapshotActivationManifestValidation:
    errors: list[str] = []
    if manifest.get("track_id") != "machine_attested_synthetic_regression":
        errors.append("snapshot activation manifest track_id mismatch")
    if manifest.get("required_receipt_kinds") != list(REQUIRED_RECEIPT_KINDS):
        errors.append("snapshot activation manifest required_receipt_kinds mismatch")
    missing = manifest.get("missing_receipt_kinds")
    if not isinstance(missing, list):
        errors.append("missing_receipt_kinds must be a list")
        missing = []
    activation_allowed = manifest.get("activation_allowed")
    if missing:
        if manifest.get("status") != "snapshot_activation_blocked":
            errors.append("snapshot activation must be blocked when receipts are missing")
        if activation_allowed is not False:
            errors.append("activation_allowed must be false when receipts are missing")
        if manifest.get("snapshot_id") is not None:
            errors.append("snapshot_id must be null when activation is blocked")
        if manifest.get("activation_receipt_ref") is not None:
            errors.append("activation_receipt_ref must be null when activation is blocked")
        if manifest.get("block_reason") != "index_visibility_receipts_missing":
            errors.append("block_reason must be index_visibility_receipts_missing")
    else:
        if manifest.get("status") != "snapshot_activation_ready":
            errors.append("snapshot activation status must be ready when receipts are complete")
        if activation_allowed is not True:
            errors.append("activation_allowed must be true when receipts are complete")
        if manifest.get("provided_receipt_count") != 0:
            errors.append("provided_receipt_count must be 0 before real adapter receipts")
    expected_hash = sha256_json(
        {key: value for key, value in manifest.items() if key != "snapshot_activation_manifest_hash"}
    )
    if manifest.get("snapshot_activation_manifest_hash") != expected_hash:
        errors.append("snapshot_activation_manifest_hash mismatch")
    return SnapshotActivationManifestValidation(
        passed=not errors,
        errors=errors,
        required_receipt_count=len(REQUIRED_RECEIPT_KINDS),
        provided_receipt_count=int(manifest.get("provided_receipt_count") or 0),
        missing_receipt_count=len(missing),
        activation_allowed=manifest.get("activation_allowed") is True,
        snapshot_activation_manifest_hash=manifest.get("snapshot_activation_manifest_hash"),
    )


def write_snapshot_activation_manifest(out_root: Path, *, index_job_manifest_path: Path) -> dict[str, Any]:
    out_root.mkdir(parents=True, exist_ok=True)
    index_job_manifest = json.loads(index_job_manifest_path.read_text(encoding="utf-8"))
    manifest = build_snapshot_activation_manifest(index_job_manifest)
    validation = validate_snapshot_activation_manifest(manifest)
    (out_root / "snapshot_activation_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    (out_root / "snapshot_activation_manifest_report.json").write_text(
        json.dumps(validation.__dict__, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    return validation.__dict__


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-root", required=True, type=Path)
    parser.add_argument("--index-job-manifest", required=True, type=Path)
    args = parser.parse_args()
    result = write_snapshot_activation_manifest(args.out_root, index_job_manifest_path=args.index_job_manifest)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
