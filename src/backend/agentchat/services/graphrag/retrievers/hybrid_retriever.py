from __future__ import annotations


class HybridRetriever:
    def merge(self, *, vector_documents: list[dict] | None = None, graph_documents: list[dict] | None = None) -> list[dict]:
        seen: set[str] = set()
        merged: list[dict] = []
        for item in (vector_documents or []) + (graph_documents or []):
            chunk_id = str(item.get("chunk_id") or "")
            if chunk_id and chunk_id in seen:
                continue
            if chunk_id:
                seen.add(chunk_id)
            merged.append(item)
        return merged
