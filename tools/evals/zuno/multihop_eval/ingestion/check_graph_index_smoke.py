from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[5]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from zuno.services.runtime_registry import get_local_runtime_settings
from zuno.services.graphrag.client import Neo4jClient

from tools.evals.zuno.multihop_eval.run_real_runtime_eval import (
    _read_jsonl,
    build_chunks_from_corpus,
)
from tools.evals.zuno.rag_eval.run_stackless_local_eval import _build_local_graph_retriever


def resolve_default_corpus_path(dataset: str) -> Path:
    normalized = str(dataset or "").strip().lower()
    if normalized not in {"hotpotqa", "twowiki", "musique"}:
        raise ValueError(f"Unsupported dataset: {dataset}")
    return REPO_ROOT / "data" / "evals" / "multihop" / "corpus" / normalized / "dev_sample50_corpus.jsonl"


async def build_graph_index_smoke(
    *,
    dataset: str,
    knowledge_id: str,
    questions_path: Path,
    corpus_path: Path,
    limit: int,
) -> dict[str, Any]:
    selected_questions = _read_jsonl(questions_path)[: max(int(limit), 0)]
    selected_question_ids = {str(item.get("id") or "") for item in selected_questions}
    corpus_rows = [
        row
        for row in _read_jsonl(corpus_path)
        if str(row.get("question_id") or "") in selected_question_ids
    ]
    runtime_settings = get_local_runtime_settings(knowledge_id)
    persisted_graph_runtime_available = runtime_settings is not None and bool(runtime_settings.get("graph_retriever"))
    persisted_entity_count = None
    persisted_relation_count = None
    persisted_backlink_count = None
    mismatch_reason = None
    if Neo4jClient.is_enabled():
        try:
            persisted_counts = await Neo4jClient().count_knowledge_graph(knowledge_id, status="active")
            persisted_entity_count = persisted_counts["entity_count"]
            persisted_relation_count = persisted_counts["relation_count"]
            persisted_backlink_count = persisted_counts["backlink_count"]
            if persisted_entity_count == 0 and persisted_relation_count == 0:
                mismatch_reason = "persisted_graph_empty_for_eval_knowledge"
        except Exception as exc:
            mismatch_reason = f"persisted_graph_query_failed: {exc}"
    else:
        mismatch_reason = "neo4j_disabled_or_unavailable"
    chunks = build_chunks_from_corpus(corpus_rows=corpus_rows, knowledge_id=knowledge_id)
    graph_retriever = await _build_local_graph_retriever(chunks)

    extracted_documents = list(getattr(getattr(graph_retriever, "client", None), "extracted_documents", []) or [])
    entity_count = sum(len(item.get("entities") or []) for item in extracted_documents)
    relation_count = sum(len(item.get("relations") or []) for item in extracted_documents)
    backlink_count = sum(
        1
        for item in extracted_documents
        for relation in (item.get("relations") or [])
        if relation.get("chunk_id")
    )

    question_reports: list[dict[str, Any]] = []
    for item in selected_questions:
        query = str(item.get("question") or "")
        seed_entities = graph_retriever._extract_query_seeds(query)  # type: ignore[attr-defined]
        graph_worthy = graph_retriever._is_graph_worthy_query(query, seed_entities)  # type: ignore[attr-defined]
        result = await graph_retriever.retrieve(query, knowledge_id)
        path_count = len(result.get("paths") or [])
        entities = list(result.get("entities") or [])
        status: list[str] = []
        if not persisted_graph_runtime_available:
            status.append("graph_index_missing")
        if not seed_entities:
            status.append("seed_entity_empty")
        if path_count == 0:
            status.append("graph_path_empty")
        question_reports.append(
            {
                "question_id": str(item.get("id") or ""),
                "question": query,
                "seed_entities": seed_entities,
                "seed_entity_count": len(seed_entities),
                "graph_worthy": graph_worthy,
                "entity_count": len(entities),
                "path_count": path_count,
                "status": status,
            }
        )

    return {
        "execution_mode": "graph_index_smoke",
        "dataset": str(dataset).strip().lower(),
        "knowledge_id": knowledge_id,
        "sample_limit": len(selected_questions),
        "persisted_graph_runtime_available": persisted_graph_runtime_available,
        "graph_index_missing": not persisted_graph_runtime_available,
        "corpus_document_count": len(corpus_rows),
        "chunk_count": len(chunks),
        "entity_count": entity_count,
        "relation_count": relation_count,
        "chunk_backlink_count": backlink_count,
        "persisted_entity_count": persisted_entity_count,
        "persisted_relation_count": persisted_relation_count,
        "persisted_backlink_count": persisted_backlink_count,
        "local_rebuilt_entity_count": entity_count,
        "local_rebuilt_relation_count": relation_count,
        "mismatch_reason": mismatch_reason,
        "questions": question_reports,
        "notes": [
            "Current multihop real runtime runner clears local runtime registration after each run.",
            "This smoke therefore distinguishes persisted graph runtime availability from local eval graph artifacts rebuilt from corpus rows.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Check GraphRAG graph activation smoke for eval corpus.")
    parser.add_argument("--dataset", required=True, choices=["hotpotqa", "twowiki", "musique"])
    parser.add_argument("--knowledge-id", required=True)
    parser.add_argument("--questions", required=True, type=Path)
    parser.add_argument("--corpus", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    corpus_path = args.corpus or resolve_default_corpus_path(args.dataset)
    report = asyncio.run(
        build_graph_index_smoke(
            dataset=args.dataset,
            knowledge_id=args.knowledge_id,
            questions_path=args.questions,
            corpus_path=corpus_path,
            limit=args.limit,
        )
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "execution_mode": report["execution_mode"],
                "graph_index_missing": report["graph_index_missing"],
                "entity_count": report["entity_count"],
                "relation_count": report["relation_count"],
                "output": str(args.output),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
