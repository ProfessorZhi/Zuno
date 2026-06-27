import asyncio
from pathlib import Path


def _contract_review_query_policy() -> dict:
    from zuno.services.graphrag.project.loader import GraphRAGProjectLoader

    projects_root = Path(__file__).resolve().parents[2] / "examples" / "graphrag-projects"
    project = GraphRAGProjectLoader(projects_root=projects_root).load("contract_review")
    return dict(project.settings["retrieval_policy"])


def test_graph_retriever_handles_contract_review_chinese_query():
    from zuno.services.graphrag.retriever import GraphRetriever

    class FakeClient:
        async def query_neighbors(
            self,
            entity_name,
            knowledge_id,
            hops=1,
            limit=10,
            domain_pack_id=None,
            **_kwargs,
        ):
            if entity_name != "违约责任":
                return []
            return [
                {
                    "source": "第八条 违约责任",
                    "target": "违约责任",
                    "chunk_ids": ["contract_chunk_1"],
                }
            ]

    class FakeChunkStore:
        async def get_documents_by_chunk_ids(self, collection_name, chunk_ids):
            return [
                {
                    "chunk_id": "contract_chunk_1",
                    "file_name": "loan_contract_001.md",
                    "content": "第八条 违约责任：借款人未按约定期限还款的，应承担违约责任。",
                    "summary": "",
                }
            ]

    result = asyncio.run(
        GraphRetriever(client=FakeClient(), chunk_store=FakeChunkStore()).retrieve(
            "这份合同是否约定了违约责任？",
            "k_contract",
            graph_hop_limit=2,
            max_paths_per_entity=5,
            domain_pack_id="contract_review",
            query_policy=_contract_review_query_policy(),
        )
    )

    assert result["paths"] == ["第八条 违约责任 -> 违约责任"]
    assert result["structured_paths"][0]["source"] == "第八条 违约责任"
    assert result["documents"][0]["chunk_id"] == "contract_chunk_1"
