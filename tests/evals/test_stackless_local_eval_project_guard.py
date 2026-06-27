import asyncio

import pytest


def test_stackless_local_graph_retriever_rejects_domain_pack_without_project_assets():
    from zuno.evals.rag_eval.run_stackless_local_eval import _build_local_graph_retriever
    from zuno.schema.chunk import ChunkModel
    with pytest.raises(ModuleNotFoundError):
        __import__("zuno.services.domain_pack.loader")

    chunk = ChunkModel(
        chunk_id="plain_chunk_1",
        content="plain local graph text",
        file_id="file_plain_1",
        file_name="plain.md",
        update_time="2026-06-08T00:00:00",
        knowledge_id="kb_plain",
        summary="plain",
    )

    with pytest.raises(ValueError, match="GraphRAG Project assets are required"):
        asyncio.run(
            _build_local_graph_retriever(
                [chunk],
                domain_pack_id="unknown_legacy_pack",
            )
        )
