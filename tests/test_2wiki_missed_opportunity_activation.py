import asyncio
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src" / "backend"))

from zuno.services.graphrag.retriever import GraphRetriever
from zuno.services.retrieval.models import FusionResult, RetrievedDocument
from zuno.services.retrieval.orchestrator import RetrievalOrchestrator
from zuno.services.retrieval.planner import RetrievalPlanner
from zuno.services.retrieval.retrievers import QueryProcessor


def _doc(
    chunk_id: str,
    file_name: str,
    score: float,
    *,
    source_type: str = "vector",
    matched_by: list[str] | None = None,
    metadata: dict | None = None,
):
    merged_metadata = {"matched_by": list(matched_by or [source_type])}
    merged_metadata.update(dict(metadata or {}))
    return RetrievedDocument(
        chunk_id=chunk_id,
        knowledge_id="kb_1",
        file_id=file_name,
        file_name=file_name,
        content=file_name,
        summary="",
        score=score,
        normalized_score=None,
        source_type=source_type,
        source_backend=source_type,
        retrieval_reason=source_type,
        metadata=merged_metadata,
    )


class _StaticExpander:
    def __init__(self, rewrites: list[str] | None = None):
        self.rewrites = list(rewrites or [])

    async def expand(self, query: str):
        return [query, *self.rewrites]


class _MappingRetriever:
    def __init__(self, mapping):
        self.mapping = mapping

    async def retrieve(self, query, knowledge_ids, options=None):
        docs = list(self.mapping.get(query, []))
        return {
            "content": "\n".join(doc.file_name for doc in docs),
            "raw_content": "\n".join(doc.file_name for doc in docs),
            "documents": [doc.to_dict() for doc in docs],
            "document_count": len(docs),
            "requested_top_k": (options or {}).get("top_k"),
            "top_score": max((doc.score for doc in docs), default=0.0),
            "score_threshold": (options or {}).get("score_threshold"),
        }


class _GraphRetrieverStub:
    def __init__(self, payload):
        self.payload = payload

    def _extract_query_seeds(self, query):
        return GraphRetriever._extract_query_seeds(query)

    def _is_graph_worthy_query(self, query, seed_entities):
        return GraphRetriever._is_graph_worthy_query(query, seed_entities)

    async def retrieve(self, query, knowledge_ids, options=None):
        return self.payload


class _RequeryAwareFusion:
    def __init__(self, *, use_requery_docs: bool):
        self.use_requery_docs = use_requery_docs

    def merge(self, *, query: str, documents_by_source, top_k=None):
        vector_docs = list(documents_by_source.get("vector") or [])
        requery_docs = list(documents_by_source.get("requery") or [])
        docs = list(vector_docs)
        if self.use_requery_docs and requery_docs:
            docs = [vector_docs[0], requery_docs[0], *vector_docs[1:]]
        if top_k is not None:
            docs = docs[:top_k]
        return FusionResult(
            documents=docs,
            dropped_documents=[],
            fusion_metadata={"strategy": "baseline_preserving"},
            rerank_metadata={},
        )


class _StaticFusion:
    def __init__(self, docs, *, fusion_metadata=None):
        self.docs = list(docs)
        self.fusion_metadata = dict(fusion_metadata or {"strategy": "baseline_preserving"})

    def merge(self, *, query: str, documents_by_source, top_k=None):
        docs = list(self.docs)
        if top_k is not None:
            docs = docs[:top_k]
        return FusionResult(
            documents=docs,
            dropped_documents=[],
            fusion_metadata=dict(self.fusion_metadata),
            rerank_metadata={},
        )


def test_genealogy_bridge_pattern_triggers_graph_activation_reason():
    query = "When did John V, Prince Of Anhalt-Zerbst's father die?"
    orchestrator = RetrievalOrchestrator(
        rag_retriever=_MappingRetriever(
            {
                query: [
                    _doc("v1", "John V, Prince of Anhalt-Zerbst", 0.95),
                    _doc("v2", "Prince of Anhalt-Zerbst", 0.82),
                ]
            }
        ),
        keyword_retriever=_MappingRetriever({}),
        graph_retriever=_GraphRetrieverStub(
            {
                "content": "graph evidence",
                "raw_content": "graph evidence",
                "documents": [
                    _doc(
                        "g1",
                        "Ernest I, Prince of Anhalt-Dessau",
                        0.88,
                        source_type="graph",
                        matched_by=["graph"],
                        metadata={"graph_path_relation_labels": ["father", "death"]},
                    ).to_dict()
                ],
                "entities": [{"name": "John V, Prince Of Anhalt-Zerbst"}],
                "paths": [{"source": "John V, Prince Of Anhalt-Zerbst", "target": "Ernest I, Prince of Anhalt-Dessau"}],
            }
        ),
        query_expander=_StaticExpander(),
        query_processor=QueryProcessor(),
        planner=RetrievalPlanner(enable_keyword_recall=True),
    )

    result = asyncio.run(
        orchestrator.run(
            mode="enhanced_retrieval",
            query=query,
            knowledge_ids=["kb_1"],
                retrieval_options={
                    "knowledge_capability": "rag_graph",
                    "index_health": {"graph": "ready", "community": "not_built"},
                    "bm25_available": False,
                    "rerank_available": True,
                    "top_k": 6,
                },
            )
        )

    metadata = result["metadata"]

    assert metadata["route_selection_reason"] == "relation_question"
    assert metadata["graph_route_attempted"] is True
    assert metadata["graph_activation_reason"] == "genealogy_bridge_pattern"
    assert metadata["enhanced_activation_reason"] == "genealogy_bridge_pattern"
    assert metadata["requery_activation_reason"] is None


def test_born_later_comparison_pattern_triggers_graph_activation_reason():
    query = "Which film has the director who was born later, El Extraño Viaje or Love In Pawn?"
    orchestrator = RetrievalOrchestrator(
        rag_retriever=_MappingRetriever(
            {
                query: [
                    _doc("v1", "El Extraño Viaje", 0.95),
                    _doc("v2", "Love in Pawn", 0.84),
                ]
            }
        ),
        keyword_retriever=_MappingRetriever({}),
        graph_retriever=_GraphRetrieverStub(
            {
                "content": "graph comparison evidence",
                "raw_content": "graph comparison evidence",
                "documents": [
                    _doc(
                        "g1",
                        "Fernando Fernán Gómez",
                        0.87,
                        source_type="graph",
                        matched_by=["graph"],
                        metadata={"graph_path_relation_labels": ["director", "birthplace"]},
                    ).to_dict()
                ],
                "entities": [{"name": "El Extraño Viaje"}],
                "paths": [{"source": "El Extraño Viaje", "target": "Fernando Fernán Gómez"}],
            }
        ),
        query_expander=_StaticExpander(),
        query_processor=QueryProcessor(),
        planner=RetrievalPlanner(enable_keyword_recall=True),
    )

    result = asyncio.run(
        orchestrator.run(
            mode="enhanced_retrieval",
            query=query,
            knowledge_ids=["kb_1"],
            retrieval_options={
                "knowledge_capability": "rag_graph",
                "index_health": {"graph": "ready", "community": "not_built"},
                "bm25_available": False,
                "rerank_available": True,
                "top_k": 6,
            },
        )
    )

    metadata = result["metadata"]

    assert metadata["route_selection_reason"] == "relation_question"
    assert metadata["graph_route_attempted"] is True
    assert metadata["graph_activation_reason"] == "comparison_bridge_pattern"


def test_genealogy_guardrail_preserves_standard_floor_and_records_block_reason():
    query = "Who is the maternal grandfather of Antiochus X Eusebes?"
    vector_docs = [
        _doc("v1", "Antiochus X Eusebes", 0.96),
        _doc("v2", "Laodice of the Sameans", 0.90),
        _doc("v3", "Albert III, Prince of Anhalt-Zerbst", 0.85),
        _doc("v4", "Fujiwara no Nagara", 0.83),
        _doc("v5", "Cleopatra IV of Egypt", 0.82, metadata={"matched_by": ["vector"]}),
    ]
    graph_payload = {
        "content": "graph evidence",
        "raw_content": "graph evidence",
        "documents": [
            _doc(
                "g1",
                "North Marion High School (West Virginia)",
                0.0,
                source_type="graph",
                matched_by=["graph"],
                metadata={
                    "graph_seed_hit_count": 4,
                    "graph_support_count": 12,
                    "graph_path_count": 8,
                    "graph_path_relation_labels": ["school", "nearby_family"],
                    "indirect_family_noise_path": True,
                },
            ).to_dict()
        ],
        "entities": [{"name": "Antiochus X Eusebes"}],
        "paths": [{"source": "Antiochus X Eusebes", "target": "North Marion High School"}],
    }
    orchestrator = RetrievalOrchestrator(
        rag_retriever=_MappingRetriever({query: vector_docs}),
        keyword_retriever=_MappingRetriever({}),
        graph_retriever=_GraphRetrieverStub(graph_payload),
        query_expander=_StaticExpander(),
        query_processor=QueryProcessor(),
        planner=RetrievalPlanner(enable_keyword_recall=True),
        fusion=_StaticFusion(
            [
                _doc("v1", "Antiochus X Eusebes", 0.96),
                _doc("v2", "Laodice of the Sameans", 0.90),
                _doc("v3", "Albert III, Prince of Anhalt-Zerbst", 0.85),
                _doc("v4", "Fujiwara no Nagara", 0.83),
                _doc("v5", "Cleopatra IV of Egypt", 0.82),
                _doc(
                    "g1",
                    "North Marion High School (West Virginia)",
                    0.10,
                    source_type="graph",
                    matched_by=["graph"],
                    metadata={
                        "genealogy_promotion_blocked_reason": "genealogy_chain_protection",
                        "genealogy_promotion_allowed": False,
                        "noisy_genealogy_graph_only": True,
                    },
                ),
            ],
            fusion_metadata={
                "strategy": "baseline_preserving",
                "genealogy_bridge_question": True,
            },
        ),
    )

    result = asyncio.run(
        orchestrator.run(
            mode="enhanced_retrieval",
            query=query,
            knowledge_ids=["kb_1"],
            retrieval_options={
                "knowledge_capability": "rag_graph",
                "index_health": {"graph": "ready", "community": "not_built"},
                "bm25_available": False,
                "rerank_available": True,
                "top_k": 6,
            },
        )
    )

    metadata = result["metadata"]
    top5 = [doc["file_name"] for doc in result["final_pass_result"]["documents"][:5]]

    assert "Cleopatra IV of Egypt" in top5
    assert metadata["candidate_blocked_reason"] == "genealogy_chain_protection"
    assert metadata["floor_preserved_reason"] == "standard_floor_chain_protection"


def test_standard_floor_gap_can_trigger_requery_activation_reason():
    query = "Ralph Hefferline was a psychology professor at a university that is located in what city?"
    rewrite = "What city is Columbia University in?"
    orchestrator = RetrievalOrchestrator(
        rag_retriever=_MappingRetriever(
            {
                query: [
                    _doc("v1", "Ralph Hefferline", 0.95),
                    _doc("v2", "Virginia Commonwealth University", 0.82),
                ],
                rewrite: [
                    _doc("r1", "Columbia University", 0.88, matched_by=["requery"], metadata={"requery_confidence_score": 3})
                ],
            }
        ),
        keyword_retriever=_MappingRetriever({}),
        graph_retriever=_GraphRetrieverStub({"content": "", "raw_content": "", "documents": [], "entities": [], "paths": []}),
        query_expander=_StaticExpander([rewrite]),
        query_processor=QueryProcessor(),
        planner=RetrievalPlanner(enable_keyword_recall=True),
        fusion=_RequeryAwareFusion(use_requery_docs=True),
    )

    result = asyncio.run(
        orchestrator.run(
            mode="enhanced_retrieval",
            query=query,
            knowledge_ids=["kb_1"],
            retrieval_options={
                "knowledge_capability": "rag_graph",
                "index_health": {"graph": "unavailable", "community": "not_built"},
                "bm25_available": False,
                "rerank_available": True,
                "top_k": 5,
            },
        )
    )

    metadata = result["metadata"]

    assert metadata["requery_used"] is True
    assert metadata["requery_activation_reason"] == "bridge_attribute_pattern"
    assert metadata["enhanced_activation_reason"] == "bridge_attribute_pattern"
    assert metadata["missed_opportunity_trigger_reason"] is None


def test_simple_fact_query_keeps_activation_metadata_quiet():
    query = "What is Buck-Tick?"
    orchestrator = RetrievalOrchestrator(
        rag_retriever=_MappingRetriever({query: [_doc("v1", "Buck-Tick", 0.95), _doc("v2", "Atsushi Sakurai", 0.83)]}),
        keyword_retriever=_MappingRetriever({}),
        graph_retriever=_GraphRetrieverStub({"content": "", "raw_content": "", "documents": [], "entities": [], "paths": []}),
        query_expander=_StaticExpander(["Explain Buck-Tick."]),
        query_processor=QueryProcessor(),
        planner=RetrievalPlanner(enable_keyword_recall=True),
        fusion=_RequeryAwareFusion(use_requery_docs=False),
    )

    result = asyncio.run(
        orchestrator.run(
            mode="enhanced_retrieval",
            query=query,
            knowledge_ids=["kb_1"],
            retrieval_options={
                "knowledge_capability": "rag_graph",
                "index_health": {"graph": "unavailable", "community": "not_built"},
                "bm25_available": False,
                "rerank_available": True,
                "top_k": 5,
            },
        )
    )

    metadata = result["metadata"]

    assert metadata["graph_activation_reason"] is None
    assert metadata["requery_activation_reason"] is None
    assert metadata["missed_opportunity_trigger_reason"] is None
    assert metadata["candidate_blocked_reason"] is None
