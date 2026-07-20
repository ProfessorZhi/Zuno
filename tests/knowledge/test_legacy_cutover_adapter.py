from __future__ import annotations

import asyncio


def test_legacy_cutover_adapter_projects_parse_gateway_ir_to_chunks(tmp_path) -> None:
    from zuno.knowledge.ingestion import (
        LEGACY_ADAPTER_ID,
        LEGACY_ADAPTER_REMOVAL_PHASE,
        parse_file_into_legacy_chunks,
        parse_file_to_canonical_ir,
    )

    source = tmp_path / "policy.md"
    source.write_text("# Policy\nRenewal notice is required.", encoding="utf-8")

    document = parse_file_to_canonical_ir(
        file_id="file_policy",
        file_path=str(source),
        knowledge_id="knowledge_policy",
        knowledge_config={"index_capability": "rag"},
    )
    chunks = asyncio.run(
        parse_file_into_legacy_chunks(
            file_id="file_policy",
            file_path=str(source),
            knowledge_id="knowledge_policy",
            knowledge_config={"index_capability": "rag"},
        )
    )

    assert document.metadata.parser_id == "native"
    assert document.transform_ledger
    assert document.transform_ledger[0].provenance["parser_config_hash"]
    assert document.transform_ledger[0].provenance["block_count"] >= 1
    assert chunks
    assert chunks[0].file_id == "file_policy"
    assert chunks[0].knowledge_id == "knowledge_policy"
    assert chunks[0].document_hash == document.metadata.source_sha256
    assert chunks[0].source_chunk_id.startswith("file_policy:")
    assert document.metadata.source_sha256 in chunks[0].source_chunk_id
    assert LEGACY_ADAPTER_ID == "temporary.adapter.phase11.legacy_chunk_projection"
    assert LEGACY_ADAPTER_REMOVAL_PHASE == "PHASE16"
