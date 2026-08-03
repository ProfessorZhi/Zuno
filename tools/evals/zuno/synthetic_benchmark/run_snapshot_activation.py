"""PHASE22 GAP-B4 snapshot activation runner (DeepSeek2 / CC-B hardening).

Runs the hardened ``SnapshotActivationAdapter`` against the corpus-level
index build receipts collected by ``run_live_three_index_visibility.py``.

Truth boundary: while DeepSeek1's canonical ingestion has not delivered a
real ``knowledge_version_id`` (PR #112 REQUEST_WORKER_CHANGES), this
runner emits an authentic ``NOT_RUN_DEPENDENCY_BLOCKED`` activation receipt
and keeps ``snapshot_id = null``.  Adapter-live-smoke corpus receipts can
never activate a snapshot (they are not ``formal``, not owner-produced and
not snapshot-eligible).  No KnowledgeVersion or Snapshot is ever invented.

Usage:
    python tools/evals/zuno/synthetic_benchmark/run_snapshot_activation.py \
        --out-root docs/evidence/goal05-phase22-machine-attested-synthetic-regression/deepseek2-cc-b34c \
        --visibility-evidence <live_three_index_visibility_evidence.json> \
        [--knowledge-version-id <kv> --dependency-pr 112 --dependency-head-sha <sha>]
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
    REQUIRED_CORPUS_RECEIPT_KINDS,
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
    if data.get("evidence_kind") != "three_index_adapter_live_smoke":
        raise ValueError(f"not a three-index adapter live smoke evidence file: {path}")
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-root", type=Path, default=DEFAULT_EVIDENCE_DIR)
    parser.add_argument("--visibility-evidence", type=Path, default=DEFAULT_EVIDENCE_DIR / "live_three_index_visibility_evidence.json")
    parser.add_argument("--knowledge-version-id", default="")
    parser.add_argument("--dependency-pr", default="112")
    parser.add_argument("--dependency-head-sha", default="ce495af2a39c01379878a9e2c1bb58d876456b1e")
    args = parser.parse_args()

    evidence = _load_visibility_evidence(args.visibility_evidence)
    scope = evidence["scope"]
    tenant_id = scope["tenant_id"]
    workspace_id = scope["workspace_id"]
    index_job_manifest = json.loads(INDEX_JOB_MANIFEST_PATH.read_text(encoding="utf-8"))
    index_job_manifest_hash = index_job_manifest["index_job_manifest_hash"]

    corpus_receipts = list(evidence["corpus_index_build_receipts"].values())
    embedding_config = evidence["embedding"]
    knowledge_version_id = args.knowledge_version_id.strip()
    dependency_pr = args.dependency_pr.strip() or None
    dependency_head_sha = args.dependency_head_sha.strip() or None

    adapter = SnapshotActivationAdapter()
    result = adapter.activate(
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        knowledge_version_id=knowledge_version_id or None,
        index_job_manifest_hash=index_job_manifest_hash,
        corpus_receipts=corpus_receipts,
        neo4j_path_receipt=None,
        embedding_config=embedding_config,
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
            "dependency_accepted": False,
            "knowledge_version_id": knowledge_version_id or None,
        },
        "scope": {
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "index_job_manifest_hash": index_job_manifest_hash,
        },
        "required_corpus_receipt_kinds": list(REQUIRED_CORPUS_RECEIPT_KINDS),
        "provided_corpus_receipt_kinds": list(receipt.provided_corpus_receipt_kinds),
        "corpus_receipt_refs": receipt.corpus_receipt_refs,
        "receipt_visibility": receipt.receipt_visibility,
        "consistency_checks": receipt.consistency_checks,
        "embedding_config_hash": embedding_config["config_hash"],
        "activation_receipt": receipt.model_dump(),
        "receipt_validation_passed": not validation_errors,
        "content_set_immutable": result.status == "ACTIVATED",
        "snapshot_persistence": result.activation_evidence.get("persistence"),
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
            "dependency_accepted": False,
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
