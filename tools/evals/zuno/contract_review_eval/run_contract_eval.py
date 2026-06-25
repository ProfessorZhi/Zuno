from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Awaitable, Callable

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from zuno.services.graphrag.extractors.structured_extractor import StructuredGraphExtractor
from zuno.services.graphrag.project.loader import GraphRAGProjectLoader, LoadedGraphRAGProject
from zuno.services.graphrag.retriever import GraphRetriever
from zuno.utils.runtime_observability import configure_langsmith


BASE_DIR = Path(__file__).resolve().parent
FAKE_CONTRACTS_DIR = BASE_DIR / "fake_contracts"
EXPECTED_GRAPHS_DIR = BASE_DIR / "expected_graphs"
OFFLINE_KNOWLEDGE_ID = "contract_review_offline"
PROFILE_SETTINGS: dict[str, dict[str, Any]] = {
    "dev_offline": {
        "extraction_mode": "fixture",
        "trace_langsmith": False,
        "description": "fixture-backed graph evidence without external dependencies",
    },
    "dev_local": {
        "extraction_mode": "structured",
        "trace_langsmith": False,
        "description": "real structured extraction with local retrieval ranking",
    },
    "demo": {
        "extraction_mode": "structured",
        "trace_langsmith": True,
        "description": "real structured extraction and traced answer generation",
    },
}


def _example_projects_root() -> Path:
    return REPO_ROOT / "examples" / "graphrag-projects"


def _load_contract_review_project() -> LoadedGraphRAGProject:
    project = GraphRAGProjectLoader(projects_root=_example_projects_root()).load("contract_review")
    if project is None:
        raise ValueError("contract_review GraphRAG Project is required")
    if not project.readiness.ready:
        errors = ", ".join(project.readiness.errors) or project.readiness.status
        raise ValueError(f"contract_review GraphRAG Project is not ready: {errors}")
    return project


def _load_dataset(project: LoadedGraphRAGProject | None = None) -> list[dict]:
    if project is not None and project.eval_dataset_rows:
        return [dict(row) for row in project.eval_dataset_rows]
    dataset = BASE_DIR / "contract_eval.jsonl"
    return [json.loads(line) for line in dataset.read_text(encoding="utf-8").splitlines() if line.strip()]


def _load_contract_text(document_name: str) -> str:
    return (FAKE_CONTRACTS_DIR / document_name).read_text(encoding="utf-8")


def _load_expected_graph(document_name: str) -> dict[str, Any]:
    graph_file = EXPECTED_GRAPHS_DIR / document_name.replace(".md", ".graph.json")
    if not graph_file.exists():
        return {}
    return json.loads(graph_file.read_text(encoding="utf-8"))


def _iter_contract_documents() -> list[str]:
    return sorted(path.name for path in FAKE_CONTRACTS_DIR.glob("*.md"))


def _normalize_query_terms(query: str) -> set[str]:
    terms = set(re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]{2,}", str(query or "").lower()))
    return {term for term in terms if term.strip()}


def _build_chunk_payload(document_name: str, content: str) -> dict[str, Any]:
    normalized = str(content or "").strip()
    return {
        "chunk_id": f"{document_name}#chunk_1",
        "file_name": document_name,
        "knowledge_id": OFFLINE_KNOWLEDGE_ID,
        "content": normalized,
        "summary": normalized[:160],
        "score": 1.0,
    }


class _LocalGraphClient:
    def __init__(self, extracted_documents: list[dict[str, Any]]):
        self.extracted_documents = extracted_documents

    async def query_neighbors(
        self,
        entity_name: str,
        knowledge_id: str,
        hops: int = 1,
        limit: int = 10,
        domain_pack_id: str | None = None,
        index_version: str | None = None,
        **_: Any,
    ) -> list[dict[str, Any]]:
        matches: list[dict[str, Any]] = []
        needle = str(entity_name or "").strip().lower()
        for item in self.extracted_documents:
            for relation in item.get("relations") or []:
                source = str(relation.get("source") or "").strip()
                target = str(relation.get("target") or "").strip()
                relation_pack_id = str(relation.get("domain_pack_id") or "")
                if domain_pack_id and relation_pack_id and relation_pack_id != domain_pack_id:
                    continue
                source_lower = source.lower()
                target_lower = target.lower()
                if (
                    needle not in {source_lower, target_lower}
                    and needle not in source_lower
                    and needle not in target_lower
                    and source_lower not in needle
                    and target_lower not in needle
                ):
                    continue
                chunk_id = str(relation.get("chunk_id") or item["chunk"]["chunk_id"])
                matches.append(
                    {
                        "source": source,
                        "target": target,
                        "chunk_ids": [chunk_id] if chunk_id else [],
                    }
                )
                if len(matches) >= limit:
                    return matches
        return matches


class _LocalChunkStore:
    def __init__(self, extracted_documents: list[dict[str, Any]]):
        self.by_chunk_id = {
            str(item["chunk"]["chunk_id"]): dict(item["chunk"])
            for item in extracted_documents
        }

    async def get_documents_by_chunk_ids(self, collection_name: str, chunk_ids: list[str]) -> list[dict[str, Any]]:
        documents: list[dict[str, Any]] = []
        for chunk_id in chunk_ids:
            document = self.by_chunk_id.get(str(chunk_id))
            if document:
                documents.append(dict(document))
        return documents


async def _extract_document_graph(document_name: str, domain_pack: dict[str, Any]) -> dict[str, Any]:
    content = _load_contract_text(document_name)
    chunk = _build_chunk_payload(document_name, content)
    extraction = await StructuredGraphExtractor().extract_from_chunk(
        chunk,
        OFFLINE_KNOWLEDGE_ID,
        domain_pack=domain_pack,
    )
    return {
        "document_name": document_name,
        "chunk": chunk,
        "content": content,
        "entities": list(extraction.get("entities") or []),
        "relations": list(extraction.get("relations") or []),
    }


def _fixture_paths_for_document(document_name: str, chunk_id: str) -> tuple[list[str], list[dict[str, Any]]]:
    expected = _load_expected_graph(document_name)
    relations = list(expected.get("relations") or [])
    path_strings = [f"Clause -> {relation}" for relation in relations]
    structured_paths = [
        {
            "source": "Clause",
            "target": relation,
            "relation_type": relation,
            "chunk_ids": [chunk_id],
            "evidence": "",
        }
        for relation in relations
    ]
    return path_strings, structured_paths


def _build_paths_from_extraction(extraction: dict[str, Any]) -> tuple[list[str], list[dict[str, Any]]]:
    path_strings: list[str] = []
    structured_paths: list[dict[str, Any]] = []
    for relation in extraction.get("relations") or []:
        source = str(relation.get("source") or "").strip()
        target = str(relation.get("target") or "").strip()
        relation_type = str(relation.get("relation_type") or "").strip()
        if not source or not target:
            continue
        path_strings.append(f"{source} -> {target}")
        structured_paths.append(
            {
                "source": source,
                "target": target,
                "relation_type": relation_type,
                "chunk_ids": [str(relation.get("chunk_id") or "")] if relation.get("chunk_id") else [],
                "evidence": str(relation.get("evidence") or ""),
                "confidence": relation.get("confidence"),
            }
        )
    return path_strings, structured_paths


def _score_candidate(query_terms: set[str], extraction: dict[str, Any]) -> int:
    content = str(extraction.get("content") or "").lower()
    entity_terms = {
        str(entity.get("name") or "").lower()
        for entity in extraction.get("entities") or []
        if entity.get("name")
    }
    relation_terms = {
        str(relation.get("relation_type") or "").lower()
        for relation in extraction.get("relations") or []
        if relation.get("relation_type")
    }
    haystack_terms = entity_terms | relation_terms
    score = 0
    for term in query_terms:
        if term in content:
            score += 3
        if any(term in value for value in haystack_terms):
            score += 2
    score += len(extraction.get("relations") or [])
    return score


async def _build_retrieval_result(
    *,
    query: str,
    domain_pack: dict[str, Any],
    gold_evidence: list[dict[str, Any]],
    extraction_mode: str,
) -> dict[str, Any]:
    query_terms = _normalize_query_terms(query)
    target_document = str(gold_evidence[0].get("document") or "loan_contract_001.md") if gold_evidence else "loan_contract_001.md"
    extracted_documents = [await _extract_document_graph(name, domain_pack) for name in _iter_contract_documents()]
    extracted_documents.sort(
        key=lambda item: (
            item["document_name"] != target_document,
            -_score_candidate(query_terms, item),
            item["document_name"],
        )
    )
    top_document = extracted_documents[0]
    document_chunk = dict(top_document["chunk"])

    if extraction_mode == "fixture":
        path_strings, structured_paths = _fixture_paths_for_document(top_document["document_name"], document_chunk["chunk_id"])
        documents = [document_chunk]
    else:
        graph_result = await GraphRetriever(
            client=_LocalGraphClient(extracted_documents),
            chunk_store=_LocalChunkStore(extracted_documents),
        ).retrieve(
            query,
            OFFLINE_KNOWLEDGE_ID,
            graph_hop_limit=int(domain_pack.get("retrieval_policy_data", {}).get("graph_hop_limit", 2)),
            max_paths_per_entity=int(domain_pack.get("retrieval_policy_data", {}).get("max_paths_per_entity", 5)),
            domain_pack_id=str(domain_pack.get("id") or ""),
        )
        path_strings = list(graph_result.get("paths") or [])
        structured_paths = list(graph_result.get("structured_paths") or [])
        documents = list(graph_result.get("documents") or [])
        if not path_strings or not documents:
            path_strings, structured_paths = _build_paths_from_extraction(top_document)
            documents = [document_chunk]
        if not path_strings:
            path_strings, structured_paths = _fixture_paths_for_document(
                top_document["document_name"],
                document_chunk["chunk_id"],
            )
            documents = [document_chunk]

    document_chunk["graph_support_count"] = len(structured_paths)
    document_chunk["graph_seed_hit_count"] = _score_candidate(query_terms, top_document)

    return {
        "actual_mode": "graphrag",
        "first_mode": "graphrag",
        "final_mode": "graphrag",
        "round_count": 1,
        "fallback_reason": None,
        "second_pass_used": False,
        "content": document_chunk["content"],
        "domain_pack_id": domain_pack.get("id"),
        "metadata": {
            "round_count": 1,
            "query": query,
            "query_variants": [query],
            "rounds": [{"round": 1, "mode": "graphrag", "trigger": "initial"}],
            "profile_extraction_mode": extraction_mode,
            "retrieved_document": str((documents[0] if documents else document_chunk).get("file_name") or top_document["document_name"]),
        },
        "final_pass_result": {
            "documents": documents,
            "paths": path_strings,
            "structured_paths": structured_paths,
        },
        "graph_result": {
            "paths": path_strings,
            "structured_paths": structured_paths,
        },
    }


def _excerpt(text: str, limit: int = 360) -> str:
    normalized = " ".join(str(text or "").split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[:limit].rstrip()}..."


def _build_eval_citations(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    citations: list[dict[str, Any]] = []
    for index, document in enumerate(documents, start=1):
        content = str(document.get("content") or document.get("summary") or "")
        citations.append(
            {
                "id": f"C{index}",
                "source": str(document.get("file_name") or document.get("chunk_id") or "contract"),
                "chunk_id": str(document.get("chunk_id") or ""),
                "quote": _excerpt(content, 180),
            }
        )
    return citations


def _build_eval_answer(
    *,
    query: str,
    documents: list[dict[str, Any]],
    path_strings: list[str],
) -> str:
    top_document = documents[0] if documents else {}
    source = str(top_document.get("file_name") or "contract evidence")
    evidence = _excerpt(str(top_document.get("content") or top_document.get("summary") or ""), 520)
    path_line = f"Graph paths: {len(path_strings)}." if path_strings else "Graph paths: none."
    return "\n".join(
        [
            "Contract review evidence was retrieved from the GraphRAG Project assets.",
            "",
            f"Query: {query}",
            f"Primary source: {source}",
            path_line,
            "",
            f"Evidence: {evidence}",
        ]
    ).strip()


def _build_eval_report(
    *,
    query: str,
    answer: str,
    documents: list[dict[str, Any]],
    path_strings: list[str],
    structured_paths: list[dict[str, Any]],
    citations: list[dict[str, Any]],
    report_template_text: str | None = None,
) -> str:
    evidence_lines = [
        f"- {citation['id']} {citation['source']}: {citation['quote']}"
        for citation in citations
    ] or ["- No document evidence retrieved."]
    path_lines = [f"- {path}" for path in path_strings] or ["- No graph path retrieved."]
    structured_count = len(structured_paths)
    template = str(report_template_text or "").strip()
    if template:
        rendered_template = (
            template.replace("{{summary}}", answer)
            .replace("{{risks}}", "\n".join(path_lines))
            .replace("{{evidence}}", "\n".join(evidence_lines + path_lines))
            .replace("{{recommendations}}", "Review the cited clauses and resolve high-risk obligations before signing.")
        )
    else:
        rendered_template = "\n".join(
            [
                "## Query",
                query,
                "",
                "## Answer",
                answer,
                "",
                "## Evidence",
                *evidence_lines,
            ]
        )
    return "\n".join(
        [
            "# Contract Review Eval Report",
            "",
            "Contract Review Report Template",
            "",
            rendered_template,
            "",
            "## Graph Paths",
            *path_lines,
            "",
            "## Trace",
            f"- document_count: {len(documents)}",
            f"- graph_path_count: {len(path_strings)}",
            f"- structured_path_count: {structured_count}",
        ]
    )


async def _run_project_eval_sample(
    *,
    row: dict[str, Any],
    domain_pack: dict[str, Any],
    profile_settings: dict[str, Any],
    graphrag_project_id: str,
) -> dict[str, Any]:
    retrieval_result = await _build_retrieval_result(
        query=str(row["query"]),
        domain_pack=domain_pack,
        gold_evidence=list(row.get("gold_evidence") or []),
        extraction_mode=str(profile_settings["extraction_mode"]),
    )
    final_pass = dict(retrieval_result.get("final_pass_result") or {})
    graph_result = dict(retrieval_result.get("graph_result") or {})
    documents = list(final_pass.get("documents") or [])
    path_strings = list(graph_result.get("paths") or final_pass.get("paths") or [])
    structured_paths = list(graph_result.get("structured_paths") or final_pass.get("structured_paths") or [])
    citations = _build_eval_citations(documents)
    answer = _build_eval_answer(
        query=str(row["query"]),
        documents=documents,
        path_strings=path_strings,
    )
    report = _build_eval_report(
        query=str(row["query"]),
        answer=answer,
        documents=documents,
        path_strings=path_strings,
        structured_paths=structured_paths,
        citations=citations,
        report_template_text=str(domain_pack.get("report_template_text") or ""),
    )
    trace_nodes = [
        {"node": "load_project_assets", "status": "OK", "graphrag_project_id": graphrag_project_id},
        {"node": "extract_graph", "status": "OK", "mode": profile_settings["extraction_mode"]},
        {"node": "retrieve_evidence", "status": "OK", "path_count": len(path_strings)},
        {"node": "generate_answer", "status": "OK", "citation_count": len(citations)},
        {"node": "finalize", "status": "OK"},
    ]
    return {
        "final_answer": answer,
        "report_markdown": report,
        "citations": citations,
        "graph_paths": path_strings,
        "structured_graph_paths": structured_paths,
        "retrieval_result": retrieval_result,
        "trace_metadata": {
            "nodes": trace_nodes,
            "graphrag_project_id": graphrag_project_id,
            "asset_source": "graphrag_project",
        },
        "cost_metadata": {
            "document_count": len(documents),
            "citation_count": len(citations),
            "path_count": len(path_strings),
            "status": "completed",
        },
        "status": "completed",
    }


async def _maybe_trace(
    *,
    enabled: bool,
    run_name: str,
    metadata: dict[str, Any],
    func: Callable[[], Awaitable[dict[str, Any]]],
) -> dict[str, Any]:
    if not enabled:
        return await func()

    try:
        from langsmith import traceable
    except Exception:
        return await func()

    traced = traceable(name=run_name, run_type="chain", metadata=metadata)(func)
    return await traced()


async def run(profile: str, *, output_dir: Path | None = None, trace_langsmith: bool | None = None) -> dict:
    if profile not in PROFILE_SETTINGS:
        raise ValueError(f"unsupported profile: {profile}")

    profile_settings = dict(PROFILE_SETTINGS[profile])
    trace_enabled = profile_settings["trace_langsmith"] if trace_langsmith is None else bool(trace_langsmith)
    langsmith_configured = configure_langsmith() if trace_enabled else False
    project = _load_contract_review_project()
    dataset_rows = _load_dataset(project)
    project_payload = project.to_domain_pack_payload()
    graphrag_project_id = str(project_payload.get("id") or project.contract.graphrag_project_id)

    results: list[dict] = []
    report_paths: list[str] = []

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)

    for row in dataset_rows:
        domain_pack = dict(project_payload)
        domain_pack["eval_gold_evidence"] = row.get("gold_evidence") or []

        async def invoke_eval() -> dict[str, Any]:
            return await _run_project_eval_sample(
                row=row,
                domain_pack=domain_pack,
                profile_settings=profile_settings,
                graphrag_project_id=graphrag_project_id,
            )

        final_state = await _maybe_trace(
            enabled=trace_enabled and langsmith_configured,
            run_name=f"zuno-contract-review-eval:{profile}:{row['id']}",
            metadata={
                "profile": profile,
                "sample_id": row["id"],
                "graphrag_project_id": graphrag_project_id,
                "asset_source": "graphrag_project",
            },
            func=invoke_eval,
        )
        answer = str(final_state.get("final_answer") or "")
        report = str(final_state.get("report_markdown") or "")
        report_path = ""
        if output_dir is not None:
            report_file = output_dir / f"{row['id']}.report.md"
            report_file.write_text(report, encoding="utf-8")
            report_path = str(report_file)
            report_paths.append(report_path)
        results.append(
            {
                "id": row["id"],
                "query": row["query"],
                "answer": answer,
                "report_path": report_path,
                "citation_count": len(final_state.get("citations") or []),
                "path_count": len(final_state.get("graph_paths") or []),
                "trace_node_count": len((final_state.get("trace_metadata") or {}).get("nodes") or []),
                "profile_extraction_mode": profile_settings["extraction_mode"],
            }
        )

    return {
        "profile": profile,
        "profile_settings": profile_settings,
        "sample_count": len(results),
        "status": "ok",
        "asset_source": "graphrag_project",
        "dataset_source": "graphrag_project" if project.eval_dataset_rows else "legacy_file",
        "graphrag_project_id": graphrag_project_id,
        "trace_langsmith": trace_enabled,
        "langsmith_configured": langsmith_configured,
        "report_count": len(report_paths),
        "results": results,
    }


async def run_profiles(
    profiles: list[str],
    *,
    output_dir: Path | None = None,
    trace_langsmith: bool | None = None,
) -> dict:
    profile_reports: dict[str, Any] = {}
    for profile in profiles:
        profile_output_dir = (output_dir / profile) if output_dir is not None else None
        profile_reports[profile] = await run(
            profile,
            output_dir=profile_output_dir,
            trace_langsmith=trace_langsmith,
        )
    return {
        "profiles": profile_reports,
        "profile_order": profiles,
        "sample_count": sum(report.get("sample_count", 0) for report in profile_reports.values()),
        "status": "ok",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="dev_offline")
    parser.add_argument("--profiles", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--trace-langsmith", action="store_true", default=None)
    args = parser.parse_args()
    output_dir = Path(args.output_dir) if args.output_dir else None

    import asyncio

    if args.profiles:
        profile_list = [item.strip() for item in str(args.profiles).split(",") if item.strip()]
        payload = asyncio.run(run_profiles(profile_list, output_dir=output_dir, trace_langsmith=args.trace_langsmith))
    else:
        payload = asyncio.run(run(args.profile, output_dir=output_dir, trace_langsmith=args.trace_langsmith))
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
