from __future__ import annotations

from zuno.knowledge.agentic.contracts import CorrectiveAction, RetrievalQualityVerdict


class CorrectiveRetrievalPolicy:
    def decide(
        self,
        *,
        verdict: RetrievalQualityVerdict,
        failure_bucket: str = "",
        used_actions: list[CorrectiveAction] | None = None,
        max_rounds_reached: bool = False,
        novelty: float = 1.0,
    ) -> CorrectiveAction:
        used = set(used_actions or [])
        if verdict == RetrievalQualityVerdict.RELEVANT:
            return CorrectiveAction.CONTINUE
        if max_rounds_reached or (novelty <= 0.0 and not failure_bucket):
            return CorrectiveAction.ABSTAIN
        if verdict == RetrievalQualityVerdict.INSUFFICIENT_SPAN or failure_bucket == "text_hit_citation_miss":
            return self._first_unused([CorrectiveAction.FOCUSED_CITATION_RETRIEVE], used)
        if failure_bucket == "doc_miss":
            return self._first_unused(
                [CorrectiveAction.QUERY_REWRITE, CorrectiveAction.MULTI_QUERY, CorrectiveAction.HYDE],
                used,
            )
        if failure_bucket == "doc_hit_text_miss":
            return self._first_unused([CorrectiveAction.PARENT_EXPAND, CorrectiveAction.GRAPH_EXPAND], used)
        if verdict == RetrievalQualityVerdict.CONFLICTING:
            return self._first_unused([CorrectiveAction.GRAPH_EXPAND, CorrectiveAction.ASK_USER], used)
        if novelty <= 0.0 and used:
            return CorrectiveAction.ABSTAIN
        if verdict in {RetrievalQualityVerdict.IRRELEVANT, RetrievalQualityVerdict.AMBIGUOUS}:
            return self._first_unused([CorrectiveAction.QUERY_REWRITE, CorrectiveAction.STEP_BACK], used)
        return CorrectiveAction.CONTINUE

    def _first_unused(self, candidates: list[CorrectiveAction], used: set[CorrectiveAction]) -> CorrectiveAction:
        for candidate in candidates:
            if candidate not in used:
                return candidate
        return CorrectiveAction.ABSTAIN


__all__ = ["CorrectiveRetrievalPolicy"]
