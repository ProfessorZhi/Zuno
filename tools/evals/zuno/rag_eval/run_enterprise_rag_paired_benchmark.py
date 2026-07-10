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
from zuno.evals.rag_eval.metrics import _is_context_relevant
from zuno.evals.rag_eval.public_enterprise_datasets import (
    EnterpriseDocumentSchemaError,
    _as_string_list,
    _iter_enterprise_document_rows,
    _read_rows,
    _safe_stem,
    _write_jsonl,
    inspect_enterprise_document_schema,
    prepare_public_enterprise_eval,
)
from zuno.evals.rag_eval.run_stackless_local_eval import run_stackless_local_eval


PROFILE_ALIASES = {
    "standard_rag": "baseline_rag",
    "local_graphrag": "local_graphrag",
    "deep_graphrag": "deep_graphrag",
    "agentic_graphrag": "agentic_graphrag",
}
METRIC_KEYS = [
    "retrieval_recall_at_k",
    "context_precision_at_k",
    "mrr_at_k",
    "ndcg_at_k",
    "answer_correctness",
    "citation_accuracy",
    "source_doc_citation_accuracy",
    "evidence_text_available_at_k",
    "source_span_accuracy",
    "unsupported_claim_rate",
]

ENTERPRISE_RAG_DEFAULT_CHUNK_SIZE = 1800
ENTERPRISE_RAG_DEFAULT_OVERLAP = 240
PER_SAMPLE_METRIC_MAP = {
    "retrieval_recall": "retrieval_recall_at_k",
    "context_precision": "context_precision_at_k",
    "mrr": "mrr_at_k",
    "ndcg": "ndcg_at_k",
    "answer_correctness": "answer_correctness",
    "citation_accuracy": "citation_accuracy",
    "source_doc_citation_accuracy": "source_doc_citation_accuracy",
    "evidence_text_available": "evidence_text_available_at_k",
    "source_span_accuracy": "source_span_accuracy",
    "unsupported_claim_rate": "unsupported_claim_rate",
}
ADVANCED_FAILURE_TAGS = [
    "gold_doc_not_indexed",
    "gold_doc_recalled_but_low_rank",
    "graph_context_non_gold",
    "rerank_demoted_gold",
    "no_answer_should_refuse",
    "too_expensive_for_gain",
]
FAILURE_BUCKETS = [
    "doc_miss",
    "doc_hit_text_miss",
    "text_hit_citation_miss",
    "citation_hit_answer_wrong",
]
UNAVAILABLE_BUCKET_REASON = "unavailable_due_to_missing_trace_fields"


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
    yield from _iter_enterprise_document_rows(source_root)


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
    if manifest.get("blocked_reason") == "document_schema_unsupported":
        manifest["hard_negative_count"] = 0
        manifest["file_count"] = len(manifest.get("files", []))
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return manifest
    if not source_root or hard_negative_count <= 0 or not source_root.exists():
        manifest["hard_negative_count"] = 0
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return manifest

    existing_doc_ids = {str(item.get("doc_id") or Path(str(item.get("file_name") or "")).stem) for item in manifest.get("files", [])}
    files_dir = manifest_path.parent / "files"
    files_dir.mkdir(parents=True, exist_ok=True)
    added = 0
    try:
        documents = _iter_source_documents(source_root)
        for document in documents:
            doc_id = str(document.get("doc_id") or "")
            if not doc_id or doc_id in excluded_doc_ids or doc_id in existing_doc_ids:
                continue
            manifest.setdefault("files", []).append(_write_document_markdown(files_dir, document))
            existing_doc_ids.add(doc_id)
            added += 1
            if added >= hard_negative_count:
                break
    except EnterpriseDocumentSchemaError:
        manifest["blocked_reason"] = "document_schema_unsupported"
        manifest["document_source_status"] = "document_schema_unsupported"
        manifest["hard_negative_count"] = 0
        manifest["file_count"] = len(manifest.get("files", []))
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return manifest
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


def _cost_latency_from_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
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


def _cost_latency(profile_dir: Path) -> dict[str, Any]:
    return _cost_latency_from_rows(_read_jsonl(profile_dir / "retrieval_results.jsonl"))


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
        if public_name == "agentic_graphrag" and not aggregate:
            profiles[public_name]["metrics_source"] = "not_measured"
            profiles[public_name]["blocked_reason"] = "agentic_runtime_runner_not_wired"
    return profiles, cost_latency, per_samples


def _replan_success_rate(
    *,
    run_root: Path,
    agentic_underlying_profile: str,
    standard_rows: list[dict[str, Any]],
    agentic_rows: list[dict[str, Any]],
) -> float | None:
    retrieval_rows = _read_jsonl(run_root / agentic_underlying_profile / "retrieval_results.jsonl")
    if not retrieval_rows:
        return None

    standard_by_id = {str(row.get("id")): row for row in standard_rows}
    agentic_by_id = {str(row.get("id")): row for row in agentic_rows}
    attempts = 0
    successes = 0
    for retrieval_row in retrieval_rows:
        raw = dict(retrieval_row.get("raw_result") or {})
        try:
            round_count = int(raw.get("round_count") or 1)
        except (TypeError, ValueError):
            round_count = 1
        attempted = round_count > 1 or raw.get("replan_success") is not None or raw.get("fallback_reason")
        if not attempted:
            continue
        attempts += 1
        case_id = str(retrieval_row.get("id") or "")
        standard_recall = float((standard_by_id.get(case_id) or {}).get("retrieval_recall") or 0.0)
        agentic_recall = float((agentic_by_id.get(case_id) or {}).get("retrieval_recall") or 0.0)
        if raw.get("replan_success") is True or agentic_recall > standard_recall:
            successes += 1
    if attempts == 0:
        return None
    return round(successes / attempts, 6)


def _cost_quality_ratio(
    *,
    quality_delta: float | None,
    standard_latency: dict[str, Any],
    agentic_latency: dict[str, Any],
) -> float | None:
    if quality_delta is None:
        return None
    standard_cost = standard_latency.get("estimated_cost")
    agentic_cost = agentic_latency.get("estimated_cost")
    if standard_cost is None or agentic_cost is None:
        return None
    cost_delta = float(agentic_cost) - float(standard_cost)
    if cost_delta <= 0:
        return None
    return round(float(quality_delta) / cost_delta, 6)


def _delta(left: dict[str, Any], right: dict[str, Any]) -> dict[str, float | None]:
    output: dict[str, float | None] = {}
    for key in METRIC_KEYS:
        left_value = left.get(key)
        right_value = right.get(key)
        output[key] = round(float(left_value) - float(right_value), 6) if left_value is not None and right_value is not None else None
    return output


def _mean(values: Iterable[Any]) -> float | None:
    usable: list[float] = []
    for value in values:
        if value is None:
            continue
        try:
            usable.append(float(value))
        except (TypeError, ValueError):
            continue
    if not usable:
        return None
    return sum(usable) / len(usable)


def _aggregate_per_sample_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    aggregate: dict[str, Any] = {"sample_count": len(rows)}
    for sample_key, aggregate_key in PER_SAMPLE_METRIC_MAP.items():
        aggregate[aggregate_key] = _mean(row.get(sample_key) for row in rows)
    return aggregate


def _profile_retrieval_rows(run_root: Path) -> dict[str, list[dict[str, Any]]]:
    return {
        public_name: _read_jsonl(run_root / underlying / "retrieval_results.jsonl")
        for public_name, underlying in PROFILE_ALIASES.items()
    }


def _question_type_metrics(
    *,
    cases: list[dict[str, Any]],
    per_samples: dict[str, list[dict[str, Any]]],
    retrieval_rows: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    case_types = {str(row.get("id")): str(row.get("question_type") or "unknown") for row in cases}
    type_order = list(dict.fromkeys(case_types.values()))
    output: dict[str, Any] = {}
    for question_type in type_order:
        case_ids = {case_id for case_id, type_name in case_types.items() if type_name == question_type}
        type_payload: dict[str, Any] = {
            "sample_count": len(case_ids),
            "profiles": {},
            "deltas": {},
        }
        for profile, rows in per_samples.items():
            selected_rows = [row for row in rows if str(row.get("id")) in case_ids]
            aggregate = _aggregate_per_sample_rows(selected_rows)
            selected_retrieval_rows = [
                row for row in retrieval_rows.get(profile, []) if str(row.get("id")) in case_ids
            ]
            aggregate.update(_cost_latency_from_rows(selected_retrieval_rows))
            type_payload["profiles"][profile] = aggregate
        profiles = type_payload["profiles"]
        type_payload["deltas"] = {
            "deep_vs_standard": _delta(
                profiles.get("deep_graphrag") or {},
                profiles.get("standard_rag") or {},
            ),
            "agentic_vs_standard": _delta(
                profiles.get("agentic_graphrag") or {},
                profiles.get("standard_rag") or {},
            ),
            "agentic_vs_deep": _delta(
                profiles.get("agentic_graphrag") or {},
                profiles.get("deep_graphrag") or {},
            ),
        }
        output[question_type] = type_payload
    return output


def _case_gold_evidence(case: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not case:
        return []
    gold = list(case.get("gold_evidence") or [])
    if gold:
        return gold
    return [{"doc_id": doc_id} for doc_id in _as_string_list(case.get("expected_doc_ids")) if doc_id]


def _context_matches_gold(context: dict[str, Any], case: dict[str, Any] | None) -> bool:
    gold = _case_gold_evidence(case)
    return bool(gold and _is_context_relevant(context, gold, allow_document_match=True))


def _row_float(row: dict[str, Any] | None, key: str) -> float | None:
    if not row:
        return None
    value = row.get(key)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _has_bucket_trace_fields(sample: dict[str, Any] | None, retrieval_row: dict[str, Any] | None) -> bool:
    if not sample:
        return False
    required_metric_keys = (
        "retrieval_recall",
        "evidence_text_available",
        "citation_accuracy",
        "source_doc_citation_accuracy",
        "answer_correctness",
    )
    if any(key not in sample for key in required_metric_keys):
        return False
    if retrieval_row is None:
        return False
    contexts = retrieval_row.get("contexts") if "contexts" in retrieval_row else retrieval_row.get("documents")
    return isinstance(contexts, list)


def _failure_bucket_for_sample(
    *,
    sample: dict[str, Any],
    retrieval_row: dict[str, Any] | None,
) -> tuple[str | None, str | None]:
    if not _has_bucket_trace_fields(sample, retrieval_row):
        return None, UNAVAILABLE_BUCKET_REASON

    recall = _row_float(sample, "retrieval_recall")
    evidence_text_available = _row_float(sample, "evidence_text_available")
    citation_accuracy = _row_float(sample, "citation_accuracy")
    source_doc_citation_accuracy = _row_float(sample, "source_doc_citation_accuracy")
    answer_correctness = _row_float(sample, "answer_correctness")

    if recall is None or evidence_text_available is None or answer_correctness is None:
        return None, UNAVAILABLE_BUCKET_REASON
    if recall <= 0:
        return "doc_miss", None
    if evidence_text_available <= 0:
        return "doc_hit_text_miss", None
    if citation_accuracy is None or source_doc_citation_accuracy is None:
        return None, UNAVAILABLE_BUCKET_REASON
    if citation_accuracy <= 0:
        return "text_hit_citation_miss", None
    if answer_correctness < 0.5:
        return "citation_hit_answer_wrong", None
    return None, None


def _build_evidence_conversion_diagnostics(
    *,
    cases: list[dict[str, Any]],
    per_samples: dict[str, list[dict[str, Any]]],
    retrieval_rows: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    cases_by_id = {str(row.get("id")): row for row in cases}
    samples_by_profile = {
        profile: {str(row.get("id")): row for row in rows}
        for profile, rows in per_samples.items()
    }
    retrieval_by_profile = {
        profile: {str(row.get("id")): row for row in rows}
        for profile, rows in retrieval_rows.items()
    }
    standard_by_id = samples_by_profile.get("standard_rag") or {}
    agentic_by_id = samples_by_profile.get("agentic_graphrag") or {}
    items: list[dict[str, Any]] = []
    tag_counts: dict[str, int] = {}
    failure_buckets = {bucket: 0 for bucket in FAILURE_BUCKETS}
    bucket_items: list[dict[str, Any]] = []
    unavailable_items: list[dict[str, Any]] = []

    def add(case_id: str, profile: str, tag: str) -> None:
        items.append(
            {
                "case_id": case_id,
                "question_type": str((cases_by_id.get(case_id) or {}).get("question_type") or "unknown"),
                "profile": profile,
                "tag": tag,
            }
        )
        tag_counts[tag] = tag_counts.get(tag, 0) + 1

    def add_bucket(case_id: str, profile: str, sample: dict[str, Any]) -> None:
        retrieval_row = (retrieval_by_profile.get(profile) or {}).get(case_id)
        bucket, unavailable_reason = _failure_bucket_for_sample(sample=sample, retrieval_row=retrieval_row)
        question_type = str((cases_by_id.get(case_id) or {}).get("question_type") or "unknown")
        if unavailable_reason:
            unavailable_items.append(
                {
                    "case_id": case_id,
                    "question_type": question_type,
                    "profile": profile,
                    "reason": unavailable_reason,
                }
            )
            tag_counts[unavailable_reason] = tag_counts.get(unavailable_reason, 0) + 1
            return
        if not bucket:
            return
        failure_buckets[bucket] += 1
        bucket_items.append(
            {
                "case_id": case_id,
                "question_type": question_type,
                "profile": profile,
                "bucket": bucket,
                "retrieval_recall": _row_float(sample, "retrieval_recall"),
                "evidence_text_available": _row_float(sample, "evidence_text_available"),
                "source_doc_citation_accuracy": _row_float(sample, "source_doc_citation_accuracy"),
                "citation_accuracy": _row_float(sample, "citation_accuracy"),
                "answer_correctness": _row_float(sample, "answer_correctness"),
            }
        )

    for profile, rows in samples_by_profile.items():
        for case_id, sample in rows.items():
            add_bucket(case_id, profile, sample)
            recall = _row_float(sample, "retrieval_recall") or 0.0
            answer_correctness = _row_float(sample, "answer_correctness")
            citation_accuracy = _row_float(sample, "citation_accuracy")
            evidence_text_available = _row_float(sample, "evidence_text_available")
            if recall > 0 and answer_correctness is not None and answer_correctness < 0.5:
                add(case_id, profile, "gold_doc_retrieved_but_answer_missing")
            if recall > 0 and citation_accuracy is not None and citation_accuracy <= 0:
                add(case_id, profile, "gold_doc_retrieved_but_citation_missing")
                add(case_id, profile, "citation_not_bound_to_gold_doc")
                if evidence_text_available is not None and evidence_text_available <= 0:
                    add(case_id, profile, "gold_text_not_in_retrieved_context")
                elif evidence_text_available is not None and evidence_text_available > 0:
                    add(case_id, profile, "citation_not_bound_to_gold_text")

    for case_id, agentic_sample in agentic_by_id.items():
        standard_sample = standard_by_id.get(case_id)
        agentic_recall = _row_float(agentic_sample, "retrieval_recall") or 0.0
        standard_recall = _row_float(standard_sample, "retrieval_recall") or 0.0
        agentic_answer = _row_float(agentic_sample, "answer_correctness")
        standard_answer = _row_float(standard_sample, "answer_correctness")
        agentic_retrieval = (retrieval_by_profile.get("agentic_graphrag") or {}).get(case_id)
        if agentic_recall > standard_recall:
            add(case_id, "agentic_graphrag", "agentic_added_new_gold_doc")
            if agentic_answer is not None and standard_answer is not None and agentic_answer < standard_answer:
                add(case_id, "agentic_graphrag", "answer_correctness_drop_despite_recall_gain")
        if not agentic_retrieval:
            add(case_id, "agentic_graphrag", UNAVAILABLE_BUCKET_REASON)
            continue
        metadata = dict(agentic_retrieval.get("metadata") or {})
        raw = dict(agentic_retrieval.get("raw_result") or {})
        contexts = list(agentic_retrieval.get("contexts") or agentic_retrieval.get("documents") or [])
        floor_fusion = bool(metadata.get("agentic_floor_fusion") or raw.get("agentic_floor_fusion"))
        if floor_fusion and standard_recall > 0 and agentic_recall >= standard_recall:
            add(case_id, "agentic_graphrag", "standard_floor_preserved_gold_doc")
        graph_contexts = [context for context in contexts if context.get("kind") == "graph_path"]
        if not graph_contexts:
            continue
        case = cases_by_id.get(case_id)
        gold_graph_contexts = [context for context in graph_contexts if _context_matches_gold(context, case)]
        non_gold_graph_contexts = [context for context in graph_contexts if not _context_matches_gold(context, case)]
        if agentic_recall > standard_recall and gold_graph_contexts:
            add(case_id, "agentic_graphrag", "graph_added_gold_doc")
        if agentic_recall <= standard_recall and non_gold_graph_contexts:
            add(case_id, "agentic_graphrag", "graph_added_non_gold_context")

    measured_bucket_count = sum(failure_buckets.values())
    return {
        "measurement_status": "fixed_benchmark",
        "bucket_taxonomy": FAILURE_BUCKETS,
        "failure_buckets": failure_buckets,
        "bucket_items": bucket_items,
        "unavailable_items": unavailable_items,
        "unavailable_reason": UNAVAILABLE_BUCKET_REASON if unavailable_items else None,
        "measured_failure_bucket_count": measured_bucket_count,
        "items": items,
        "tag_counts": tag_counts,
    }


def _build_gated_agentic_simulation(
    *,
    cases: list[dict[str, Any]],
    profiles: dict[str, Any],
    per_samples: dict[str, list[dict[str, Any]]],
    retrieval_rows: dict[str, list[dict[str, Any]]],
    question_type_metrics: dict[str, Any],
) -> dict[str, Any]:
    case_types = {str(row.get("id")): str(row.get("question_type") or "unknown") for row in cases}
    selected_profile_by_type: dict[str, str] = {}
    for question_type, payload in question_type_metrics.items():
        delta = ((payload.get("deltas") or {}).get("agentic_vs_standard") or {}).get("retrieval_recall_at_k")
        try:
            agentic_recall_gain = float(delta)
        except (TypeError, ValueError):
            agentic_recall_gain = 0.0
        selected_profile_by_type[question_type] = "agentic_graphrag" if agentic_recall_gain > 0 else "standard_rag"

    samples_by_profile = {
        profile: {str(row.get("id")): row for row in rows}
        for profile, rows in per_samples.items()
    }
    retrieval_by_profile = {
        profile: {str(row.get("id")): row for row in rows}
        for profile, rows in retrieval_rows.items()
    }

    selected_samples: list[dict[str, Any]] = []
    selected_retrieval_rows: list[dict[str, Any]] = []
    selected_case_profiles: dict[str, str] = {}
    profile_mix = {"standard_case_count": 0, "agentic_case_count": 0}
    for case in cases:
        case_id = str(case.get("id"))
        question_type = case_types.get(case_id, "unknown")
        selected_profile = selected_profile_by_type.get(question_type, "standard_rag")
        selected_case_profiles[case_id] = selected_profile
        if selected_profile == "agentic_graphrag":
            profile_mix["agentic_case_count"] += 1
        else:
            profile_mix["standard_case_count"] += 1
        sample = (samples_by_profile.get(selected_profile) or {}).get(case_id)
        if sample:
            selected_samples.append(sample)
        retrieval_row = (retrieval_by_profile.get(selected_profile) or {}).get(case_id)
        if retrieval_row:
            selected_retrieval_rows.append(retrieval_row)

    common_case_ids = set(case_types)
    all_agentic_rows = [
        row for row in retrieval_rows.get("agentic_graphrag", []) if str(row.get("id")) in common_case_ids
    ]
    aggregate = _aggregate_per_sample_rows(selected_samples)
    latency = _cost_latency_from_rows(selected_retrieval_rows)
    all_agentic_latency = _cost_latency_from_rows(all_agentic_rows)
    standard = (profiles.get("standard_rag") or {}).get("aggregate") or {}
    agentic = (profiles.get("agentic_graphrag") or {}).get("aggregate") or {}
    return {
        "metrics_source": "fixed_benchmark_simulation",
        "gate_policy": {
            "mode": "positive_agentic_recall_delta",
            "selected_profile_by_question_type": selected_profile_by_type,
            "selected_profile_by_case_id": selected_case_profiles,
        },
        "profile_mix": profile_mix,
        "aggregate": aggregate,
        "deltas_vs_standard": _delta(aggregate, standard),
        "deltas_vs_all_agentic": _delta(aggregate, agentic),
        **latency,
        "all_agentic_latency_p50_ms": all_agentic_latency.get("latency_p50_ms"),
        "all_agentic_latency_p95_ms": all_agentic_latency.get("latency_p95_ms"),
        "all_agentic_estimated_cost": all_agentic_latency.get("estimated_cost"),
    }


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
            if (
                float(row.get("retrieval_recall") or 0.0) > 0
                and row.get("citation_accuracy") is not None
                and float(row.get("citation_accuracy") or 0.0) <= 0
                and row.get("evidence_text_available") is not None
                and float(row.get("evidence_text_available") or 0.0) <= 0
            ):
                tags.append("gold_text_not_in_retrieved_context")
            if tags and not _has_advanced_failure_trace_fields(row):
                tags.append("unavailable_due_to_missing_trace_fields")
            if tags:
                failures.append({"case_id": row.get("id"), "profile": profile, "tags": tags})
    return failures


def _has_advanced_failure_trace_fields(row: dict[str, Any]) -> bool:
    return any(
        key in row
        for key in (
            "retrieval_contexts",
            "retrieval_rank_trace",
            "graph_context_gold_hits",
            "rerank_trace",
            "answer_type",
            "case_cost_usd",
            "latency_ms",
        )
    )


def _write_failure_cases(
    path: Path,
    failures: list[dict[str, Any]],
    *,
    diagnostics: dict[str, Any] | None = None,
) -> None:
    lines = ["# EnterpriseRAG Failure Cases", ""]
    if not failures:
        lines.append("No tagged failures were found in the measured per-sample metrics.")
    if any("unavailable_due_to_missing_trace_fields" in failure.get("tags", []) for failure in failures):
        lines.extend(
            [
                "Advanced failure tags were not fully available because the per-sample metrics do not yet carry graph context, rerank, no-answer, and per-case cost trace fields.",
                "",
            ]
        )
    for failure in failures:
        lines.append(f"- `{failure['case_id']}` / `{failure['profile']}`: {', '.join(failure['tags'])}")
    diagnostic_items = list((diagnostics or {}).get("items") or [])
    bucket_items = list((diagnostics or {}).get("bucket_items") or [])
    unavailable_items = list((diagnostics or {}).get("unavailable_items") or [])
    if bucket_items or unavailable_items:
        lines.extend(["", "## PHASE01 Failure Buckets", ""])
        buckets_by_name: dict[str, list[dict[str, Any]]] = {bucket: [] for bucket in FAILURE_BUCKETS}
        for item in bucket_items:
            buckets_by_name.setdefault(str(item.get("bucket")), []).append(item)
        for bucket in FAILURE_BUCKETS:
            lines.extend(["", f"### {bucket}", ""])
            bucket_cases = buckets_by_name.get(bucket) or []
            if not bucket_cases:
                lines.append("- None measured.")
                continue
            for item in bucket_cases:
                lines.append(
                    "- `{case_id}` / `{profile}` / `{question_type}`: recall={recall}, evidence_text={evidence}, source_doc_citation={source_doc}, strict_citation={citation}, answer={answer}".format(
                        case_id=item.get("case_id"),
                        profile=item.get("profile"),
                        question_type=item.get("question_type"),
                        recall=_fmt(item.get("retrieval_recall")),
                        evidence=_fmt(item.get("evidence_text_available")),
                        source_doc=_fmt(item.get("source_doc_citation_accuracy")),
                        citation=_fmt(item.get("citation_accuracy")),
                        answer=_fmt(item.get("answer_correctness")),
                    )
                )
        if unavailable_items:
            lines.extend(["", f"### {UNAVAILABLE_BUCKET_REASON}", ""])
            for item in unavailable_items:
                lines.append(
                    "- `{case_id}` / `{profile}` / `{question_type}`: {reason}".format(
                        case_id=item.get("case_id"),
                        profile=item.get("profile"),
                        question_type=item.get("question_type"),
                        reason=item.get("reason"),
                    )
                )
    if diagnostic_items:
        lines.extend(["", "## Evidence Conversion Diagnostics", ""])
        for item in diagnostic_items:
            lines.append(
                "- `{case_id}` / `{profile}` / `{question_type}`: {tag}".format(
                    case_id=item.get("case_id"),
                    profile=item.get("profile"),
                    question_type=item.get("question_type"),
                    tag=item.get("tag"),
                )
            )
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def _write_report(path: Path, metrics: dict[str, Any]) -> None:
    lines = [
        "# EnterpriseRAG Paired Benchmark",
        "",
        f"- status: `{metrics['status']}`",
        f"- measurement_status: `{metrics['measurement_status']}`",
        f"- selected_case_count: `{metrics['case_set']['selected_case_count']}`",
        f"- measured_case_count: `{metrics['case_set']['measured_case_count']}`",
        f"- chunk_size_override: `{(metrics.get('runtime_config') or {}).get('chunk_size_override')}`",
        f"- overlap_override: `{(metrics.get('runtime_config') or {}).get('overlap_override')}`",
        "",
        (
            "| Profile | Measured | Recall@5 | MRR@5 | Answer Correctness | Citation Accuracy | "
            "Source Doc Citation | Evidence Text Available | Latency p95 ms | Cost |"
        ),
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for profile, payload in metrics.get("profiles", {}).items():
        aggregate = payload.get("aggregate") or {}
        lines.append(
            "| {profile} | {measured} | {recall} | {mrr} | {correctness} | {citation} | {source_doc_citation} | {evidence_text_available} | {latency} | {cost} |".format(
                profile=profile,
                measured=str(bool(payload.get("measured"))).lower(),
                recall=_fmt(aggregate.get("retrieval_recall_at_k")),
                mrr=_fmt(aggregate.get("mrr_at_k")),
                correctness=_fmt(aggregate.get("answer_correctness")),
                citation=_fmt(aggregate.get("citation_accuracy")),
                source_doc_citation=_fmt(aggregate.get("source_doc_citation_accuracy")),
                evidence_text_available=_fmt(aggregate.get("evidence_text_available_at_k")),
                latency=_fmt(payload.get("latency_p95_ms")),
                cost=_fmt(payload.get("estimated_cost")),
            )
        )
    if metrics.get("deltas"):
        lines.extend(
            [
                "",
                "## Paired Deltas",
                "",
                "| Delta | Recall@5 | MRR@5 | Answer Correctness | Citation Accuracy | Source Doc Citation | Evidence Text Available |",
                "|---|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for name, delta in metrics.get("deltas", {}).items():
            lines.append(
                "| {name} | {recall} | {mrr} | {correctness} | {citation} | {source_doc_citation} | {evidence_text_available} |".format(
                    name=name,
                    recall=_fmt((delta or {}).get("retrieval_recall_at_k")),
                    mrr=_fmt((delta or {}).get("mrr_at_k")),
                    correctness=_fmt((delta or {}).get("answer_correctness")),
                    citation=_fmt((delta or {}).get("citation_accuracy")),
                    source_doc_citation=_fmt((delta or {}).get("source_doc_citation_accuracy")),
                    evidence_text_available=_fmt((delta or {}).get("evidence_text_available_at_k")),
                )
            )
    if metrics.get("question_type_metrics"):
        lines.extend(
            [
                "",
                "## Question Type Breakdown",
                "",
                (
                    "| Question Type | Cases | Standard Recall@5 | Deep Recall@5 | Agentic Recall@5 | "
                    "Agentic Δ Recall | Agentic Δ Answer | Agentic Δ Citation | "
                    "Agentic Δ Source Doc Citation | Agentic Δ Evidence Text | Agentic p95 ms |"
                ),
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for question_type, payload in metrics.get("question_type_metrics", {}).items():
            profiles = payload.get("profiles") or {}
            deltas = payload.get("deltas") or {}
            agentic_delta = deltas.get("agentic_vs_standard") or {}
            lines.append(
                "| {question_type} | {cases} | {standard} | {deep} | {agentic} | {delta_recall} | {delta_answer} | {delta_citation} | {delta_source_doc_citation} | {delta_evidence_text} | {latency} |".format(
                    question_type=question_type,
                    cases=payload.get("sample_count"),
                    standard=_fmt((profiles.get("standard_rag") or {}).get("retrieval_recall_at_k")),
                    deep=_fmt((profiles.get("deep_graphrag") or {}).get("retrieval_recall_at_k")),
                    agentic=_fmt((profiles.get("agentic_graphrag") or {}).get("retrieval_recall_at_k")),
                    delta_recall=_fmt(agentic_delta.get("retrieval_recall_at_k")),
                    delta_answer=_fmt(agentic_delta.get("answer_correctness")),
                    delta_citation=_fmt(agentic_delta.get("citation_accuracy")),
                    delta_source_doc_citation=_fmt(agentic_delta.get("source_doc_citation_accuracy")),
                    delta_evidence_text=_fmt(agentic_delta.get("evidence_text_available_at_k")),
                    latency=_fmt((profiles.get("agentic_graphrag") or {}).get("latency_p95_ms")),
                )
            )
        lines.extend(
            [
                "",
                "### Strategy Gate Notes",
                "",
                "- Treat question types with positive agentic retrieval delta as candidates for agentic deep routing.",
                "- Treat question types with no agentic retrieval gain and higher latency as candidates for standard-first routing.",
                "- Answer/citation non-gain means the next bottleneck is evidence-to-answer synthesis and citation binding, not more context alone.",
            ]
        )
    if metrics.get("agentic_metrics"):
        agentic_metrics = metrics["agentic_metrics"]
        lines.extend(
            [
                "",
                "## Agentic Metrics",
                "",
                f"- graph_usage_gain: `{_fmt(agentic_metrics.get('graph_usage_gain'))}`",
                f"- replan_success_rate: `{_fmt(agentic_metrics.get('replan_success_rate'))}`",
                f"- cost_quality_ratio: `{_fmt(agentic_metrics.get('cost_quality_ratio'))}`",
            ]
        )
    gated = metrics.get("gated_agentic_simulation") or {}
    if gated:
        gate_policy = gated.get("gate_policy") or {}
        profile_mix = gated.get("profile_mix") or {}
        aggregate = gated.get("aggregate") or {}
        deltas = gated.get("deltas_vs_standard") or {}
        lines.extend(
            [
                "",
                "## Gated Agentic Simulation",
                "",
                f"- metrics_source: `{gated.get('metrics_source')}`",
                f"- gate_policy: `{gate_policy.get('mode')}`",
                f"- standard_case_count: `{profile_mix.get('standard_case_count')}`",
                f"- agentic_case_count: `{profile_mix.get('agentic_case_count')}`",
                f"- Recall@5: `{_fmt(aggregate.get('retrieval_recall_at_k'))}`",
                f"- Recall@5 delta vs standard: `{_fmt(deltas.get('retrieval_recall_at_k'))}`",
                f"- Answer Correctness delta vs standard: `{_fmt(deltas.get('answer_correctness'))}`",
                f"- Source Doc Citation delta vs standard: `{_fmt(deltas.get('source_doc_citation_accuracy'))}`",
                f"- latency_p50_ms: `{_fmt(gated.get('latency_p50_ms'))}`",
                f"- latency_p95_ms: `{_fmt(gated.get('latency_p95_ms'))}`",
                f"- all_agentic_latency_p95_ms: `{_fmt(gated.get('all_agentic_latency_p95_ms'))}`",
                "",
                "| Question Type | Selected Profile |",
                "|---|---|",
            ]
        )
        for question_type, profile in (gate_policy.get("selected_profile_by_question_type") or {}).items():
            lines.append(f"| {question_type} | {profile} |")
    diagnostics = metrics.get("evidence_conversion_diagnostics") or {}
    if diagnostics.get("tag_counts") or diagnostics.get("bucket_items") or diagnostics.get("unavailable_items"):
        lines.extend(["", "## Evidence Conversion Diagnostics", ""])
        lines.extend(
            [
                "- measured_state: `fixed_benchmark` only when `measurement_status` is `fixed_benchmark`; blocked and prepared runs remain not measured.",
                "- Evidence Text Available@5 checks whether the gold text span is present in retrieved context; strict citation additionally requires the answer citation to bind to that gold text, so source-doc citation alone is not strict citation.",
                "- Responsibility boundary: `doc_miss` belongs to retrieval, `doc_hit_text_miss` to evidence text/chunking/rerank, `text_hit_citation_miss` to citation binding, and `citation_hit_answer_wrong` to answer synthesis.",
                "",
                "### PHASE01 Failure Buckets",
                "",
            ]
        )
        buckets = diagnostics.get("failure_buckets") or {}
        for bucket in FAILURE_BUCKETS:
            lines.append(f"- {bucket}: `{buckets.get(bucket, 0)}`")
        if diagnostics.get("unavailable_items"):
            lines.append(f"- {UNAVAILABLE_BUCKET_REASON}: `{len(diagnostics.get('unavailable_items') or [])}`")
        lines.append("")
        for tag, count in sorted((diagnostics.get("tag_counts") or {}).items()):
            lines.append(f"- {tag}: `{count}`")
    if metrics["measurement_status"] == "blocked_not_measured":
        lines.extend(
            [
                "",
                "## Blocked",
                "",
                f"- blocked_reason: `{metrics['corpus'].get('blocked_reason')}`",
                "- No benchmark metrics were measured because the EnterpriseRAG-Bench corpus is blocked.",
            ]
        )
    agentic = (metrics.get("profiles") or {}).get("agentic_graphrag") or {}
    if agentic.get("measured") is False and agentic.get("blocked_reason"):
        lines.extend(
            [
                "",
                "## Agentic GraphRAG",
                "",
                f"- measured: `false`",
                f"- blocked_reason: `{agentic.get('blocked_reason')}`",
            ]
        )
    if metrics.get("failure_tag_limitations"):
        lines.extend(
            [
                "",
                "## Failure Tag Limitations",
                "",
                str(metrics["failure_tag_limitations"]),
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
            "agentic_graphrag": {
                "measured": False,
                "metrics_source": "blocked_not_measured",
                "blocked_reason": "agentic_runtime_runner_not_wired",
                "aggregate": {},
            },
        },
        "deltas": {},
        "agentic_metrics": {"graph_usage_gain": None, "replan_success_rate": None, "cost_quality_ratio": None},
        "question_type_metrics": {},
        "evidence_conversion_diagnostics": {
            "measurement_status": "blocked_not_measured",
            "bucket_taxonomy": FAILURE_BUCKETS,
            "failure_buckets": {bucket: 0 for bucket in FAILURE_BUCKETS},
            "bucket_items": [],
            "unavailable_items": [],
            "unavailable_reason": None,
            "measured_failure_bucket_count": 0,
            "items": [],
            "tag_counts": {},
        },
        "gated_agentic_simulation": {},
        "cost_latency": {},
        "failure_count": 0,
        "failure_tag_limitations": _failure_tag_limitations(),
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


def inspect_documents_schema(document_source: Path, *, output_root: Path, preview_chars: int = 160) -> dict[str, Any]:
    probe = inspect_enterprise_document_schema(document_source, preview_chars=preview_chars)
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "schema_probe.json").write_text(json.dumps(probe, ensure_ascii=False, indent=2), encoding="utf-8")
    return probe


def _failure_tag_limitations() -> str:
    return (
        "Advanced tags require per-sample graph context, rerank rank trace, no-answer labels, "
        "and per-case cost/latency fields. Missing fields are tagged as "
        "unavailable_due_to_missing_trace_fields rather than inferred."
    )


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
    inspect_schema: bool = False,
    spawn_dev_embedding_server: bool = True,
    rerank_score_threshold_override: float | None = 0.0,
    chunk_size_override: int | None = ENTERPRISE_RAG_DEFAULT_CHUNK_SIZE,
    overlap_override: int | None = ENTERPRISE_RAG_DEFAULT_OVERLAP,
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
    schema_probe = inspect_documents_schema(document_source, output_root=output_root) if inspect_schema and document_source else None
    corpus_dir = output_root / "corpus"
    prepared = prepare_public_enterprise_eval(
        dataset_id="enterprise_rag_bench",
        raw_path=selected_questions,
        source_root=document_source,
        output_dir=corpus_dir,
    )
    manifest_path = Path(prepared["manifest_path"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if schema_probe is not None:
        manifest["schema_probe"] = schema_probe
    if documents_file is not None:
        manifest["documents_file"] = str(documents_file)
    if source_root is not None:
        manifest["source_root"] = str(source_root)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
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
        metrics["evidence_conversion_diagnostics"]["measurement_status"] = "prepared_not_measured"
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
        chunk_size_override=chunk_size_override,
        overlap_override=overlap_override,
    )
    profiles, cost_latency, per_samples = _build_profile_summary(run_root=stackless_root, run_report=run_report)
    cases = _read_jsonl(dataset_path)
    retrieval_rows = _profile_retrieval_rows(stackless_root)
    common_case_ids = [str(row.get("id")) for row in cases]
    standard = profiles["standard_rag"].get("aggregate") or {}
    deep = profiles["deep_graphrag"].get("aggregate") or {}
    agentic = profiles["agentic_graphrag"].get("aggregate") or {}
    deep_vs_standard = _delta(deep, standard)
    agentic_vs_standard = _delta(agentic, standard) if agentic else {}
    agentic_vs_deep = _delta(agentic, deep) if agentic else {}
    failures = _build_failure_cases(per_samples)
    evidence_conversion_diagnostics = _build_evidence_conversion_diagnostics(
        cases=cases,
        per_samples=per_samples,
        retrieval_rows=retrieval_rows,
    )
    failure_tag_limitations = _failure_tag_limitations()
    replan_success_rate = (
        _replan_success_rate(
            run_root=stackless_root,
            agentic_underlying_profile=str(profiles["agentic_graphrag"].get("underlying_profile") or "agentic_graphrag"),
            standard_rows=per_samples.get("standard_rag") or [],
            agentic_rows=per_samples.get("agentic_graphrag") or [],
        )
        if agentic
        else None
    )
    graph_usage_gain = (
        agentic_vs_standard.get("retrieval_recall_at_k")
        if agentic_vs_standard
        else deep_vs_standard.get("retrieval_recall_at_k")
    )
    question_type_metrics = _question_type_metrics(
        cases=cases,
        per_samples=per_samples,
        retrieval_rows=retrieval_rows,
    )
    gated_agentic_simulation = _build_gated_agentic_simulation(
        cases=cases,
        profiles=profiles,
        per_samples=per_samples,
        retrieval_rows=retrieval_rows,
        question_type_metrics=question_type_metrics,
    )
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
        "runtime_config": {
            "chunk_size_override": chunk_size_override,
            "overlap_override": overlap_override,
            "rerank_score_threshold_override": rerank_score_threshold_override,
        },
        "profiles": profiles,
        "deltas": {
            "deep_vs_standard": deep_vs_standard,
            "agentic_vs_standard": agentic_vs_standard,
            "agentic_vs_deep": agentic_vs_deep,
        },
        "question_type_metrics": question_type_metrics,
        "agentic_metrics": {
            "graph_usage_gain": graph_usage_gain,
            "replan_success_rate": replan_success_rate,
            "cost_quality_ratio": _cost_quality_ratio(
                quality_delta=agentic_vs_standard.get("answer_correctness") if agentic_vs_standard else None,
                standard_latency=cost_latency.get("standard_rag") or {},
                agentic_latency=cost_latency.get("agentic_graphrag") or {},
            ),
        },
        "evidence_conversion_diagnostics": evidence_conversion_diagnostics,
        "gated_agentic_simulation": gated_agentic_simulation,
        "cost_latency": cost_latency,
        "failure_count": len(failures),
        "failure_tag_limitations": failure_tag_limitations,
    }
    (output_root / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_failure_cases(
        output_root / "failure_cases.md",
        failures,
        diagnostics=evidence_conversion_diagnostics,
    )
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
    parser.add_argument("--inspect-documents-schema", action="store_true")
    parser.add_argument("--no-spawn-dev-embedding-server", action="store_true")
    parser.add_argument("--rerank-score-threshold-override", type=float, default=0.0)
    parser.add_argument("--chunk-size-override", type=int, default=ENTERPRISE_RAG_DEFAULT_CHUNK_SIZE)
    parser.add_argument("--overlap-override", type=int, default=ENTERPRISE_RAG_DEFAULT_OVERLAP)
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
            inspect_schema=args.inspect_documents_schema,
            spawn_dev_embedding_server=not args.no_spawn_dev_embedding_server,
            rerank_score_threshold_override=args.rerank_score_threshold_override,
            chunk_size_override=args.chunk_size_override,
            overlap_override=args.overlap_override,
        )
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
