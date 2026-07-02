from __future__ import annotations

import json
from pathlib import Path


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_public_enterprise_registry_marks_first_pass_adapters() -> None:
    from zuno.evals.rag_eval.public_enterprise_datasets import get_dataset_definition

    techqa = get_dataset_definition("techqa_rag_eval")
    cfqa = get_dataset_definition("cfqa")
    enterprise = get_dataset_definition("enterprise_rag_bench")

    assert techqa["current_status"] == "adapter_ready"
    assert techqa["primary_metrics"][:3] == ["retrieval_recall_at_k", "context_precision_at_k", "mrr_at_k"]
    assert cfqa["current_status"] == "adapter_ready"
    assert "source_span_accuracy" in cfqa["primary_metrics"]
    assert enterprise["current_status"] == "selected_adapter_ready"
    assert enterprise["source_url"] == "https://github.com/onyx-dot-app/EnterpriseRAG-Bench"


def test_prepare_techqa_rag_eval_writes_corpus_manifest_and_zuno_dataset(tmp_path: Path) -> None:
    from zuno.evals.rag_eval.public_enterprise_datasets import prepare_public_enterprise_eval

    raw_path = tmp_path / "techqa.jsonl"
    raw_path.write_text(
        json.dumps(
            {
                "question": "How do I reset a failed enterprise search connector?",
                "answer": "Reset the connector lease, then replay the failed crawl job.",
                "is_impossible": False,
                "contexts": [
                    {
                        "title": "Enterprise Search Connector Recovery",
                        "text": "A failed connector can be recovered by resetting the connector lease and replaying the failed crawl job.",
                    }
                ],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    summary = prepare_public_enterprise_eval(
        dataset_id="techqa_rag_eval",
        raw_path=raw_path,
        output_dir=tmp_path / "prepared",
    )

    assert summary["dataset_id"] == "techqa_rag_eval"
    assert summary["case_count"] == 1
    assert summary["manifest"]["file_count"] == 1
    assert summary["external_documents_required"] is False

    dataset_rows = _read_jsonl(Path(summary["dataset_path"]))
    assert dataset_rows[0]["id"] == "techqa_rag_eval_0001"
    assert dataset_rows[0]["query"] == "How do I reset a failed enterprise search connector?"
    assert dataset_rows[0]["reference_answer"] == "Reset the connector lease, then replay the failed crawl job."
    assert dataset_rows[0]["required_citations"] is True
    assert dataset_rows[0]["is_unanswerable"] is False
    assert dataset_rows[0]["gold_evidence"][0]["file_contains"] == "techqa_rag_eval_0001.md"
    assert "connector lease" in dataset_rows[0]["gold_evidence"][0]["text_contains"]

    manifest = json.loads(Path(summary["manifest_path"]).read_text(encoding="utf-8"))
    prepared_file = Path(manifest["files"][0]["prepared_path"])
    assert prepared_file.exists()
    assert "Enterprise Search Connector Recovery" in prepared_file.read_text(encoding="utf-8")


def test_prepare_cfqa_keeps_page_grounding_without_faking_missing_pdfs(tmp_path: Path) -> None:
    from zuno.evals.rag_eval.public_enterprise_datasets import prepare_public_enterprise_eval

    raw_path = tmp_path / "cfqa.jsonl"
    raw_path.write_text(
        json.dumps(
            {
                "id": "cfqa_demo_001",
                "问题": "某科技公司 2023 年研发费用是多少？",
                "答案": "研发费用为 1.23 亿元。",
                "答案出自": [42],
                "公司": "某科技公司",
                "年份": "2023",
                "股票代码": "600000",
                "文档名": "600000_2023_annual_report.pdf",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    summary = prepare_public_enterprise_eval(
        dataset_id="cfqa",
        raw_path=raw_path,
        output_dir=tmp_path / "prepared",
    )

    assert summary["dataset_id"] == "cfqa"
    assert summary["external_documents_required"] is True
    assert summary["manifest"]["file_count"] == 0
    assert summary["manifest"]["blocked_reason"] == "cfqa_annual_report_pdf_required"

    dataset_rows = _read_jsonl(Path(summary["dataset_path"]))
    sample = dataset_rows[0]
    assert sample["id"] == "cfqa_demo_001"
    assert sample["query"] == "某科技公司 2023 年研发费用是多少？"
    assert sample["reference_answer"] == "研发费用为 1.23 亿元。"
    assert sample["gold_evidence"][0]["file_contains"] == "600000_2023_annual_report.pdf"
    assert sample["gold_evidence"][0]["page_number"] == 42
    assert sample["answer_type"] == "financial_pdf_page_grounded"


def test_prepare_enterprise_rag_bench_extracts_expected_docs_from_parquet(tmp_path: Path) -> None:
    import pyarrow as pa
    import pyarrow.parquet as pq

    from zuno.evals.rag_eval.public_enterprise_datasets import prepare_public_enterprise_eval

    raw_path = tmp_path / "questions.jsonl"
    raw_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "question_id": "qst_0001",
                        "question_type": "basic",
                        "source_types": ["github"],
                        "question": "What are the multipart upload limits?",
                        "expected_doc_ids": ["dsid_upload_limits"],
                        "gold_answer": "The default limits are 10 MiB per file and 50 MiB total per request.",
                        "answer_facts": [
                            "The default per file upload size limit is 10 MiB.",
                            "The default total request size limit is 50 MiB.",
                        ],
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "question_id": "qst_0002",
                        "question_type": "basic",
                        "source_types": ["linear"],
                        "question": "Which release owns the rollout checklist?",
                        "expected_doc_ids": ["dsid_rollout_checklist"],
                        "gold_answer": "The rollout checklist belongs to console-2026.04.",
                        "answer_facts": [
                            "The rollout checklist belongs to console-2026.04.",
                        ],
                    },
                    ensure_ascii=False,
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    docs_path = tmp_path / "documents.parquet"
    pq.write_table(
        pa.table(
            {
                "doc_id": ["dsid_upload_limits", "dsid_rollout_checklist", "dsid_unrelated"],
                "source_type": ["github", "linear", "slack"],
                "title": ["Multipart upload support", "Rollout checklist", "Noise"],
                "content": [
                    "The default per file upload size limit is 10 MiB. The default total request size limit is 50 MiB.",
                    "The rollout checklist belongs to console-2026.04.",
                    "This unrelated thread should not be copied into the prepared corpus.",
                ],
            }
        ),
        docs_path,
    )

    summary = prepare_public_enterprise_eval(
        dataset_id="enterprise_rag_bench",
        raw_path=raw_path,
        source_root=docs_path,
        output_dir=tmp_path / "prepared",
    )

    assert summary["dataset_id"] == "enterprise_rag_bench"
    assert summary["case_count"] == 2
    assert summary["manifest"]["file_count"] == 2
    assert summary["external_documents_required"] is False
    assert summary["manifest"]["skipped_case_count"] == 0

    dataset_rows = _read_jsonl(Path(summary["dataset_path"]))
    assert dataset_rows[0]["id"] == "qst_0001"
    assert dataset_rows[0]["question_type"] == "basic"
    assert dataset_rows[0]["answer_type"] == "enterprise_internal_qa"
    assert dataset_rows[0]["gold_evidence"][0]["file_contains"] == "dsid_upload_limits.md"
    assert dataset_rows[0]["gold_evidence"][0]["text_contains"] == "The default per file upload size limit is 10 MiB."
    assert dataset_rows[0]["required_citations"] is True

    manifest = json.loads(Path(summary["manifest_path"]).read_text(encoding="utf-8"))
    prepared_files = {item["file_name"]: Path(item["prepared_path"]) for item in manifest["files"]}
    assert set(prepared_files) == {"dsid_upload_limits.md", "dsid_rollout_checklist.md"}
    assert "Multipart upload support" in prepared_files["dsid_upload_limits.md"].read_text(encoding="utf-8")
