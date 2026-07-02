from __future__ import annotations

import argparse
import asyncio
import json
import math
import shutil
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any, Iterable

from zuno.evals.rag_eval.paths import default_runs_root
from zuno.evals.rag_eval.public_enterprise_datasets import (
    _as_string_list,
    _read_rows,
    _safe_stem,
    _write_jsonl,
    prepare_public_enterprise_eval,
)
from zuno.evals.rag_eval.run_stackless_local_eval import run_stackless_local_eval


PROFILE_ALIASES = {
    "standard_rag": "baseline_rag",
    "local_graphrag": "local_graphrag",
    "deep_graphrag": "deep_graphrag",
}
METRIC_KEYS = [
    "retrieval_recall_at_k",
    "context_precision_at_k",
    "mrr_at_k",
    "ndcg_at_k",
    "answer_correctness",
    "citation_accuracy",
    "source_span_accuracy",
    "unsupported_claim_rate",
]


def _select_rows(
    rows: list[dict[str, Any]],
    *,
    sample_size: int | None,
    stratify_by_question_type: bool,
) -> list[dict[str, Any]]:
    if not sample_size or sample_size <= 0 or sample_size >= len(rows):
        return list(rows)
    if not stratify_by_question_type:
        return list(rows[:sample_size])

    groups: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
    for row in rows:
        question_type = str(row.get("question_type") or "unknown")
        groups.setdefault(question_type, []).append(row)

    selected: list[dict[str, Any]] = []
    while len(selected) < sample_size and any(groups.values()):
        for group_rows in groups.values():
            if not group_rows:
                continue
            selected.append(group_rows.pop(0))
            if len(selected) >= sample_size:
                break
    return selected


def _expected_doc_ids(rows: Iterable[dict[str, Any]]) -> set[str]:
    return {
        doc_id
        for row in rows
        for doc_id in _as_string_list(row.get("expected_doc_ids"))
        if doc_id
    }


def _iter_source_documents(source_root: Path) -> Iterable[dict[str, Any]]:
    if source_root.is_file() and source_root.suffix.lower() == ".parquet":
        yield from _iter_parquet_documents(source_root)
        return
    if source_root.is_dir():
        for parquet_path in sorted(source_root.rglob("*.parquet")):
            yield from _iter_parquet_documents(parquet_path)
        for file_path in sorted(source_root.rglob("*")):
            if not file_path.is_file() or file_path.suffix.lower() in {".parquet", ".zip"}:
                continue
            yield {
                "doc_id": file_path.stem,
                "source_type": file_path.parent.name,
                "title": file_path.stem,
                "content": file_path.read_text(encoding="utf-8", errors="replace"),
            }


def _iter_parquet_documents(path: Path) -> Iterable[dict[str, Any]]:
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:  # pragma: no cover - depends on optional local env
        raise RuntimeError("pyarrow is required to read EnterpriseRAG-Bench parquet documents") from exc

    parquet_file = pq.ParquetFile(path)
    available_columns = set(parquet_file.schema_arrow.names)
    columns = [column for column in ("doc_id", "source_type", "title", "content") if column in available_columns]
    if "doc_id" not in columns or "content" not in columns:
        return
    for batch in parquet_file.iter_batches(batch_size=4096, columns=columns):
        payload = batch.to_pydict()
        for index, doc_id in enumerate(payload.get("doc_id") or []):
            yield {column: (payload.get(column) or [None])[index] for column in columns} | {"doc_id": str(doc_id or "")}


def _write_document_markdown(files_dir: Path, document: dict[str, Any]) -> dict[str, Any]:
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
        "source_path": doc_id,
        "relative_source_path": file_name,
        "prepared_path": str(prepared_path),
        "file_name": file_name,
        "size_bytes": prepared_path.stat().st_size,
        "doc_id": doc_id,
        "source_type": source_type,
        "hard_negative": True,
    }


def _append_hard_negatives(
    *,
    manifest_path: Path,
    source_root: Path | None,
    excluded_doc_ids: set[str],
    hard_negative_count: int,
) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not source_root or hard_negative_count <= 0 or not source_root.exists():
        manifest["hard_negative_count"] = 0
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return manifest

    existing_doc_ids = {str(item.get("doc_id") or Path(str(item.get("file_name") or "")).stem) for item in manifest.get("files", [])}
    files_dir = manifest_path.parent / "files"
    files_dir.mkdir(parents=True, exist_ok=True)
    added = 0
    for document in _iter_source_documents(source_root):
        doc_id = str(document.get("doc_id") or "")
        if not doc_id or doc_id in excluded_doc_ids or doc_id in existing_doc_ids:
            continue
        manifest.setdefault("files", []).append(_write_document_markdown(files_dir, document))
        existing_doc_ids.add(doc_id)
        added += 1
        if added >= hard_negative_count:
            break
    manifest["hard_negative_count"] = added
    manifest["file_count"] = len(manifest.get("files", []))
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def _copy_artifacts(*, corpus_dir: Path, output_root: Path) -> None:
    for source_name, target_name in [
        ("enterprise_rag_bench_eval.jsonl", "cases.jsonl"),
        ("manifest.json", "corpus_manifest.json"),
    ]:
        source = corpus_dir / source_name
        if source.exists():
            shutil.copyfile(source, output_root / target_name)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(min(math.ceil(percentile * len(ordered)) - 1, len(ordered) - 1), 0)
    return ordered[index]


def _cost_latency(profile_dir: Path) -> dict[str, Any]:
    rows = _read_jsonl(profile_dir / "retrieval_results.jsonl")
    latencies = [
        float((row.get("metadata") or {}).get("latency_ms"))
        for row in rows
        if (row.get("metadata") or {}).get("latency_ms") is not None
    ]
    costs = [
        float((row.get("metadata") or {}).get("cost_usd"))
        for row in rows
        if (row.get("metadata") or {}).get("cost_usd") is not None
    ]
    graph_used = 0
    for row in rows:
        raw = row.get("raw_result") or {}
        contexts = list(row.get("contexts") or [])
        if "graph" in str(raw.get("final_mode") or raw.get("first_mode") or "").lower() or any(
            context.get("kind") == "graph_path" for context in contexts
        ):
            graph_used += 1
    return {
        "latency_p50_ms": _percentile(latencies, 0.50),
        "latency_p95_ms": _percentile(latencies, 0.95),
        "estimated_cost": sum(costs) if costs else None,
        "graph_used_rate": (graph_used / len(rows)) if rows else None,
    }


def _load_profile_metrics(run_root: Path, underlying_profile: str, report_profiles: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    metrics_path = run_root / underlying_profile / "metrics.json"
    if metrics_path.exists():
        payload = json.loads(metrics_path.read_text(encoding="utf-8"))
        return dict(payload.get("aggregate") or {}), list(payload.get("per_sample") or [])
    return dict(report_profiles.get(underlying_profile) or {}), []


def _build_profile_summary(*, run_root: Path, run_report: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, list[dict[str, Any]]]]:
    report_profiles = dict((run_report.get("report") or run_report).get("profiles") or {})
    profiles: dict[str, Any] = {}
    per_samples: dict[str, list[dict[str, Any]]] = {}
    cost_latency: dict[str, Any] = {}
    for public_name, underlying in PROFILE_ALIASES.items():
        aggregate, rows = _load_profile_metrics(run_root, underlying, report_profiles)
        per_samples[public_name] = rows
        latency = _cost_latency(run_root / underlying)
        cost_latency[public_name] = latency
        profiles[public_name] = {
            "measured": bool(aggregate),
            "metrics_source": "fixed_benchmark",
            "underlying_profile": underlying,
            "aggregate": aggregate,
            **latency,
        }
    profiles["agentic_graphrag"] = {
        "measured": False,
        "metrics_source": "not_measured",
        "blocked_reason": "agentic_runtime_runner_not_wired",
        "aggregate": {},
    }
    return profiles, cost_latency, per_samples


def _delta(left: dict[str, Any], right: dict[str, Any]) -> dict[str, float | None]:
    output: dict[str, float | None] = {}
    for key in METRIC_KEYS:
        left_value = left.get(key)
        right_value = right.get(key)
        output[key] = round(float(left_value) - float(right_value), 6) if left_value is not None and right_value is not None else None
    return output


def _build_failure_cases(per_samples: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for profile, rows in per_samples.items():
        for row in rows:
            tags: list[str] = []
            if float(row.get("retrieval_recall") or 0.0) <= 0:
                tags.append("retrieval_miss")
            if row.get("unsupported_claim_rate") is not None and float(row.get("unsupported_claim_rate") or 0.0) > 0:
                tags.append("unsupported_claim")
            if row.get("citation_accuracy") is not None and float(row.get("citation_accuracy") or 0.0) <= 0:
                tags.append("citation_missing")
            if tags:
                failures.append({"case_id": row.get("id"), "profile": profile, "tags": tags})
    return failures


def _write_failure_cases(path: Path, failures: list[dict[str, Any]]) -> None:
    lines = ["# EnterpriseRAG Failure Cases", ""]
    if not failures:
        lines.append("No tagged failures were found in the measured per-sample metrics.")
    for failure in failures:
        lines.append(f"- `{failure['case_id']}` / `{failure['profile']}`: {', '.join(failure['tags'])}")
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def _write_report(path: Path, metrics: dict[str, Any]) -> None:
    lines = [
        "# EnterpriseRAG Paired Benchmark",
        "",
        f"- status: `{metrics['status']}`",
        f"- measurement_status: `{metrics['measurement_status']}`",
        f"- selected_case_count: `{metrics['case_set']['selected_case_count']}`",
        f"- measured_case_count: `{metrics['case_set']['measured_case_count']}`",
        "",
        "| Profile | Measured | Recall@5 | MRR@5 | Answer Correctness | Citation Accuracy | Latency p95 ms | Cost |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for profile, payload in metrics.get("profiles", {}).items():
        aggregate = payload.get("aggregate") or {}
        lines.append(
            "| {profile} | {measured} | {recall} | {mrr} | {correctness} | {citation} | {latency} | {cost} |".format(
                profile=profile,
                measured=str(bool(payload.get("measured"))).lower(),
                recall=_fmt(aggregate.get("retrieval_recall_at_k")),
                mrr=_fmt(aggregate.get("mrr_at_k")),
                correctness=_fmt(aggregate.get("answer_correctness")),
                citation=_fmt(aggregate.get("citation_accuracy")),
                latency=_fmt(payload.get("latency_p95_ms")),
                cost=_fmt(payload.get("estimated_cost")),
            )
        )
    if metrics["measurement_status"] == "blocked_not_measured":
        lines.extend(
            [
                "",
                "## Blocked",
                "",
                f"- blocked_reason: `{metrics['corpus'].get('blocked_reason')}`",
                "- No benchmark metrics were measured because the EnterpriseRAG-Bench documents are missing.",
            ]
        )
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def _fmt(value: Any) -> str:
    if value is None:
        return "-"
    try:
        return f"{float(value):.4f}"
    except (TypeError, ValueError):
        return str(value)


def _blocked_metrics(*, selected_rows: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "blocked",
        "measurement_status": "blocked_not_measured",
        "metrics_source": "blocked_not_measured",
        "case_set": {
            "selected_case_count": len(selected_rows),
            "measured_case_count": 0,
            "common_case_ids": [],
            "question_type_counts": _question_type_counts(selected_rows),
        },
        "corpus": manifest,
        "profiles": {
            "standard_rag": {"measured": False, "metrics_source": "blocked_not_measured", "aggregate": {}},
            "deep_graphrag": {"measured": False, "metrics_source": "blocked_not_measured", "aggregate": {}},
            "agentic_graphrag": {"measured": False, "metrics_source": "blocked_not_measured", "aggregate": {}},
        },
        "deltas": {},
        "agentic_metrics": {"graph_usage_gain": None, "replan_success_rate": None, "cost_quality_ratio": None},
        "cost_latency": {},
    }


def _question_type_counts(rows: Iterable[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        key = str(row.get("question_type") or "unknown")
        counts[key] = counts.get(key, 0) + 1
    return counts


def _write_selected_questions(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _write_jsonl(path, rows)


async def run_enterprise_rag_paired_benchmark(
    *,
    questions_file: Path,
    output_root: Path,
    documents_file: Path | None = None,
    source_root: Path | None = None,
    sample_size: int = 80,
    stratify_by_question_type: bool = True,
    hard_negative_count: int = 0,
    allow_blocked: bool = True,
    run_profiles: bool = True,
    spawn_dev_embedding_server: bool = True,
    rerank_score_threshold_override: float | None = 0.0,
) -> dict[str, Any]:
    output_root.mkdir(parents=True, exist_ok=True)
    rows = _read_rows(questions_file)
    selected_rows = _select_rows(
        rows,
        sample_size=sample_size,
        stratify_by_question_type=stratify_by_question_type,
    )
    selected_questions = output_root / "selected_questions.jsonl"
    _write_selected_questions(selected_questions, selected_rows)

    document_source = documents_file or source_root
    corpus_dir = output_root / "corpus"
    prepared = prepare_public_enterprise_eval(
        dataset_id="enterprise_rag_bench",
        raw_path=selected_questions,
        source_root=document_source,
        output_dir=corpus_dir,
    )
    manifest_path = Path(prepared["manifest_path"])
    manifest = _append_hard_negatives(
        manifest_path=manifest_path,
        source_root=document_source,
        excluded_doc_ids=_expected_doc_ids(selected_rows),
        hard_negative_count=hard_negative_count,
    )
    _copy_artifacts(corpus_dir=corpus_dir, output_root=output_root)

    if prepared["external_documents_required"] or prepared["case_count"] == 0:
        if not allow_blocked:
            raise RuntimeError("EnterpriseRAG-Bench documents are required before running measured benchmark profiles")
        metrics = _blocked_metrics(selected_rows=selected_rows, manifest=manifest)
        (output_root / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
        _write_failure_cases(output_root / "failure_cases.md", [])
        _write_report(output_root / "report.md", metrics)
        return {"status": "blocked", "metrics_source": "blocked_not_measured", "output_root": str(output_root)}

    if not run_profiles:
        metrics = _blocked_metrics(selected_rows=selected_rows, manifest=manifest)
        metrics["status"] = "prepared"
        metrics["measurement_status"] = "prepared_not_measured"
        metrics["metrics_source"] = "prepared_not_measured"
        (output_root / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
        _write_failure_cases(output_root / "failure_cases.md", [])
        _write_report(output_root / "report.md", metrics)
        return {"status": "prepared", "metrics_source": "prepared_not_measured", "output_root": str(output_root)}

    dataset_path = Path(prepared["dataset_path"])
    stackless_root = output_root / "stackless_profiles"
    run_report = await run_stackless_local_eval(
        manifest_path=manifest_path,
        dataset_path=dataset_path,
        output_root=stackless_root,
        profile_set="deep_graphrag_compare",
        sample_limit=prepared["case_count"],
        spawn_dev_embedding_server=spawn_dev_embedding_server,
        rerank_score_threshold_override=rerank_score_threshold_override,
    )
    profiles, cost_latency, per_samples = _build_profile_summary(run_root=stackless_root, run_report=run_report)
    cases = _read_jsonl(dataset_path)
    common_case_ids = [str(row.get("id")) for row in cases]
    standard = profiles["standard_rag"].get("aggregate") or {}
    deep = profiles["deep_graphrag"].get("aggregate") or {}
    failures = _build_failure_cases(per_samples)
    metrics = {
        "status": "measured",
        "measurement_status": "fixed_benchmark",
        "metrics_source": "fixed_benchmark",
        "case_set": {
            "selected_case_count": len(selected_rows),
            "measured_case_count": len(cases),
            "common_case_ids": common_case_ids,
            "question_type_counts": _question_type_counts(cases),
        },
        "corpus": manifest,
        "profiles": profiles,
        "deltas": {
            "deep_vs_standard": _delta(deep, standard),
        },
        "agentic_metrics": {
            "graph_usage_gain": _delta(deep, standard).get("retrieval_recall_at_k"),
            "replan_success_rate": None,
            "cost_quality_ratio": None,
        },
        "cost_latency": cost_latency,
        "failure_count": len(failures),
    }
    (output_root / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_failure_cases(output_root / "failure_cases.md", failures)
    _write_report(output_root / "report.md", metrics)
    return {
        "status": "measured",
        "metrics_source": "fixed_benchmark",
        "output_root": str(output_root),
        "measured_case_count": len(cases),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run EnterpriseRAG-Bench selected-doc paired benchmark for Zuno.")
    parser.add_argument("--questions-file", required=True, type=Path)
    parser.add_argument("--documents-file", type=Path)
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--sample-size", type=int, default=80)
    parser.add_argument("--no-stratify-by-question-type", action="store_true")
    parser.add_argument("--hard-negative-count", type=int, default=20)
    parser.add_argument("--allow-blocked", action="store_true")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--no-spawn-dev-embedding-server", action="store_true")
    parser.add_argument("--rerank-score-threshold-override", type=float, default=0.0)
    args = parser.parse_args()

    output_root = args.output_root or default_runs_root() / f"enterprise-rag-paired-{time.strftime('%Y%m%d-%H%M%S')}"
    result = asyncio.run(
        run_enterprise_rag_paired_benchmark(
            questions_file=args.questions_file,
            documents_file=args.documents_file,
            source_root=args.source_root,
            output_root=output_root,
            sample_size=args.sample_size,
            stratify_by_question_type=not args.no_stratify_by_question_type,
            hard_negative_count=max(args.hard_negative_count, 0),
            allow_blocked=args.allow_blocked,
            run_profiles=not args.prepare_only,
            spawn_dev_embedding_server=not args.no_spawn_dev_embedding_server,
            rerank_score_threshold_override=args.rerank_score_threshold_override,
        )
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
