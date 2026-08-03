"""PHASE22 GAP-B4 snapshot activation runner (DeepSeek2 / CC-B).

Runs the canonical ``SnapshotActivationAdapter`` against the live
three-index visibility evidence collected by
``run_live_three_index_visibility.py``.

Snapshot activation is a Knowledge-owned gate and stays fail closed:

* The real ``knowledge_version_id`` must come from DeepSeek1's canonical
  ingestion runtime.  Until that dependency lands, this runner emits an
  authentic ``NOT_RUN_DEPENDENCY_BLOCKED`` activation receipt and keeps
  ``snapshot_id = null`` — it never invents a KnowledgeVersion.
* When the dependency is present, activation additionally requires all
  three index visibility receipts (authentic, visible, same
  tenant/workspace/knowledge_version/index_version scope) plus a frozen
  embedding config hash.

Usage:
    python tools/evals/zuno/synthetic_benchmark/run_snapshot_activation.py \
        --out-root docs/evidence/goal05-phase22-machine-attested-synthetic-regression/deepseek2-cc-b34c \
        --visibility-evidence <live_three_index_visibility_evidence.json>
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from zuno.knowledge.indexing import (  # noqa: E402
    REQUIRED_VISIBILITY_RECEIPT_KINDS,
    SnapshotActivationAdapter,
    validate_snapshot_activation_receipt,
)

from tools.evals.zuno.synthetic_benchmark.dataset_contract import sha256_json  # noqa: E402

DEFAULT_EVIDENCE_DIR = (
    REPO_ROOT
    / "docs"
    / "evidence"
    / "goal05-phase22-machine-attested-synthetic-regression"
    / "deepseek2-cc-b34c"
)
INDEX_JOB_MANIFEST_PATH = (
    REPO_ROOT
    / "docs"
    / "evidence"
    / "goal05-phase22-machine-attested-synthetic-regression"
    / "index_job_manifest.json"
)


def _load_visibility_evidence(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("evidence_kind") != "live_three_index_visibility":
        raise ValueError(f"not a live three-index visibility evidence file: {path}")
    if data.get("all_visibility_passed") is not True:
        raise ValueError("live visibility evidence reports failure; cannot activate")
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-root", type=Path, default=DEFAULT_EVIDENCE_DIR)
    parser.add_argument("--visibility-evidence", type=Path, default=DEFAULT_EVIDENCE_DIR / "live_three_index_visibility_evidence.json")
    parser.add_argument("--knowledge-version-id", default="", help="real KnowledgeVersion id from DeepSeek1 canonical ingestion")
    parser.add_argument("--dependency-pr", default="", help="DeepSeek1 PR number once it exists")
    parser.add_argument("--dependency-head-sha", default="", help="DeepSeek1 PR head sha once it exists")
    args = parser.parse_args()

    evidence = _load_visibility_evidence(args.visibility_evidence)
    scope = evidence["scope"]
    tenant_id = scope["tenant_id"]
    workspace_id = scope["workspace_id"]
    index_job_manifest = json.loads(INDEX_JOB_MANIFEST_PATH.read_text(encoding="utf-8"))
    index_job_manifest_hash = index_job_manifest["index_job_manifest_hash"]

    visibility_receipts = list(evidence["index_runtime"]["adapter_visibility_receipts"].values())
    embedding_attestation = evidence["embedding"]
    embedding_config_hash = embedding_attestation["config_hash"]

    knowledge_version_id = args.knowledge_version_id.strip()
    dependency_pr = args.dependency_pr.strip() or None
    dependency_head_sha = args.dependency_head_sha.strip() or None

    adapter = SnapshotActivationAdapter()
    result = adapter.activate(
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        knowledge_version_id=knowledge_version_id or None,
        index_job_manifest_hash=index_job_manifest_hash,
        visibility_receipts=visibility_receipts,
        embedding_config_hash=embedding_config_hash,
        dependency_pr=dependency_pr,
        dependency_head_sha=dependency_head_sha,
        observed_at=datetime.now(timezone.utc),
    )

    receipt = result.receipt
    assert receipt is not None
    validation_errors = validate_snapshot_activation_receipt(receipt)
    if validation_errors:
        print(f"ERROR: activation receipt invalid: {validation_errors}")
        return 1

    report: dict[str, Any] = {
        "schema_version": "1.0.0",
        "track_id": "machine_attested_synthetic_regression",
        "evidence_kind": "snapshot_activation",
        "worker": "deepseek2-cc-b34c",
        "status": result.status,
        "activation_status": result.status,
        "snapshot_id": result.snapshot_id,
        "snapshot_content_hash": result.snapshot_content_hash,
        "block_reason": result.block_reason,
        "dependency": {
            "dependency_pr": result.dependency_pr,
            "dependency_head_sha": result.dependency_head_sha,
            "knowledge_version_id": knowledge_version_id or None,
        },
        "scope": {
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "index_job_manifest_hash": index_job_manifest_hash,
        },
        "required_receipt_kinds": list(REQUIRED_VISIBILITY_RECEIPT_KINDS),
        "provided_receipt_kinds": list(receipt.provided_receipt_kinds),
        "receipt_visibility": receipt.receipt_visibility,
        "consistency_checks": receipt.consistency_checks,
        "embedding_config_hash": embedding_config_hash,
        "embedding_attestation": embedding_attestation,
        "activation_receipt": receipt.model_dump(),
        "receipt_validation_passed": not validation_errors,
        "content_set_immutable": result.status == "ACTIVATED",
    }
    report["evidence_hash"] = sha256_json(report)

    args.out_root.mkdir(parents=True, exist_ok=True)
    (args.out_root / "snapshot_activation_evidence.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(
        {
            "activation_status": result.status,
            "snapshot_id": result.snapshot_id,
            "block_reason": result.block_reason,
            "knowledge_version_id": knowledge_version_id or None,
            "activation_receipt_ref": receipt.receipt_ref,
            "evidence_hash": report["evidence_hash"],
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
