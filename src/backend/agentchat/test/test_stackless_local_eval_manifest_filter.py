from __future__ import annotations

import json
import tempfile
from pathlib import Path

from agentchat.evals.rag_eval.run_stackless_local_eval import _filter_manifest_by_dataset


def test_filter_manifest_by_dataset_keeps_variant_files() -> None:
    manifest = {
        "files": [
            {"file_name": "contract_001_master_service_agreement.md"},
            {"file_name": "contract_001_master_service_agreement__variant_1.md"},
            {"file_name": "contract_002_saas_subscription.md"},
        ]
    }
    workspace_tmp = Path(tempfile.mkdtemp(prefix="zuno-manifest-filter-", dir=Path.cwd()))
    dataset_path = workspace_tmp / "dataset.jsonl"
    try:
        dataset_path.write_text(
            json.dumps(
                {
                    "gold_evidence": [
                        {"file_contains": "contract_001_master_service_agreement.md"},
                    ]
                },
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

        filtered = _filter_manifest_by_dataset(manifest, dataset_path)

        kept_files = [item["file_name"] for item in filtered["files"]]
        assert "contract_001_master_service_agreement.md" in kept_files
        assert "contract_001_master_service_agreement__variant_1.md" in kept_files
        assert "contract_002_saas_subscription.md" not in kept_files
    finally:
        if dataset_path.exists():
            dataset_path.unlink()
        workspace_tmp.rmdir()
