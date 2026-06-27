def test_graphrag_version_state_records_hashes_and_versions():
    from zuno.services.graphrag.versioning import GraphRAGVersionState

    state = GraphRAGVersionState(
        index_version="graph-v2",
        community_version="community-v3",
        document_hash="doc-sha",
        chunk_hash="chunk-sha",
        status="active",
    )

    assert state.to_trace() == {
        "index_version": "graph-v2",
        "community_version": "community-v3",
        "document_hash": "doc-sha",
        "chunk_hash": "chunk-sha",
        "status": "active",
    }


def test_graphrag_version_state_detects_stale_index_use():
    from zuno.services.graphrag.versioning import detect_stale_index_reasons

    assert detect_stale_index_reasons(
        index_health={"vector": "ready", "graph": "stale", "community": "ready"},
        scope_policy={"status": "active"},
    ) == ["graph index health is stale"]
    assert detect_stale_index_reasons(
        index_health={"vector": "ready", "graph": "ready"},
        scope_policy={"status": "archived"},
    ) == ["knowledge status is archived"]


def test_graph_writer_preserves_version_and_hash_metadata():
    from zuno.services.graphrag.graph_store.graph_writer import GraphWriter

    payload = GraphWriter().build_entity_payload(
        {
            "name": "Clause",
            "chunk_id": "chunk-1",
            "document_hash": "doc-sha",
            "chunk_hash": "chunk-sha",
        },
        domain_pack_id="legacy",
        index_version="graph-v2",
        status="active",
        knowledge_file_id="file-1",
    )

    assert payload["index_version"] == "graph-v2"
    assert payload["document_hash"] == "doc-sha"
    assert payload["chunk_hash"] == "chunk-sha"
    assert payload["source_chunk_id"] == "chunk-1"
    assert payload["status"] == "active"
