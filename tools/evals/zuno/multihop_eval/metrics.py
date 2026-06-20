from __future__ import annotations

from typing import Any, Iterable


def _unique_in_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        normalized = str(value or "").strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return ordered


def _hits_at_k(retrieved_ids: list[str], gold_ids: set[str], k: int) -> int:
    return sum(1 for item in _unique_in_order(retrieved_ids)[:k] if item in gold_ids)


def _recall_for_hits(*, hits: int, gold_count: int) -> float | None:
    if gold_count <= 0:
        return None
    return hits / gold_count


def _precision_at_k(*, hits: int, k: int) -> float:
    if k <= 0:
        return 0.0
    return hits / k


def _mrr_at_k(retrieved_ids: list[str], gold_ids: set[str], k: int) -> float | None:
    if not gold_ids:
        return None
    for index, item in enumerate(_unique_in_order(retrieved_ids)[:k], start=1):
        if item in gold_ids:
            return 1.0 / index
    return 0.0


def _full_chain_hit(*, hits: int, gold_count: int) -> float | None:
    if gold_count <= 0:
        return None
    return 1.0 if hits == gold_count else 0.0


def _mean(values: Iterable[float | None]) -> float | None:
    usable = [value for value in values if value is not None]
    if not usable:
        return None
    return sum(usable) / len(usable)


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    rank = (len(ordered) - 1) * percentile
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def recall_at_k(retrieved_ids: list[str], gold_ids: list[str], k: int) -> float:
    unique_gold = set(_unique_in_order(gold_ids))
    if not unique_gold:
        return 0.0
    return _hits_at_k(retrieved_ids, unique_gold, k) / len(unique_gold)


def compute_question_metrics(
    *,
    question_id: str,
    gold_doc_ids: Iterable[str],
    retrieved_doc_ids: Iterable[str],
    latency_ms: float | None = None,
    fallback: bool = False,
    failure: bool = False,
) -> dict[str, Any]:
    normalized_gold = set(_unique_in_order(gold_doc_ids))
    normalized_retrieved = _unique_in_order(retrieved_doc_ids)
    gold_count = len(normalized_gold)
    invalid_gold = gold_count == 0

    hits_at_2 = _hits_at_k(normalized_retrieved, normalized_gold, 2) if not invalid_gold else 0
    hits_at_5 = _hits_at_k(normalized_retrieved, normalized_gold, 5) if not invalid_gold else 0
    hits_at_10 = _hits_at_k(normalized_retrieved, normalized_gold, 10) if not invalid_gold else 0

    return {
        "question_id": question_id,
        "gold_count": gold_count,
        "retrieved_count": len(normalized_retrieved),
        "hits_at_2": hits_at_2,
        "hits_at_5": hits_at_5,
        "hits_at_10": hits_at_10,
        "recall_at_2": _recall_for_hits(hits=hits_at_2, gold_count=gold_count),
        "recall_at_5": _recall_for_hits(hits=hits_at_5, gold_count=gold_count),
        "recall_at_10": _recall_for_hits(hits=hits_at_10, gold_count=gold_count),
        "precision_at_5": _precision_at_k(hits=hits_at_5, k=5) if not invalid_gold else None,
        "precision_at_10": _precision_at_k(hits=hits_at_10, k=10) if not invalid_gold else None,
        "mrr_at_10": _mrr_at_k(normalized_retrieved, normalized_gold, 10),
        "chain_recall_at_5": _recall_for_hits(hits=hits_at_5, gold_count=gold_count),
        "chain_recall_at_10": _recall_for_hits(hits=hits_at_10, gold_count=gold_count),
        "full_chain_hit_at_5": _full_chain_hit(hits=hits_at_5, gold_count=gold_count),
        "full_chain_hit_at_10": _full_chain_hit(hits=hits_at_10, gold_count=gold_count),
        "latency_ms": latency_ms,
        "fallback": bool(fallback),
        "failure": bool(failure),
        "invalid_gold": invalid_gold,
    }


def aggregate_question_metrics(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    materialized = list(rows)
    valid_rows = [row for row in materialized if not row.get("invalid_gold")]
    latencies = [float(row["latency_ms"]) for row in materialized if row.get("latency_ms") is not None]
    failure_count = sum(1 for row in materialized if row.get("failure"))
    fallback_count = sum(1 for row in materialized if row.get("fallback"))
    empty_result_count = sum(1 for row in materialized if int(row.get("retrieved_count", 0)) == 0)
    question_count = len(materialized)

    return {
        "question_count": question_count,
        "valid_question_count": len(valid_rows),
        "Recall@2": _mean(row.get("recall_at_2") for row in valid_rows),
        "Recall@5": _mean(row.get("recall_at_5") for row in valid_rows),
        "Recall@10": _mean(row.get("recall_at_10") for row in valid_rows),
        "Precision@5": _mean(row.get("precision_at_5") for row in valid_rows),
        "Precision@10": _mean(row.get("precision_at_10") for row in valid_rows),
        "MRR@10": _mean(row.get("mrr_at_10") for row in valid_rows),
        "ChainRecall@5": _mean(row.get("chain_recall_at_5") for row in valid_rows),
        "ChainRecall@10": _mean(row.get("chain_recall_at_10") for row in valid_rows),
        "FullChainHit@5": _mean(row.get("full_chain_hit_at_5") for row in valid_rows),
        "FullChainHit@10": _mean(row.get("full_chain_hit_at_10") for row in valid_rows),
        "avg_latency_ms": _mean(latencies),
        "p50_latency_ms": _percentile(latencies, 0.50),
        "p95_latency_ms": _percentile(latencies, 0.95),
        "failure_count": failure_count,
        "failure_rate": (failure_count / question_count) if question_count else 0.0,
        "fallback_count": fallback_count,
        "fallback_rate": (fallback_count / question_count) if question_count else 0.0,
        "empty_result_count": empty_result_count,
    }


__all__ = [
    "aggregate_question_metrics",
    "compute_question_metrics",
    "recall_at_k",
]
