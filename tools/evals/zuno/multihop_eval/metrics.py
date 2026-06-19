from __future__ import annotations


def recall_at_k(retrieved_ids: list[str], gold_ids: list[str], k: int) -> float:
    if not gold_ids:
        return 0.0
    retrieved = set(retrieved_ids[:k])
    return len(retrieved & set(gold_ids)) / len(set(gold_ids))


__all__ = ["recall_at_k"]

