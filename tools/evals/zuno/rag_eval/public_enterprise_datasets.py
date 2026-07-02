from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable

from zuno.evals.rag_eval.paths import default_corpus_root


ENTERPRISE_DOCUMENT_COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "doc_id": ("doc_id", "document_id", "dsid", "id", "source_id"),
    "content": ("content", "text", "body", "page_content", "document", "raw_text"),
    "title": ("title", "name", "subject", "doc_title"),
    "source_type": ("source_type", "source", "connector", "app", "datasource"),
}


class EnterpriseDocumentSchemaError(ValueError):
    """Raised when an EnterpriseRAG document source lacks required columns."""


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
        "current_status": "selected_adapter_ready",
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
        "notes": "Supports selected local parquet/document subsets; full 500K corpus remains an explicit external-scale target.",
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
    if path.suffix.lower() == ".parquet":
        try:
            import pyarrow.parquet as pq
        except ImportError as exc:  # pragma: no cover - depends on optional local env
            raise RuntimeError("pyarrow is required to read parquet public eval datasets") from exc
        table = pq.read_table(path)
        return [
            {column: table[column][index].as_py() for column in table.column_names}
            for index in range(table.num_rows)
        ]
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


def _resolve_enterprise_document_columns(columns: Iterable[str]) -> dict[str, str | None]:
    available = list(columns)
    available_set = set(available)
    resolved: dict[str, str | None] = {}
    for field, aliases in ENTERPRISE_DOCUMENT_COLUMN_ALIASES.items():
        resolved[field] = next((alias for alias in aliases if alias in available_set), None)
    return resolved


def _preview_value(value: Any, *, limit: int = 160) -> str:
    normalized = " ".join(str(value or "").split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: max(limit - 3, 0)].rstrip() + "..."


def _inspect_parquet_schema(path: Path, *, preview_chars: int = 160) -> dict[str, Any]:
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:  # pragma: no cover - depends on optional local env
        raise RuntimeError("pyarrow is required to inspect EnterpriseRAG-Bench parquet documents") from exc

    parquet_file = pq.ParquetFile(path)
    columns = list(parquet_file.schema_arrow.names)
    preview: dict[str, str] = {}
    if parquet_file.metadata.num_rows:
        try:
            batch = next(parquet_file.iter_batches(batch_size=1, columns=columns))
            payload = batch.to_pydict()
            preview = {
                column: _preview_value((payload.get(column) or [None])[0], limit=preview_chars)
                for column in columns
            }
        except StopIteration:
            preview = {}
    aliases = _resolve_enterprise_document_columns(columns)
    probe = {
        "path": str(path),
        "source_kind": "parquet",
        "row_count": parquet_file.metadata.num_rows,
        "columns": columns,
        "column_aliases": aliases,
        "first_row_preview": preview,
    }
    if not aliases.get("doc_id") or not aliases.get("content"):
        probe["blocked_reason"] = "document_schema_unsupported"
    return probe


def inspect_enterprise_document_schema(source_root: Path, *, preview_chars: int = 160) -> dict[str, Any]:
    if not source_root.exists():
        return {
            "path": str(source_root),
            "source_kind": "missing",
            "row_count": 0,
            "columns": [],
            "column_aliases": {field: None for field in ENTERPRISE_DOCUMENT_COLUMN_ALIASES},
            "first_row_preview": {},
            "blocked_reason": "enterprise_rag_bench_documents_required",
        }
    if source_root.is_file() and source_root.suffix.lower() == ".parquet":
        return _inspect_parquet_schema(source_root, preview_chars=preview_chars)
    if source_root.is_dir():
        first_parquet = next(iter(sorted(source_root.rglob("*.parquet"))), None)
        if first_parquet:
            probe = _inspect_parquet_schema(first_parquet, preview_chars=preview_chars)
            probe["directory"] = str(source_root)
            return probe
        files = [path for path in sorted(source_root.rglob("*")) if path.is_file()]
        return {
            "path": str(source_root),
            "source_kind": "directory_files",
            "row_count": len(files),
            "columns": [],
            "column_aliases": {
                "doc_id": "file_stem",
                "content": "file_text",
                "title": "file_stem",
                "source_type": "parent_directory",
            },
            "first_row_preview": {"path": str(files[0])} if files else {},
        }
    return {
        "path": str(source_root),
        "source_kind": "unsupported",
        "row_count": 0,
        "columns": [],
        "column_aliases": {field: None for field in ENTERPRISE_DOCUMENT_COLUMN_ALIASES},
        "first_row_preview": {},
        "blocked_reason": "document_schema_unsupported",
    }


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


def _as_string_list(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if item not in (None, "")]
    return [str(value)]


def _iter_parquet_document_rows(path: Path, *, doc_ids: set[str] | None = None) -> Iterable[dict[str, Any]]:
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:  # pragma: no cover - depends on optional local env
        raise RuntimeError("pyarrow is required to read EnterpriseRAG-Bench parquet documents") from exc

    remaining = set(doc_ids or [])
    parquet_file = pq.ParquetFile(path)
    resolved = _resolve_enterprise_document_columns(parquet_file.schema_arrow.names)
    if not resolved.get("doc_id") or not resolved.get("content"):
        raise EnterpriseDocumentSchemaError(f"document_schema_unsupported: {path}")
    columns = [column for column in resolved.values() if column]

    for batch in parquet_file.iter_batches(batch_size=4096, columns=columns):
        payload = batch.to_pydict()
        doc_id_values = payload.get(resolved["doc_id"]) or []
        for index, doc_id_value in enumerate(doc_id_values):
            doc_id = str(doc_id_value or "")
            if doc_ids is not None and doc_id not in remaining:
                continue
            row: dict[str, Any] = {"doc_id": doc_id}
            for target_field in ("source_type", "title", "content"):
                source_column = resolved.get(target_field)
                row[target_field] = (payload.get(source_column) or [None])[index] if source_column else None
            yield row
            if doc_ids is not None:
                remaining.discard(doc_id)
            if doc_ids is not None and not remaining:
                return


def _iter_file_document_rows(source_root: Path, *, doc_ids: set[str]) -> Iterable[dict[str, Any]]:
    for file_path in source_root.rglob("*"):
        if not file_path.is_file() or file_path.suffix.lower() in {".parquet", ".zip"}:
            continue
        doc_id = file_path.stem
        if doc_id not in doc_ids:
            continue
        yield {
            "doc_id": doc_id,
            "source_type": file_path.parent.name,
            "title": file_path.stem,
            "content": file_path.read_text(encoding="utf-8", errors="replace"),
        }


def _iter_enterprise_document_rows(source_root: Path, *, doc_ids: set[str] | None = None) -> Iterable[dict[str, Any]]:
    if source_root.is_file() and source_root.suffix.lower() == ".parquet":
        yield from _iter_parquet_document_rows(source_root, doc_ids=doc_ids)
        return
    if source_root.is_dir():
        parquet_paths = sorted(source_root.rglob("*.parquet"))
        if parquet_paths:
            if doc_ids is None:
                for parquet_path in parquet_paths:
                    yield from _iter_parquet_document_rows(parquet_path)
                return
            remaining = set(doc_ids or [])
            for parquet_path in parquet_paths:
                emitted = list(_iter_parquet_document_rows(parquet_path, doc_ids=remaining))
                for row in emitted:
                    yield row
                remaining -= {str(row.get("doc_id")) for row in emitted}
                if not remaining:
                    return
        remaining_for_files = set(doc_ids or [])
        if doc_ids is not None:
            for row in _iter_file_document_rows(source_root, doc_ids=remaining_for_files):
                yield row
        else:
            for file_path in sorted(source_root.rglob("*")):
                if not file_path.is_file() or file_path.suffix.lower() in {".parquet", ".zip"}:
                    continue
                yield {
                    "doc_id": file_path.stem,
                    "source_type": file_path.parent.name,
                    "title": file_path.stem,
                    "content": file_path.read_text(encoding="utf-8", errors="replace"),
                }
        return
    raise ValueError(f"unsupported EnterpriseRAG-Bench document source: {source_root}")


def _load_enterprise_documents(source_root: Path | None, *, doc_ids: set[str]) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    if not source_root:
        return {}, {
            "document_source_status": "missing_source_root",
            "missing_doc_ids": sorted(doc_ids),
        }
    if not source_root.exists():
        raise FileNotFoundError(f"EnterpriseRAG-Bench document source does not exist: {source_root}")

    rows: list[dict[str, Any]] = []
    scanned_paths: list[str] = []
    schema_probe = inspect_enterprise_document_schema(source_root)
    try:
        if source_root.is_file() and source_root.suffix.lower() == ".parquet":
            scanned_paths.append(str(source_root))
            rows.extend(_iter_parquet_document_rows(source_root, doc_ids=doc_ids))
        elif source_root.is_dir():
            scanned_paths.extend(str(path) for path in sorted(source_root.rglob("*.parquet")))
            scanned_paths.append(str(source_root))
            rows.extend(_iter_enterprise_document_rows(source_root, doc_ids=doc_ids))
        else:
            raise ValueError(f"unsupported EnterpriseRAG-Bench document source: {source_root}")
    except EnterpriseDocumentSchemaError:
        return {}, {
            "document_source_status": "document_schema_unsupported",
            "source_root": str(source_root),
            "scanned_paths": scanned_paths or [str(source_root)],
            "loaded_doc_count": 0,
            "missing_doc_ids": sorted(doc_ids),
            "blocked_reason": "document_schema_unsupported",
            "schema_probe": schema_probe,
        }

    documents = {str(row.get("doc_id")): row for row in rows if row.get("doc_id")}
    return documents, {
        "document_source_status": "loaded",
        "source_root": str(source_root),
        "scanned_paths": scanned_paths,
        "loaded_doc_count": len(documents),
        "missing_doc_ids": sorted(doc_ids - set(documents)),
        "schema_probe": schema_probe,
    }


def _write_enterprise_document_file(
    *,
    files_dir: Path,
    document: dict[str, Any],
) -> dict[str, Any]:
    doc_id = _safe_stem(str(document.get("doc_id") or ""), "enterprise_doc")
    source_type = str(document.get("source_type") or "unknown").strip() or "unknown"
    title = str(document.get("title") or doc_id).strip() or doc_id
    content = str(document.get("content") or "").strip()
    file_name = f"{doc_id}.md"
    prepared_path = files_dir / file_name
    prepared_path.write_text(
        "\n".join(
            [
                f"# {title}",
                "",
                f"Document ID: {doc_id}",
                f"Source Type: {source_type}",
                "",
                content,
            ]
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    return {
        "source_path": str(document.get("doc_id") or doc_id),
        "relative_source_path": file_name,
        "prepared_path": str(prepared_path),
        "file_name": file_name,
        "size_bytes": prepared_path.stat().st_size,
        "doc_id": doc_id,
        "source_type": source_type,
    }


def _prepare_enterprise_rag_bench(
    *,
    rows: list[dict[str, Any]],
    output_dir: Path,
    limit: int | None,
    source_root: Path | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    files_dir = output_dir / "files"
    files_dir.mkdir(parents=True, exist_ok=True)
    selected_rows = rows[:limit] if limit else rows
    expected_doc_ids = {
        doc_id
        for row in selected_rows
        for doc_id in _as_string_list(row.get("expected_doc_ids"))
    }
    documents_by_id, document_probe = _load_enterprise_documents(source_root, doc_ids=expected_doc_ids)
    manifest_files_by_name: dict[str, dict[str, Any]] = {}
    cases: list[dict[str, Any]] = []
    skipped_case_count = 0

    for index, row in enumerate(selected_rows, start=1):
        sample_id = _safe_stem(str(row.get("question_id") or row.get("id") or f"enterprise_rag_bench_{index:04d}"), f"enterprise_rag_bench_{index:04d}")
        doc_ids = _as_string_list(row.get("expected_doc_ids"))
        available_docs = [documents_by_id[doc_id] for doc_id in doc_ids if doc_id in documents_by_id]
        if doc_ids and len(available_docs) != len(doc_ids):
            skipped_case_count += 1
            continue

        gold_evidence: list[dict[str, Any]] = []
        answer_facts = _as_string_list(row.get("answer_facts"))
        for doc_index, document in enumerate(available_docs):
            manifest_item = _write_enterprise_document_file(files_dir=files_dir, document=document)
            manifest_files_by_name[manifest_item["file_name"]] = manifest_item
            snippet = answer_facts[min(doc_index, len(answer_facts) - 1)] if answer_facts else _evidence_snippet(document.get("content") or "")
            gold_evidence.append(
                {
                    "file_contains": manifest_item["file_name"],
                    "text_contains": _evidence_snippet(snippet),
                    "doc_id": manifest_item["doc_id"],
                    "source_type": manifest_item["source_type"],
                }
            )

        cases.append(
            {
                "id": sample_id,
                "dataset": "enterprise_rag_bench",
                "query": str(_first_nonempty(row, ("question", "query", "prompt")) or "").strip(),
                "reference_answer": str(_first_nonempty(row, ("gold_answer", "answer", "reference_answer")) or "").strip(),
                "gold_evidence": gold_evidence,
                "required_citations": bool(gold_evidence),
                "is_unanswerable": not bool(gold_evidence),
                "answer_type": "enterprise_internal_qa" if gold_evidence else "enterprise_no_ground_truth",
                "question_type": str(row.get("question_type") or "enterprise").strip() or "enterprise",
                "metadata": {
                    "source_types": _as_string_list(row.get("source_types")),
                    "expected_doc_ids": doc_ids,
                    "answer_facts": answer_facts,
                },
            }
        )

    manifest_files = list(manifest_files_by_name.values())
    blocked_reason = document_probe.get("blocked_reason")
    manifest = {
        "source": "EnterpriseRAG-Bench",
        "output_dir": str(output_dir),
        "file_count": len(manifest_files),
        "external_documents_required": bool(expected_doc_ids and (blocked_reason or not documents_by_id)),
        "blocked_reason": blocked_reason or ("enterprise_rag_bench_documents_required" if expected_doc_ids and not documents_by_id else None),
        "files": manifest_files,
        "selected_question_count": len(selected_rows),
        "skipped_case_count": skipped_case_count,
        **document_probe,
    }
    return cases, manifest


def prepare_public_enterprise_eval(
    *,
    dataset_id: str,
    raw_path: Path,
    output_dir: Path,
    source_root: Path | None = None,
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
    elif normalized == "enterprise_rag_bench":
        cases, manifest = _prepare_enterprise_rag_bench(
            rows=rows,
            output_dir=output_dir,
            limit=limit,
            source_root=source_root,
        )
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
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    output_dir = args.output_dir or default_corpus_root() / "public_enterprise_v1" / args.dataset
    summary = prepare_public_enterprise_eval(
        dataset_id=args.dataset,
        raw_path=args.raw,
        output_dir=output_dir,
        source_root=args.source_root,
        limit=args.limit,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
