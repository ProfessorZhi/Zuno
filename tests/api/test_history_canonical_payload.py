from __future__ import annotations


def test_history_rag_payload_uses_canonical_dict_shape() -> None:
    from zuno.api.services.history import HistoryService

    payload = HistoryService._history_chunk_payload(
        collection_name="dialog_memory",
        content="User asked about renewal notices.",
    )

    assert payload["chunk_id"]
    assert payload["content"] == "User asked about renewal notices."
    assert payload["file_id"] == "history_rag"
    assert payload["file_name"] == "history_rag"
    assert payload["knowledge_id"] == "dialog_memory"
    assert payload["modality"] == "text"
    assert payload["source_chunk_id"] == payload["chunk_id"]
    assert payload["document_hash"]
    assert payload["chunk_hash"]
    assert payload["metadata"] == {"source": "history_rag"}
