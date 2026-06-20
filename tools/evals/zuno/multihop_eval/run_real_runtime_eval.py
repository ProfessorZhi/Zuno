from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from copy import deepcopy
from pathlib import Path
from typing import Any
from uuid import uuid4

import yaml


REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from zuno.api.services.knowledge import DEFAULT_KNOWLEDGE_CONFIG
from zuno.database.dao.llm import LLMDao
from zuno.schema.chunk import ChunkModel
from zuno.services.rag.handler import RagHandler
from zuno.services.runtime_registry import clear_local_runtime_settings, register_local_runtime_settings
from zuno.settings import initialize_app_settings, resolve_app_config_path
from zuno.utils.helpers import get_provider_from_model

from tools.evals.zuno.multihop_eval.metrics import aggregate_question_metrics, compute_question_metrics
from tools.evals.zuno.rag_eval.run_stackless_local_eval import _build_local_graph_retriever


DEFAULT_OUTPUT_ROOT = REPO_ROOT / "reports" / "evals" / "multihop" / "real_runtime"
SUPPORTED_DATASETS = {"hotpotqa", "twowiki", "musique"}
SUPPORTED_MODES = {"baseline_rag", "local_graphrag", "deep_graphrag"}
SUPPORTED_ROUTE_POLICIES = {"auto", "force_graph", "force_deep"}
MODE_TO_RUNTIME = {
    "baseline_rag": "rag",
    "local_graphrag": "local_graphrag",
    "deep_graphrag": "rag_graph_deep",
}
MODE_TO_CAPABILITY = {
    "baseline_rag": "rag",
    "local_graphrag": "rag_graph",
    "deep_graphrag": "rag_graph",
}
MODEL_SLOT_BY_TYPE = {
    "LLM": "conversation_model",
    "Embedding": "embedding",
    "Rerank": "rerank",
}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _build_temp_config() -> Path:
    source_path = resolve_app_config_path()
    data = yaml.safe_load(source_path.read_text(encoding="utf-8")) or {}
    rag = data.setdefault("rag", {})
    rag["enable_elasticsearch"] = False
    vector_db = rag.setdefault("vector_db", {})
    vector_db["mode"] = "chroma"
    temp_dir = REPO_ROOT / ".local" / "tmp" / f"multihop-real-runtime-{uuid4().hex[:8]}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_config = temp_dir / "config.yaml"
    temp_config.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return temp_config


def resolve_runtime_mode(mode: str) -> str:
    normalized = str(mode or "").strip().lower()
    if normalized not in MODE_TO_RUNTIME:
        raise ValueError(f"Unsupported mode: {mode}")
    return MODE_TO_RUNTIME[normalized]


def resolve_route_policy(route_policy: str | None) -> str:
    normalized = str(route_policy or "auto").strip().lower() or "auto"
    if normalized not in SUPPORTED_ROUTE_POLICIES:
        raise ValueError(f"Unsupported route policy: {route_policy}")
    return normalized


def resolve_eval_profile(*, profile_file: Path, profile_name: str) -> dict[str, Any]:
    payload = json.loads(profile_file.read_text(encoding="utf-8"))
    if profile_name not in payload:
        raise ValueError(f"eval profile not found: {profile_name}")
    profile = dict(payload[profile_name] or {})
    profile["profile_name"] = profile_name
    profile["profile_file"] = str(profile_file)
    return profile


def _normalize_llm_type(value: str | None) -> str:
    if value == "Reranker":
        return "Rerank"
    return str(value or "")


async def _resolve_model_config_by_name(*, model_name: str, llm_type: str) -> dict[str, Any]:
    rows = await LLMDao.get_all_llm()
    normalized_type = _normalize_llm_type(llm_type)
    exact = [
        row
        for row in rows
        if str(row.model or "").strip() == str(model_name).strip()
        and _normalize_llm_type(getattr(row, "llm_type", None)) == normalized_type
    ]
    if not exact:
        raise ValueError(f"model `{model_name}` with type `{normalized_type}` not found in registry")

    preferred_slot = MODEL_SLOT_BY_TYPE.get(normalized_type)
    if preferred_slot:
        slot_matches = [row for row in exact if str(getattr(row, "model_slot", "") or "") == preferred_slot]
        if len(slot_matches) == 1:
            selected = slot_matches[0]
        elif len(exact) == 1:
            selected = exact[0]
        else:
            raise ValueError(f"model `{model_name}` with type `{normalized_type}` is ambiguous in registry")
    elif len(exact) == 1:
        selected = exact[0]
    else:
        raise ValueError(f"model `{model_name}` with type `{normalized_type}` is ambiguous in registry")

    return {
        "llm_id": getattr(selected, "llm_id", None),
        "model_name": selected.model,
        "api_key": selected.api_key,
        "base_url": selected.base_url,
        "provider": selected.provider or get_provider_from_model(selected.model),
        "llm_type": _normalize_llm_type(selected.llm_type),
        "model_slot": selected.model_slot,
    }


async def resolve_profile_model_configs(profile: dict[str, Any]) -> dict[str, Any]:
    conversation = await _resolve_model_config_by_name(
        model_name=str(profile.get("conversation_model") or "").strip(),
        llm_type="LLM",
    )
    text_embedding = await _resolve_model_config_by_name(
        model_name=str(profile.get("text_embedding_model") or "").strip(),
        llm_type="Embedding",
    )
    rerank = await _resolve_model_config_by_name(
        model_name=str(profile.get("rerank_model") or "").strip(),
        llm_type="Rerank",
    )
    return {
        "conversation_model": conversation,
        "text_embedding_config": text_embedding,
        "rerank_config": rerank,
        "model_profile": {
            "conversation_model": conversation["model_name"],
            "text_embedding_model": text_embedding["model_name"],
            "rerank_model": rerank["model_name"],
        },
    }


def _build_runtime_knowledge_config(*, mode: str, profile: dict[str, Any], top_k: int) -> dict[str, Any]:
    config = deepcopy(DEFAULT_KNOWLEDGE_CONFIG)
    config["index_capability"] = MODE_TO_CAPABILITY[mode]
    config["retrieval_settings"]["default_mode"] = "rag" if mode == "baseline_rag" else "rag_graph_deep"
    config["retrieval_settings"]["profile"] = str(profile.get("profile_name") or "auto")
    config["retrieval_settings"]["top_k"] = int(top_k)
    config["retrieval_settings"]["rerank_top_k"] = int((profile.get("retrieval") or {}).get("rerank_top_k") or min(top_k, 5))
    config["retrieval_settings"]["rerank_enabled"] = bool((profile.get("retrieval") or {}).get("rerank_enabled", True))
    config["retrieval_settings"]["score_threshold"] = (profile.get("retrieval") or {}).get("score_threshold")
    config["retrieval_settings"]["graph_hop_limit"] = int((profile.get("retrieval") or {}).get("graph_hop_limit") or 2)
    config["retrieval_settings"]["max_paths_per_entity"] = int((profile.get("retrieval") or {}).get("max_paths_per_entity") or 5)
    config["index_settings"]["vector_backend"] = "chroma"
    config["index_settings"]["image_indexing_mode"] = "text_only"
    config["graph_index_settings"]["health_status"] = "ready" if config["index_capability"] == "rag_graph" else "unavailable"
    config["graph_index_settings"]["graph_index_status"] = "ready" if config["index_capability"] == "rag_graph" else "not_built"
    config["graph_index_settings"]["community_detection_status"] = "not_built"
    config["graph_index_settings"]["community_report_status"] = "not_built"
    return config


def build_runtime_retrieval_options(*, top_k: int, profile_name: str, route_policy: str) -> dict[str, Any]:
    resolved_route_policy = resolve_route_policy(route_policy)
    options = {
        "top_k": top_k,
        "requested_profile": profile_name,
        "trace_policy": {"enabled": True},
        "route_policy": resolved_route_policy,
    }
    if resolved_route_policy != "auto":
        options["eval_only_route_override"] = resolved_route_policy
    return options


def _doc_identity(document: dict[str, Any]) -> str:
    return str(document.get("doc_id") or document.get("title") or "").strip()


def build_gold_doc_ids(question_row: dict[str, Any]) -> list[str]:
    by_title = {
        str(document.get("title") or "").strip(): _doc_identity(document)
        for document in (question_row.get("documents") or [])
    }
    gold_ids: list[str] = []
    for item in question_row.get("gold_support") or []:
        title = str(item.get("title") or "").strip()
        doc_id = by_title.get(title) or title
        if doc_id and doc_id not in gold_ids:
            gold_ids.append(doc_id)
    return gold_ids


def build_chunks_from_corpus(*, corpus_rows: list[dict[str, Any]], knowledge_id: str) -> list[ChunkModel]:
    chunks: list[ChunkModel] = []
    for index, row in enumerate(corpus_rows):
        doc_id = str(row.get("doc_id") or row.get("title") or f"doc-{index}")
        title = str(row.get("title") or doc_id)
        text = str(row.get("text") or "").strip()
        if not text:
            continue
        chunks.append(
            ChunkModel(
                chunk_id=f"{doc_id}::0",
                content=text,
                file_id=doc_id,
                file_name=title,
                update_time=str(row.get("metadata", {}).get("update_time") or ""),
                knowledge_id=knowledge_id,
                summary=title,
                modality="text",
                source_url=f"multihop://{row.get('dataset') or 'dataset'}/{doc_id}",
            )
        )
    return chunks


def _filter_corpus_for_questions(corpus_rows: list[dict[str, Any]], question_ids: set[str]) -> list[dict[str, Any]]:
    return [row for row in corpus_rows if str(row.get("question_id") or "") in question_ids]


def extract_route_diagnostics(
    *,
    runtime_result: dict[str, Any] | None,
    fallback: bool,
    fallback_reason: str | None,
) -> tuple[dict[str, Any], list[str]]:
    metadata = dict((runtime_result or {}).get("metadata") or {})
    first_pass = dict((runtime_result or {}).get("first_pass_result") or {})
    final_pass = dict((runtime_result or {}).get("final_pass_result") or {})
    rounds = list(metadata.get("rounds") or [])
    primary_pass = first_pass or final_pass

    retriever_runs = list(metadata.get("retriever_runs") or [])
    retriever_used = [str(run.get("source") or "").strip() for run in retriever_runs if str(run.get("source") or "").strip()]
    graph_result = dict(primary_pass.get("graph_result") or {})
    community_result = dict(primary_pass.get("community_result") or {})
    notes: list[str] = []

    seed_entities = metadata.get("seed_entities")
    if seed_entities is None:
        notes.append("seed_entities not exposed by runtime metadata")

    if "graph_result" not in primary_pass:
        notes.append("graph_result not exposed by selected runtime pass")
    if "community_result" not in primary_pass and metadata.get("internal_route") in {"community_global", "drift_like"}:
        notes.append("community_result not exposed by selected runtime pass")

    diagnostics = {
        "route_policy": metadata.get("route_policy"),
        "requested_mode": metadata.get("requested_mode"),
        "resolved_mode": metadata.get("resolved_mode"),
        "internal_route": metadata.get("internal_route"),
        "graph_worthy": metadata.get("graph_worthy"),
        "retriever_used": retriever_used or None,
        "fallback": fallback,
        "fallback_reason": fallback_reason,
        "graph_result_count": len(list(graph_result.get("documents") or [])) if graph_result else None,
        "graph_path_count": len(list(graph_result.get("paths") or [])) if graph_result else None,
        "seed_entities": seed_entities if seed_entities is not None else None,
        "seed_entity_count": (len(seed_entities) if isinstance(seed_entities, list) else None),
        "community_report_count": len(list(community_result.get("used_communities") or [])) if community_result else None,
        "drift_followup_count": len(list(community_result.get("follow_up_questions") or [])) if community_result else None,
        "round_count": len(rounds) or None,
    }
    return diagnostics, notes


async def run_real_runtime_eval(
    *,
    dataset: str,
    mode: str,
    questions_path: Path,
    corpus_path: Path,
    profile_file: Path,
    profile_name: str,
    route_policy: str = "auto",
    knowledge_id: str | None = None,
    limit: int = 10,
    top_k: int = 10,
    output_path: Path | None = None,
) -> dict[str, Any]:
    normalized_dataset = str(dataset).strip().lower()
    if normalized_dataset not in SUPPORTED_DATASETS:
        raise ValueError(f"Unsupported dataset: {dataset}")
    normalized_mode = str(mode).strip().lower()
    if normalized_mode not in SUPPORTED_MODES:
        raise ValueError(f"Unsupported mode: {mode}")

    profile = resolve_eval_profile(profile_file=profile_file, profile_name=profile_name)
    resolved_route_policy = resolve_route_policy(route_policy)
    model_configs = await resolve_profile_model_configs(profile)
    temp_config = _build_temp_config()
    os.environ["ZUNO_CONFIG"] = str(temp_config)
    await initialize_app_settings(str(temp_config))

    all_questions = _read_jsonl(questions_path)
    selected_questions = all_questions[: max(int(limit), 0)]
    selected_question_ids = {str(row.get("id") or "") for row in selected_questions}
    corpus_rows = _filter_corpus_for_questions(_read_jsonl(corpus_path), selected_question_ids)
    runtime_knowledge_id = str(knowledge_id or f"eval_{normalized_dataset}_{normalized_mode}_{uuid4().hex[:8]}")
    runtime_mode = resolve_runtime_mode(normalized_mode)
    knowledge_config = _build_runtime_knowledge_config(mode=normalized_mode, profile=profile, top_k=top_k)
    chunks = build_chunks_from_corpus(corpus_rows=corpus_rows, knowledge_id=runtime_knowledge_id)

    notes: list[str] = []
    graph_init_error: str | None = None
    graph_retriever = None
    if normalized_mode in {"local_graphrag", "deep_graphrag"}:
        try:
            graph_retriever = await _build_local_graph_retriever(chunks)
        except Exception as exc:
            graph_init_error = str(exc)
            notes.append(f"graph retriever initialization failed: {exc}")

    register_local_runtime_settings(
        runtime_knowledge_id,
        {
            "knowledge_config": knowledge_config,
            "text_embedding_config": model_configs["text_embedding_config"],
            "vl_embedding_config": None,
            "rerank_config": model_configs["rerank_config"],
            "domain_pack_id": None,
            "domain_pack": None,
            "graph_retriever": graph_retriever,
            "knowledge_status": "active",
        },
    )

    questions_report: list[dict[str, Any]] = []
    try:
        await RagHandler.index_milvus_documents(
            runtime_knowledge_id,
            chunks,
            text_embedding_config=model_configs["text_embedding_config"],
            vl_embedding_config=None,
        )

        for row in selected_questions:
            question_id = str(row.get("id") or "")
            question_text = str(row.get("question") or "")
            gold_doc_ids = build_gold_doc_ids(row)
            started = time.perf_counter()
            fallback_reason: str | None = None
            error_message: str | None = None
            route_metadata: dict[str, Any] = {}
            runtime_result: dict[str, Any] | None = None
            failure = False

            try:
                runtime_result = await RagHandler.retrieve_ranked_documents_with_metadata(
                    query=question_text,
                    collection_names=[runtime_knowledge_id],
                    retrieval_mode=runtime_mode,
                    top_k=top_k,
                    retrieval_options=build_runtime_retrieval_options(
                        top_k=top_k,
                        profile_name=profile_name,
                        route_policy=resolved_route_policy,
                    ),
                )
                route_metadata = dict(runtime_result.get("metadata") or {})
                fallback_reason = (
                    route_metadata.get("fallback_reason")
                    or (route_metadata.get("route_trace") or {}).get("degraded_from")
                )
            except Exception as exc:
                failure = True
                error_message = str(exc)
                fallback_reason = graph_init_error if normalized_mode in {"local_graphrag", "deep_graphrag"} else None

            latency_ms = round((time.perf_counter() - started) * 1000, 3)
            final_pass = dict((runtime_result or {}).get("final_pass_result") or {})
            retrieved_documents = list(final_pass.get("documents") or [])
            retrieved_doc_ids_top10 = []
            retrieved_titles_top10 = []
            scores_top10 = []
            for document in retrieved_documents[:10]:
                doc_id = str(document.get("file_id") or document.get("file_name") or document.get("chunk_id") or "")
                title = str(document.get("file_name") or document.get("title") or doc_id)
                if doc_id not in retrieved_doc_ids_top10:
                    retrieved_doc_ids_top10.append(doc_id)
                    retrieved_titles_top10.append(title)
                    scores_top10.append(document.get("score"))

            fallback = bool(route_metadata.get("fallback_triggered")) or bool(fallback_reason)
            diagnostics, missing_notes = extract_route_diagnostics(
                runtime_result=runtime_result,
                fallback=fallback,
                fallback_reason=fallback_reason,
            )
            for note in missing_notes:
                if note not in notes:
                    notes.append(note)
            metrics = compute_question_metrics(
                question_id=question_id,
                gold_doc_ids=gold_doc_ids,
                retrieved_doc_ids=retrieved_doc_ids_top10[:top_k],
                latency_ms=latency_ms,
                fallback=fallback,
                failure=failure,
            )
            questions_report.append(
                {
                    "question_id": question_id,
                    "question": question_text,
                    "gold_doc_ids": gold_doc_ids,
                    "retrieved_doc_ids_top10": retrieved_doc_ids_top10[:10],
                    "retrieved_titles_top10": retrieved_titles_top10[:10],
                    "scores_top10": scores_top10[:10],
                    "route_metadata": route_metadata,
                    "route_diagnostics": diagnostics,
                    "latency_ms": latency_ms,
                    "fallback": fallback,
                    "fallback_reason": fallback_reason,
                    "failure": failure,
                    "error_message": error_message,
                    "metrics": metrics,
                }
            )
    finally:
        clear_local_runtime_settings(runtime_knowledge_id)

    aggregate = aggregate_question_metrics([row["metrics"] for row in questions_report])
    report = {
        "execution_mode": "real_runtime",
        "dataset": normalized_dataset,
        "mode": normalized_mode,
        "requested_runtime_mode": runtime_mode,
        "route_policy": resolved_route_policy,
        "knowledge_id": runtime_knowledge_id,
        "sample_limit": len(selected_questions),
        "top_k": top_k,
        "model_profile": model_configs["model_profile"],
        "aggregate_metrics": aggregate,
        "questions": questions_report,
        "fallback_count": aggregate["fallback_count"],
        "failure_count": aggregate["failure_count"],
        "notes": notes,
        "profile_name": profile_name,
        "profile_file": str(profile_file),
        "questions_path": str(questions_path),
        "corpus_path": str(corpus_path),
        "corpus_document_count": len(corpus_rows),
        "chunk_count": len(chunks),
    }
    if output_path is not None:
        _write_json(output_path, report)
        report["report_path"] = str(output_path)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run retrieval-only real runtime multihop evaluation.")
    parser.add_argument("--dataset", required=True, choices=sorted(SUPPORTED_DATASETS))
    parser.add_argument("--mode", required=True, choices=sorted(SUPPORTED_MODES))
    parser.add_argument("--knowledge-id", default=None)
    parser.add_argument("--questions", required=True, type=Path)
    parser.add_argument("--corpus", required=True, type=Path)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--route-policy", default="auto")
    parser.add_argument("--profile-file", type=Path, default=REPO_ROOT / "tools" / "evals" / "zuno" / "multihop_eval" / "eval_profiles.example.json")
    parser.add_argument("--profile-name", default="retrieval_only_text_multihop")
    args = parser.parse_args()

    output_path = args.output or (DEFAULT_OUTPUT_ROOT / f"{args.dataset}_{args.mode}_limit{args.limit}.json")
    result = asyncio.run(
        run_real_runtime_eval(
            dataset=args.dataset,
            mode=args.mode,
            knowledge_id=args.knowledge_id,
            questions_path=args.questions,
            corpus_path=args.corpus,
            profile_file=args.profile_file,
            profile_name=args.profile_name,
            route_policy=args.route_policy,
            limit=args.limit,
            top_k=args.top_k,
            output_path=output_path,
        )
    )
    print(
        json.dumps(
            {
                "execution_mode": result["execution_mode"],
                "dataset": result["dataset"],
                "mode": result["mode"],
                "sample_limit": result["sample_limit"],
                "fallback_count": result["fallback_count"],
                "failure_count": result["failure_count"],
                "report_path": result.get("report_path"),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
