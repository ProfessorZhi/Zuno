import asyncio
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src" / "backend"))

from zuno.services.graphrag.retriever import GraphRetriever
from zuno.services.retrieval.fusion import RetrievalFusion
from zuno.services.retrieval.models import ProcessedQuery, RetrievedDocument
from zuno.services.retrieval.orchestrator import RetrievalOrchestrator


GENEALOGY_QUERY = "Who is the maternal grandfather of Antiochus X Eusebes?"
BRIDGE_QUERY = "Where was the director of film Ronnie Rocket born?"


def _doc(
    chunk_id: str,
    file_name: str,
    source_type: str,
    score: float,
    *,
    content: str | None = None,
    matched_by: list[str] | None = None,
    metadata: dict | None = None,
):
    payload = {
        "matched_by": list(matched_by or [source_type]),
    }
    payload.update(dict(metadata or {}))
    return RetrievedDocument(
        chunk_id=chunk_id,
        knowledge_id="kb_1",
        file_id=file_name,
        file_name=file_name,
        content=content or file_name,
        summary="",
        score=score,
        normalized_score=None,
        source_type=source_type,
        source_backend=source_type,
        retrieval_reason=source_type,
        metadata=payload,
    )


class _StaticRetriever:
    def __init__(self, payload: dict):
        self.payload = payload

    async def retrieve(self, query, knowledge_ids, options=None):
        return self.payload


class _NoRewriteExpander:
    async def expand(self, query: str):
        return [query]


class _RelationQueryProcessor:
    async def process(self, query: str):
        return ProcessedQuery(
            original_query=query,
            normalized_query=query,
            rewritten_queries=[query],
            intent_labels=[],
            query_features={
                "relation_question": True,
                "global_question": False,
                "evidence_required": False,
            },
            route_hints=[],
        )


def _vector_payload(*docs):
    return {
        "content": "\n".join(doc.file_name for doc in docs),
        "raw_content": "\n".join(doc.file_name for doc in docs),
        "documents": [doc.to_dict() for doc in docs],
    }


def _graph_payload(*docs):
    return {
        "content": "\n".join(doc.file_name for doc in docs),
        "raw_content": "\n".join(doc.file_name for doc in docs),
        "documents": [doc.to_dict() for doc in docs],
        "entities": [{"name": "Antiochus X Eusebes"}] if docs else [],
        "paths": ["Antiochus X Eusebes -> Cleopatra IV of Egypt"] if docs else [],
        "structured_paths": [
            {
                "source": "Antiochus X Eusebes",
                "target": "Cleopatra IV of Egypt",
                "relation_type": "mother",
                "relation_labels": ["mother", "father"],
                "chunk_ids": [docs[0].chunk_id],
            }
        ]
        if docs
        else [],
        "seed_entities_with_source": [{"value": "Antiochus X Eusebes", "source": "query"}],
    }


def test_graph_retriever_emits_typed_genealogy_path_metadata():
    class FakeClient:
        async def query_neighbors(
            self,
            entity_name,
            knowledge_id,
            hops=1,
            limit=10,
            domain_pack_id=None,
            index_version=None,
            status=None,
        ):
            if "Antiochus X Eusebes" not in entity_name:
                return []
            return [
                {
                    "source": "Antiochus X Eusebes",
                    "target": "Cleopatra IV of Egypt",
                    "relation_type": "mother",
                    "relation_labels": ["mother", "father"],
                    "path_nodes": ["Antiochus X Eusebes", "Cleopatra IV of Egypt", "Ptolemy VI Philometor"],
                    "path_relation_types": ["mother", "father"],
                    "chunk_ids": ["chunk_1"],
                }
            ]

    class FakeChunkStore:
        async def get_documents_by_chunk_ids(self, collection_name, chunk_ids):
            if "chunk_1" not in chunk_ids:
                return []
            return [
                {
                    "chunk_id": "chunk_1",
                    "file_name": "Cleopatra IV of Egypt",
                    "content": "Cleopatra IV of Egypt was the mother of Antiochus X Eusebes.",
                    "summary": "",
                }
            ]

    result = asyncio.run(
        GraphRetriever(client=FakeClient(), chunk_store=FakeChunkStore()).retrieve(
            GENEALOGY_QUERY,
            "kb_genealogy",
            graph_hop_limit=2,
            max_paths_per_entity=5,
        )
    )

    document = result["documents"][0]
    structured_path = result["structured_paths"][0]

    assert structured_path["normalized_relation_types"] == ["mother", "father"]
    assert structured_path["path_length"] == 2
    assert structured_path["genealogy_path_template_match"] == "maternal_grandfather"
    assert document["normalized_relation_types"] == ["mother", "father"]
    assert document["text_unit_support_count"] == 1
    assert document["genealogy_path_template_match"] == "maternal_grandfather"
    assert document["relation_cue_match"] is True


def test_graph_only_noise_stays_in_challenger_pool_and_preserves_standard_top5():
    fusion = RetrievalFusion()
    vector_docs = [
        _doc("v1", "Antiochus X Eusebes", "vector", 0.96),
        _doc("v2", "Laodice of the Sameans", "vector", 0.91),
        _doc("v3", "Ptolemy IX Soter", "vector", 0.89),
        _doc("v4", "Seleucus VI Epiphanes", "vector", 0.86),
        _doc(
            "v5",
            "Cleopatra IV of Egypt",
            "vector",
            0.84,
            content="Cleopatra IV of Egypt was the mother of Antiochus X Eusebes.",
        ),
    ]
    graph_noise = _doc(
        "g1",
        "North Marion High School (West Virginia)",
        "graph",
        0.0,
        content="A noisy nearby family graph neighbor with no supporting genealogy text.",
        metadata={
            "graph_seed_hit_count": 4,
            "graph_support_count": 0,
            "graph_path_count": 5,
            "graph_path_relation_labels": ["school", "nearby_family"],
            "normalized_relation_types": ["school", "nearby_family"],
            "seed_entity_coverage": 1,
            "bridge_entity_coverage": 0,
            "text_unit_support_count": 0,
            "relation_cue_match": False,
            "genealogy_path_template_match": None,
            "path_length": 2,
            "high_degree_entity_noise": True,
            "indirect_family_noise_path": True,
        },
    )

    result = fusion.merge(
        query=GENEALOGY_QUERY,
        documents_by_source={"vector": vector_docs, "graph": [graph_noise]},
        top_k=6,
    )

    assert [doc.file_name for doc in result.documents[:5]] == [doc.file_name for doc in vector_docs]
    noisy = next(doc for doc in result.documents if doc.file_name == "North Marion High School (West Virginia)")
    assert result.fusion_metadata["graph_challenger_pool_size"] == 1
    assert result.fusion_metadata["graph_promotion_allowed"] is False
    assert result.fusion_metadata["graph_promotion_blocked_reason"] == "graph_only_without_text_support"
    assert result.fusion_metadata["final_top5_floor_preserved"] is True
    assert noisy.metadata["graph_only_without_text_support"] is True
    assert noisy.metadata["relation_label_mismatch"] is True


def test_typed_genealogy_graph_candidate_with_text_support_can_promote():
    fusion = RetrievalFusion()
    vector_docs = [
        _doc("v1", "Antiochus X Eusebes", "vector", 0.96),
        _doc("v2", "Laodice of the Sameans", "vector", 0.91),
        _doc("v3", "Ptolemy IX Soter", "vector", 0.89),
        _doc("v4", "Seleucus VI Epiphanes", "vector", 0.86),
        _doc("v5", "Noise Chronicle", "vector", 0.84),
    ]
    graph_candidate = _doc(
        "g1",
        "Cleopatra IV of Egypt",
        "graph",
        0.0,
        content="Cleopatra IV of Egypt was the mother of Antiochus X Eusebes and daughter of Ptolemy VIII Physcon.",
        metadata={
            "graph_seed_hit_count": 3,
            "graph_support_count": 2,
            "graph_path_count": 2,
            "graph_path_relation_labels": ["mother", "father"],
            "normalized_relation_types": ["mother", "father"],
            "seed_entity_coverage": 1,
            "bridge_entity_coverage": 1,
            "text_unit_support_count": 1,
            "relation_cue_match": True,
            "genealogy_path_template_match": "maternal_grandfather",
            "path_length": 2,
        },
    )

    result = fusion.merge(
        query=GENEALOGY_QUERY,
        documents_by_source={"vector": vector_docs, "graph": [graph_candidate]},
        top_k=6,
    )

    top5 = [doc.file_name for doc in result.documents[:5]]
    promoted = next(doc for doc in result.documents if doc.file_name == "Cleopatra IV of Egypt")

    assert "Cleopatra IV of Egypt" in top5
    assert result.fusion_metadata["graph_promotion_allowed"] is True
    assert promoted.metadata["genealogy_path_template_match"] == "maternal_grandfather"
    assert promoted.metadata["graph_only_without_text_support"] is False


def test_non_genealogy_relation_query_does_not_expose_genealogy_floor_metadata():
    fusion = RetrievalFusion()
    vector_docs = [
        _doc("v1", "Ronnie Rocket", "vector", 0.94),
        _doc("v2", "David Lynch", "vector", 0.90),
    ]
    graph_doc = _doc(
        "g1",
        "Jason Moore (director)",
        "graph",
        0.0,
        content="Jason Moore is a director born in Arkansas.",
        metadata={
            "graph_seed_hit_count": 2,
            "graph_support_count": 2,
            "graph_path_count": 2,
            "graph_path_relation_labels": ["director", "birthplace"],
            "normalized_relation_types": ["director", "birthplace"],
            "text_unit_support_count": 1,
            "relation_cue_match": True,
        },
    )

    result = fusion.merge(
        query=BRIDGE_QUERY,
        documents_by_source={"vector": vector_docs, "graph": [graph_doc]},
        top_k=5,
    )

    promoted = next(doc for doc in result.documents if doc.file_name == "Jason Moore (director)")

    assert result.fusion_metadata.get("graph_promotion_blocked_reason") is None
    assert promoted.metadata.get("genealogy_path_template_match") is None
    assert "maternal_grandfather" not in str(result.fusion_metadata)


def test_orchestrator_surfaces_graph_floor_preservation_metadata():
    vector_docs = [
        _doc("v1", "Antiochus X Eusebes", "vector", 0.96),
        _doc("v2", "Laodice of the Sameans", "vector", 0.91),
        _doc("v3", "Ptolemy IX Soter", "vector", 0.89),
        _doc("v4", "Seleucus VI Epiphanes", "vector", 0.86),
        _doc("v5", "Cleopatra IV of Egypt", "vector", 0.84),
    ]
    graph_noise = _doc(
        "g1",
        "North Marion High School (West Virginia)",
        "graph",
        0.0,
        content="No supporting genealogy text.",
        metadata={
            "graph_seed_hit_count": 4,
            "graph_support_count": 0,
            "graph_path_count": 5,
            "graph_path_relation_labels": ["school", "nearby_family"],
            "normalized_relation_types": ["school", "nearby_family"],
            "seed_entity_coverage": 1,
            "bridge_entity_coverage": 0,
            "text_unit_support_count": 0,
            "relation_cue_match": False,
            "genealogy_path_template_match": None,
            "path_length": 2,
            "high_degree_entity_noise": True,
            "indirect_family_noise_path": True,
        },
    )
    orchestrator = RetrievalOrchestrator(
        rag_retriever=_StaticRetriever(_vector_payload(*vector_docs)),
        keyword_retriever=_StaticRetriever({"content": "", "raw_content": "", "documents": []}),
        graph_retriever=_StaticRetriever(_graph_payload(graph_noise)),
        query_expander=_NoRewriteExpander(),
        query_processor=_RelationQueryProcessor(),
        fusion=RetrievalFusion(),
    )

    result = asyncio.run(
        orchestrator.run(
            mode="enhanced_retrieval",
            query=GENEALOGY_QUERY,
            knowledge_ids=["kb_1"],
            retrieval_options={
                "knowledge_capability": "rag_graph",
                "index_health": {"graph": "ready", "community": "not_built"},
                "bm25_available": False,
                "rerank_available": True,
                "top_k": 5,
            },
        )
    )

    metadata = result["metadata"]
    assert metadata["final_top5_floor_preserved"] is True
    assert metadata["graph_challenger_pool_size"] == 1
    assert metadata["graph_promotion_allowed"] is False
    assert metadata["graph_promotion_blocked_reason"] == "graph_only_without_text_support"
