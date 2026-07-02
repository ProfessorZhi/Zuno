from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable

from zuno.evals.rag_eval.paths import default_corpus_root


DATASET_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "dataset_id": "techqa_rag_eval",
        "name": "TechQA-RAG-Eval",
        "current_status": "adapter_ready",
        "license": "Apache-2.0",
        "source_url": "https://huggingface.co/datasets/nvidia/TechQA-RAG-Eval",
        "best_for": ["technical_support", "is_impossible", "standard_vs_deep"],
        "primary_metrics": [
            "retrieval_recall_at_k",
            "context_precision_at_k",
            "mrr_at_k",
            "answer_correctness",
            "unsupported_claim_rate",
        ],
        "notes": "Small technical-support style RAG dataset; contexts can be converted into local Markdown corpus files.",
    },
    {
        "dataset_id": "cfqa",
        "name": "CFQA",
        "current_status": "adapter_ready",
        "license": "public-research-dataset",
        "source_url": "https://github.com/ydli-ai/CFQA",
        "best_for": ["chinese_financial_pdf", "page_grounding", "source_span_accuracy"],
        "primary_metrics": [
            "retrieval_recall_at_k",
            "context_precision_at_k",
            "answer_correctness",
            "citation_coverage",
            "source_span_accuracy",
        ],
        "notes": "CFQA rows can be normalized immediately, but annual-report PDFs must be downloaded separately; do not fake a corpus.",
    },
    {
        "dataset_id": "enterprise_rag_bench",
        "name": "EnterpriseRAG-Bench",
        "current_status": "registry_only",
        "license": "MIT",
        "source_url": "https://github.com/onyx-dot-app/EnterpriseRAG-Bench",
        "best_for": ["enterprise_corpus", "multi_source", "conflicting_information", "no_answer"],
        "primary_metrics": [
            "retrieval_recall_at_k",
            "context_precision_at_k",
            "mrr_at_k",
            "ndcg_at_k",
            "answer_correctness",
        ],
        "notes": "Keep as registry/runbook in V1; full corpus scale is too large for the first adapter pass.",
    },
    {
        "dataset_id": "open_rag_benchmark",
        "name": "Open RAG Benchmark",
        "current_status": "registry_only",
        "license": "dataset-specific",
        "source_url": "https://huggingface.co/datasets/open-rag-benchmark/open-rag-benchmark",
        "best_for": ["pdf", "section_qrels", "table_image_text"],
        "primary_metrics": [
            "retrieval_recall_at_k",
            "context_precision_at_k",
            "mrr_at_k",
            "ndcg_at_k",
            "source_span_accuracy",
        ],
        "notes": "Needs a qrels/corpus adapter in a later pass.",
    },
)


def list_dataset_definitions() -> list[dict[str, Any]]:
    return [dict(item) for item in DATASET_DEFINITIONS]


def get_dataset_definition(dataset_id: str) -> dict[str, Any]:
    normalized = _normalize_dataset_id(dataset_id)
    for item in DATASET_DEFINITIONS:
        if item["dataset_id"] == normalized:
            return dict(item)
    raise ValueError(f"unsupported public enterprise dataset: {dataset_id}")


def _normalize_dataset_id(dataset_id: str) -> str:
    normalized = str(dataset_id or "").strip().lower().replace("-", "_")
    aliases = {
        "techqa": "techqa_rag_eval",
        "techqa_rag": "techqa_rag_eval",
        "enterprise_rag": "enterprise_rag_bench",
        "enterpriserag_bench": "enterprise_rag_bench",
        "openrag_benchmark": "open_rag_benchmark",
    }
    return aliases.get(normalized, normalized)


def _read_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"raw dataset path does not exist: {path}")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    payload = json.loads(text)
    if isinstance(payload, list):
        return [dict(item) for item in payload]
    if isinstance(payload, dict):
        for key in ("data", "rows", "examples", "questions"):
            if isinstance(payload.get(key), list):
                return [dict(item) for item in payload[key]]
        return [payload]
    raise ValueError(f"unsupported dataset payload shape: {path}")


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def _safe_stem(value: str, fallback: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value or "").strip()).strip("._")
    return cleaned or fallback


def _first_nonempty(row: dict[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return None


def _context_to_markdown(context: Any, *, index: int) -> tuple[str, str]:
    if isinstance(context, str):
        return f"Context {index}", context.strip()
    if not isinstance(context, dict):
        return f"Context {index}", str(context).strip()
    title = str(
        _first_nonempty(context, ("title", "source", "doc_title", "document_title", "id"))
        or f"Context {index}"
    )
    text = str(
        _first_nonempty(context, ("text", "content", "body", "passage", "context"))
        or ""
    ).strip()
    return title, text


def _evidence_snippet(text: str) -> str:
    normalized = " ".join(str(text or "").split())
    return normalized[:160] if len(normalized) > 160 else normalized


def _prepare_techqa(
    *,
    rows: list[dict[str, Any]],
    output_dir: Path,
    limit: int | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    files_dir = output_dir / "files"
    files_dir.mkdir(parents=True, exist_ok=True)
    cases: list[dict[str, Any]] = []
    manifest_files: list[dict[str, Any]] = []
    selected_rows = rows[:limit] if limit else rows

    for index, row in enumerate(selected_rows, start=1):
        sample_id = _safe_stem(str(row.get("id") or row.get("_id") or f"techqa_rag_eval_{index:04d}"), f"techqa_rag_eval_{index:04d}")
        if not sample_id.startswith("techqa_rag_eval_"):
            sample_id = f"techqa_rag_eval_{index:04d}"
        query = str(_first_nonempty(row, ("question", "query", "prompt")) or "").strip()
        answer = str(_first_nonempty(row, ("answer", "reference_answer", "accepted_answer")) or "").strip()
        is_unanswerable = bool(row.get("is_impossible") or row.get("unanswerable"))
        contexts = row.get("contexts") or row.get("context") or []
        if isinstance(contexts, dict) or isinstance(contexts, str):
            contexts = [contexts]

        context_blocks: list[tuple[str, str]] = []
        for context_index, context in enumerate(contexts, start=1):
            title, text = _context_to_markdown(context, index=context_index)
            if text:
                context_blocks.append((title, text))

        file_name = f"{sample_id}.md"
        gold_evidence: list[dict[str, Any]] = []
        if context_blocks:
            content = [
                f"# {query or sample_id}",
                "",
                f"Reference answer: {answer or 'NO_RELEVANT_EVIDENCE_FOUND'}",
            ]
            for title, text in context_blocks:
                content.extend(["", f"## {title}", "", text])
                if not is_unanswerable:
                    gold_evidence.append(
                        {
                            "file_contains": file_name,
                            "text_contains": _evidence_snippet(text),
                        }
                    )
            prepared_path = files_dir / file_name
            prepared_path.write_text("\n".join(content).strip() + "\n", encoding="utf-8")
            manifest_files.append(
                {
                    "source_path": "techqa_rag_eval_contexts",
                    "relative_source_path": file_name,
                    "prepared_path": str(prepared_path),
                    "file_name": file_name,
                    "size_bytes": prepared_path.stat().st_size,
                }
            )

        cases.append(
            {
                "id": sample_id,
                "dataset": "techqa_rag_eval",
                "query": query,
                "reference_answer": answer if answer else "NO_RELEVANT_EVIDENCE_FOUND",
                "gold_evidence": gold_evidence,
                "required_citations": bool(gold_evidence),
                "is_unanswerable": is_unanswerable,
                "answer_type": "unanswerable" if is_unanswerable else "technical_support",
                "question_type": "technical_support",
            }
        )

    manifest = {
        "source": "TechQA-RAG-Eval",
        "output_dir": str(output_dir),
        "file_count": len(manifest_files),
        "external_documents_required": False,
        "files": manifest_files,
    }
    return cases, manifest


def _parse_pages(value: Any) -> list[int]:
    if value in (None, ""):
        return []
    if isinstance(value, int):
        return [value]
    if isinstance(value, list):
        pages: list[int] = []
        for item in value:
            pages.extend(_parse_pages(item))
        return pages
    pages = []
    for token in re.split(r"[,，;\s]+", str(value)):
        if not token:
            continue
        try:
            pages.append(int(token))
        except ValueError:
            continue
    return pages


def _prepare_cfqa(
    *,
    rows: list[dict[str, Any]],
    output_dir: Path,
    limit: int | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    selected_rows = rows[:limit] if limit else rows
    for index, row in enumerate(selected_rows, start=1):
        sample_id = str(row.get("id") or row.get("qid") or f"cfqa_{index:04d}").strip()
        query = str(_first_nonempty(row, ("问题", "question", "query")) or "").strip()
        answer = str(_first_nonempty(row, ("答案", "answer", "reference_answer")) or "").strip()
        company = str(_first_nonempty(row, ("公司", "company", "company_name")) or "").strip()
        year = str(_first_nonempty(row, ("年份", "year", "report_year")) or "").strip()
        stock = str(_first_nonempty(row, ("股票代码", "stock_code", "ticker")) or "").strip()
        document_name = str(
            _first_nonempty(row, ("文档名", "document_name", "pdf_name", "file_name"))
            or f"{stock}_{year}_annual_report.pdf"
        ).strip()
        pages = _parse_pages(_first_nonempty(row, ("答案出自", "source_pages", "pages", "page_number")))
        first_page = pages[0] if pages else None
        evidence: dict[str, Any] = {
            "file_contains": document_name,
            "text_contains": _evidence_snippet(answer),
        }
        if first_page is not None:
            evidence["page_number"] = first_page
            evidence["source_span"] = f"{document_name}#page={first_page}"
        if company:
            evidence["company"] = company
        if year:
            evidence["year"] = year

        cases.append(
            {
                "id": sample_id,
                "dataset": "cfqa",
                "query": query,
                "reference_answer": answer,
                "gold_evidence": [evidence],
                "required_citations": True,
                "is_unanswerable": False,
                "answer_type": "financial_pdf_page_grounded",
                "question_type": "financial_qa",
                "metadata": {
                    "company": company,
                    "year": year,
                    "stock_code": stock,
                    "document_name": document_name,
                    "source_pages": pages,
                },
            }
        )

    manifest = {
        "source": "CFQA",
        "output_dir": str(output_dir),
        "file_count": 0,
        "external_documents_required": True,
        "blocked_reason": "cfqa_annual_report_pdf_required",
        "files": [],
    }
    return cases, manifest


def prepare_public_enterprise_eval(
    *,
    dataset_id: str,
    raw_path: Path,
    output_dir: Path,
    limit: int | None = None,
) -> dict[str, Any]:
    normalized = _normalize_dataset_id(dataset_id)
    definition = get_dataset_definition(normalized)
    rows = _read_rows(raw_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    if normalized == "techqa_rag_eval":
        cases, manifest = _prepare_techqa(rows=rows, output_dir=output_dir, limit=limit)
    elif normalized == "cfqa":
        cases, manifest = _prepare_cfqa(rows=rows, output_dir=output_dir, limit=limit)
    else:
        raise ValueError(f"{normalized} is {definition['current_status']}; no adapter is implemented yet")

    dataset_path = output_dir / f"{normalized}_eval.jsonl"
    manifest_path = output_dir / "manifest.json"
    _write_jsonl(dataset_path, cases)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "dataset_id": normalized,
        "definition": definition,
        "case_count": len(cases),
        "dataset_path": str(dataset_path),
        "manifest_path": str(manifest_path),
        "manifest": manifest,
        "external_documents_required": bool(manifest.get("external_documents_required")),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare public enterprise-style RAG eval datasets for Zuno.")
    parser.add_argument("--dataset", required=True, choices=[item["dataset_id"] for item in DATASET_DEFINITIONS])
    parser.add_argument("--raw", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    output_dir = args.output_dir or default_corpus_root() / "public_enterprise_v1" / args.dataset
    summary = prepare_public_enterprise_eval(
        dataset_id=args.dataset,
        raw_path=args.raw,
        output_dir=output_dir,
        limit=args.limit,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
