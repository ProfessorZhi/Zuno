from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlparse
from typing import Any

from sqlalchemy.exc import OperationalError

BACKEND_ROOT = Path(__file__).resolve().parents[4] / "src" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from zuno.api.services.llm import LLMService
from zuno.database.dao.llm import LLMDao
from zuno.database.models.user import SystemUser
from tools.evals.zuno.rag_eval.paths import default_runs_root
from zuno.settings import app_settings, initialize_app_settings


LOCAL_MODEL_HOSTS = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "host.docker.internal",
    "minio",
}


async def get_embedding(text: str, config_override=None):
    from zuno.services.rag.embedding import get_embedding as _get_embedding

    return await _get_embedding(text, config_override=config_override)


def is_probably_local_base_url(base_url: str | None) -> bool:
    normalized = str(base_url or "").strip()
    if not normalized:
        return False
    parsed = urlparse(normalized)
    hostname = (parsed.hostname or "").strip().lower()
    if hostname in LOCAL_MODEL_HOSTS:
        return True
    return hostname.endswith(".local")


def summarize_llm(llm: dict[str, Any]) -> dict[str, Any]:
    normalized_type = LLMService.normalize_llm_type(llm.get("llm_type"))
    model_name = str(llm.get("model_name") or llm.get("model") or "")
    base_url = str(llm.get("base_url") or "")
    return {
        "llm_id": llm.get("llm_id"),
        "model": model_name,
        "model_name": model_name,
        "llm_type": normalized_type,
        "provider": llm.get("provider"),
        "base_url": base_url,
        "model_slot": llm.get("model_slot"),
        "user_id": llm.get("user_id"),
        "is_local": is_probably_local_base_url(base_url),
    }


def ensure_local_embedding_target(llm: dict[str, Any] | None) -> dict[str, Any] | None:
    if not llm:
        return None
    summary = summarize_llm(llm)
    if not summary["is_local"]:
        model_name = summary.get("model") or summary.get("llm_id") or "unknown"
        raise ValueError(f"embedding target is not local: {model_name} @ {summary.get('base_url') or 'n/a'}")
    return llm


def infer_provider_from_base_url(base_url: str | None) -> str:
    normalized = str(base_url or "").strip().lower()
    if any(host in normalized for host in ("localhost", "127.0.0.1", "host.docker.internal")):
        return "openai-compatible-local"
    if "dashscope" in normalized:
        return "dashscope"
    if "minimax" in normalized:
        return "minimax"
    if "openai.com" in normalized:
        return "openai"
    return "custom"


async def list_llm_candidates(*, expected_type: str | None = None, local_only: bool = False) -> list[dict[str, Any]]:
    rows = await LLMDao.get_all_llm()
    candidates: list[dict[str, Any]] = []
    for row in rows:
        item = row.to_dict()
        summary = summarize_llm(item)
        if expected_type and summary["llm_type"] != expected_type:
            continue
        if local_only and not summary["is_local"]:
            continue
        candidates.append(summary)
    candidates.sort(
        key=lambda item: (
            not bool(item.get("is_local")),
            item.get("model_slot") != "embedding",
            str(item.get("model") or ""),
            str(item.get("llm_id") or ""),
        )
    )
    return candidates


async def ensure_llm_registration(
    *,
    model_name: str,
    base_url: str,
    api_key: str,
    llm_type: str,
    model_slot: str | None = None,
) -> dict[str, Any]:
    normalized_type = LLMService.normalize_llm_type(llm_type)
    rows = await LLMDao.get_all_llm()
    normalized_base_url = str(base_url or "").strip().rstrip("/")
    normalized_model = str(model_name or "").strip()
    for row in rows:
        item = row.to_dict()
        if (
            LLMService.normalize_llm_type(item.get("llm_type")) == normalized_type
            and str(item.get("model") or "").strip() == normalized_model
            and str(item.get("base_url") or "").strip().rstrip("/") == normalized_base_url
        ):
            return item

    provider = infer_provider_from_base_url(base_url)
    await LLMService.create_llm(
        model=normalized_model,
        base_url=normalized_base_url,
        llm_type=normalized_type,
        api_key=str(api_key or ""),
        provider=provider,
        user_id=SystemUser,
        model_slot=model_slot,
    )
    rows = await LLMDao.get_all_llm()
    for row in rows:
        item = row.to_dict()
        if (
            LLMService.normalize_llm_type(item.get("llm_type")) == normalized_type
            and str(item.get("model") or "").strip() == normalized_model
            and str(item.get("base_url") or "").strip().rstrip("/") == normalized_base_url
        ):
            return item
    raise RuntimeError(f"failed to register llm for {normalized_model} @ {normalized_base_url}")


async def resolve_embedding_model_id(
    text_embedding_model_id: str | None,
    *,
    auto_pick_local_embedding: bool = False,
) -> tuple[str | None, list[dict[str, Any]]]:
    if text_embedding_model_id:
        return text_embedding_model_id, []
    candidates = await list_llm_candidates(expected_type="Embedding")
    if not auto_pick_local_embedding:
        return None, candidates
    local_candidates = [item for item in candidates if item.get("is_local")]
    prioritized = sorted(
        local_candidates,
        key=lambda item: (
            item.get("model_slot") != "embedding",
            str(item.get("model") or ""),
            str(item.get("llm_id") or ""),
        )
    )
    picked = prioritized[0]["llm_id"] if prioritized else None
    return str(picked) if picked else None, candidates


async def get_active_embedding_config() -> dict[str, Any] | None:
    await initialize_app_settings()
    config = getattr(getattr(app_settings, "multi_models", None), "embedding", None)
    if not config or not getattr(config, "model_name", ""):
        return None
    summary = {
        "model": getattr(config, "model_name", ""),
        "base_url": getattr(config, "base_url", ""),
        "api_key": getattr(config, "api_key", ""),
        "llm_type": "Embedding",
        "model_slot": "embedding",
        "provider": "config",
        "llm_id": None,
        "is_local": is_probably_local_base_url(getattr(config, "base_url", "")),
    }
    return summary


async def resolve_direct_local_embedding_registration(
    *,
    model_name: str | None,
    base_url: str | None,
    api_key: str | None,
) -> dict[str, Any] | None:
    if not model_name and not base_url:
        return None
    if not model_name or not base_url:
        raise ValueError("both local embedding model name and base url are required for direct registration")
    if not is_probably_local_base_url(base_url):
        raise ValueError(f"direct local embedding target is not local: {base_url}")
    return await ensure_llm_registration(
        model_name=str(model_name),
        base_url=str(base_url),
        api_key=str(api_key or ""),
        llm_type="Embedding",
        model_slot=None,
    )


async def validate_model_id(llm_id: str | None, expected_type: str) -> dict[str, Any] | None:
    if not llm_id:
        return None
    llm = await LLMService.get_llm_by_id(llm_id)
    if not llm:
        raise ValueError(f"model not found: {llm_id}")
    actual_type = LLMService.normalize_llm_type(llm.get("llm_type"))
    if actual_type != expected_type:
        raise ValueError(f"model {llm_id} must be {expected_type}, got {actual_type}")
    return llm


async def probe_embedding_model(
    llm: dict[str, Any],
    *,
    sample_text: str = "本地 embedding 连通性测试",
) -> dict[str, Any]:
    started_at = time.perf_counter()
    vector = await get_embedding(sample_text, config_override=llm)
    latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
    if not isinstance(vector, list) or not vector:
        raise ValueError("embedding probe returned empty vector")
    return {
        "model_name": llm.get("model"),
        "llm_id": llm.get("llm_id"),
        "latency_ms": latency_ms,
        "dimension": len(vector),
        "sample_text": sample_text,
    }


async def preflight_local_embedding_eval(
    *,
    text_embedding_model_id: str | None,
    rerank_model_id: str | None = None,
    probe_embedding: bool = True,
    auto_pick_local_embedding: bool = False,
    use_active_config_embedding: bool = False,
    direct_local_embedding_model_name: str | None = None,
    direct_local_embedding_base_url: str | None = None,
    direct_local_embedding_api_key: str | None = None,
    register_direct_local_embedding: bool = False,
) -> dict[str, Any]:
    direct_local_registration = None
    direct_local_config = None
    if direct_local_embedding_model_name or direct_local_embedding_base_url:
        if not direct_local_embedding_model_name or not direct_local_embedding_base_url:
            raise ValueError("both local embedding model name and base url are required for direct local embedding preflight")
        if not is_probably_local_base_url(direct_local_embedding_base_url):
            raise ValueError(f"direct local embedding target is not local: {direct_local_embedding_base_url}")
        direct_local_config = {
            "llm_id": None,
            "llm_type": "Embedding",
            "model": direct_local_embedding_model_name,
            "model_name": direct_local_embedding_model_name,
            "base_url": direct_local_embedding_base_url,
            "api_key": direct_local_embedding_api_key or "",
            "provider": infer_provider_from_base_url(direct_local_embedding_base_url),
            "model_slot": None,
        }
        if register_direct_local_embedding:
            direct_local_registration = await resolve_direct_local_embedding_registration(
                model_name=direct_local_embedding_model_name,
                base_url=direct_local_embedding_base_url,
                api_key=direct_local_embedding_api_key,
            )
    if direct_local_registration:
        resolved_embedding_id = str(direct_local_registration["llm_id"])
        embedding_candidates = await list_llm_candidates(expected_type="Embedding")
    elif direct_local_config:
        resolved_embedding_id = None
        embedding_candidates = []
    else:
        resolved_embedding_id, embedding_candidates = await resolve_embedding_model_id(
            text_embedding_model_id,
            auto_pick_local_embedding=auto_pick_local_embedding,
        )
    active_embedding_config = None
    embedding_llm = None
    if direct_local_config and not direct_local_registration:
        embedding_llm = ensure_local_embedding_target(direct_local_config)
    elif resolved_embedding_id:
        embedding_llm = ensure_local_embedding_target(await validate_model_id(resolved_embedding_id, "Embedding"))
    elif use_active_config_embedding:
        active_embedding_config = await get_active_embedding_config()
        if not active_embedding_config:
            raise ValueError("no active embedding config found for fallback")
        embedding_llm = ensure_local_embedding_target(active_embedding_config)
    else:
        raise ValueError("no embedding model id provided, and no local embedding candidate could be auto-selected")
    rerank_llm = await validate_model_id(rerank_model_id, "Rerank")
    result = {
        "resolved_text_embedding_model_id": resolved_embedding_id,
        "embedding_model": embedding_llm,
        "rerank_model": rerank_llm,
        "embedding_probe": None,
        "embedding_candidates": embedding_candidates,
        "active_embedding_config": active_embedding_config,
        "direct_local_registration": summarize_llm(direct_local_registration) if direct_local_registration else None,
        "direct_local_config": summarize_llm(direct_local_config) if direct_local_config else None,
    }
    if probe_embedding and embedding_llm:
        result["embedding_probe"] = await probe_embedding_model(embedding_llm)
    return result


def _should_use_stackless_fallback(
    exc: Exception,
    *,
    direct_local_embedding_model_name: str | None,
    direct_local_embedding_base_url: str | None,
) -> bool:
    if not direct_local_embedding_model_name or not direct_local_embedding_base_url:
        return False
    if isinstance(exc, OperationalError):
        return True
    message = str(exc).lower()
    return "localhost" in message and "5432" in message


async def _run_stackless_fallback(
    *,
    manifest_path: Path,
    dataset_path: Path,
    output_root: Path,
    profile_set: str,
    direct_local_embedding_model_name: str,
    direct_local_embedding_base_url: str,
    direct_local_embedding_api_key: str | None,
    rerank_model_id: str | None,
) -> dict[str, Any]:
    from tools.evals.zuno.rag_eval.run_stackless_local_eval import run_stackless_local_eval
    from tools.evals.zuno.rag_eval.summarize_eval_profiles import summarize, write_markdown

    result = await run_stackless_local_eval(
        manifest_path=manifest_path,
        dataset_path=dataset_path,
        output_root=output_root,
        profile_set=profile_set,
        local_embedding_model_name=direct_local_embedding_model_name,
        local_embedding_base_url=direct_local_embedding_base_url,
        local_embedding_api_key=str(direct_local_embedding_api_key or ""),
        spawn_dev_embedding_server=False,
        spawn_dev_rerank_server=False,
        domain_pack_id="contract_review" if "contract_review" in str(manifest_path).lower() else None,
    )
    summary = summarize(dataset_path=Path(result["effective_dataset_path"]), profiles_root=output_root)
    summary_json_path = output_root / "summary.json"
    summary_md_path = output_root / "summary.md"
    summary_json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(summary_md_path, summary)
    return {
        "knowledge_id": result["knowledge_id"],
        "knowledge_name": "stackless-local-embedding-fallback",
        "text_embedding_model_id": None,
        "rerank_model_id": rerank_model_id,
        "profile_set": profile_set,
        "profiles": result["profiles"],
        "preflight": result["preflight"],
        "output_root": str(output_root),
        "ingest_result": None,
        "eval_report": result["report"],
        "summary_json": str(summary_json_path),
        "summary_md": str(summary_md_path),
        "execution_mode": "stackless_fallback",
        "fallback_reason": "database_unavailable_for_local_embedding_registration_or_ingest",
        "stackless_result": result,
    }


async def run_local_embedding_eval(
    *,
    manifest_path: Path,
    dataset_path: Path,
    knowledge_name: str,
    text_embedding_model_id: str | None,
    rerank_model_id: str | None = None,
    profile_set: str = "local_compare",
    output_root: Path,
    probe_embedding: bool = True,
    auto_pick_local_embedding: bool = False,
    use_active_config_embedding: bool = False,
    direct_local_embedding_model_name: str | None = None,
    direct_local_embedding_base_url: str | None = None,
    direct_local_embedding_api_key: str | None = None,
) -> dict[str, Any]:
    from tools.evals.zuno.rag_eval.ingest_prepared_corpus import ingest_prepared_corpus
    from tools.evals.zuno.rag_eval.run_eval import resolve_profiles, run_eval
    from tools.evals.zuno.rag_eval.summarize_eval_profiles import summarize, write_markdown

    try:
        preflight = await preflight_local_embedding_eval(
            text_embedding_model_id=text_embedding_model_id,
            rerank_model_id=rerank_model_id,
            probe_embedding=probe_embedding,
            auto_pick_local_embedding=auto_pick_local_embedding,
            use_active_config_embedding=use_active_config_embedding,
            direct_local_embedding_model_name=direct_local_embedding_model_name,
            direct_local_embedding_base_url=direct_local_embedding_base_url,
            direct_local_embedding_api_key=direct_local_embedding_api_key,
            register_direct_local_embedding=True,
        )
        resolved_embedding_id = preflight["resolved_text_embedding_model_id"]

        ingest_result = await ingest_prepared_corpus(
            manifest_path=manifest_path,
            knowledge_name=knowledge_name,
            text_embedding_model_id=str(resolved_embedding_id) if resolved_embedding_id else None,
            rerank_model_id=rerank_model_id,
            index_capability="rag_graph",
            default_mode="rag_graph",
        )
        knowledge_id = str(ingest_result["knowledge_id"])
        profiles = resolve_profiles(profile_set=profile_set)
        eval_report = await run_eval(
            dataset_path=dataset_path,
            knowledge_ids=[knowledge_id],
            profiles=profiles,
            output_dir=output_root,
            trace_langsmith=False,
            answer_mode="extractive",
            judge_mode="heuristic",
        )

        summary = summarize(dataset_path=dataset_path, profiles_root=output_root)
        summary_json_path = output_root / "summary.json"
        summary_md_path = output_root / "summary.md"
        summary_json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        write_markdown(summary_md_path, summary)

        return {
            "knowledge_id": knowledge_id,
            "knowledge_name": knowledge_name,
            "text_embedding_model_id": resolved_embedding_id,
            "rerank_model_id": rerank_model_id,
            "profile_set": profile_set,
            "profiles": profiles,
            "preflight": preflight,
            "output_root": str(output_root),
            "ingest_result": ingest_result,
            "eval_report": eval_report,
            "summary_json": str(summary_json_path),
            "summary_md": str(summary_md_path),
            "execution_mode": "database_backed",
            "fallback_reason": None,
        }
    except Exception as exc:
        if not _should_use_stackless_fallback(
            exc,
            direct_local_embedding_model_name=direct_local_embedding_model_name,
            direct_local_embedding_base_url=direct_local_embedding_base_url,
        ):
            raise
        return await _run_stackless_fallback(
            manifest_path=manifest_path,
            dataset_path=dataset_path,
            output_root=output_root,
            profile_set=profile_set,
            direct_local_embedding_model_name=str(direct_local_embedding_model_name),
            direct_local_embedding_base_url=str(direct_local_embedding_base_url),
            direct_local_embedding_api_key=direct_local_embedding_api_key,
            rerank_model_id=rerank_model_id,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local-embedding RAG and GraphRAG evaluation end to end.")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--knowledge-name", default="ZunoLocalEmbeddingEval")
    parser.add_argument("--text-embedding-model-id", default=None)
    parser.add_argument("--rerank-model-id", default=None)
    parser.add_argument("--profile-set", choices=["local_compare", "graph_compare"], default="local_compare")
    parser.add_argument("--output-root", type=Path, default=None)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--skip-embedding-probe", action="store_true")
    parser.add_argument("--list-embedding-models", action="store_true")
    parser.add_argument("--list-rerank-models", action="store_true")
    parser.add_argument("--local-only", action="store_true")
    parser.add_argument("--auto-pick-local-embedding", action="store_true")
    parser.add_argument("--use-active-config-embedding", action="store_true")
    parser.add_argument("--local-embedding-model-name", default=None)
    parser.add_argument("--local-embedding-base-url", default=None)
    parser.add_argument("--local-embedding-api-key", default="")
    args = parser.parse_args()

    if args.list_embedding_models:
        result = asyncio.run(list_llm_candidates(expected_type="Embedding", local_only=args.local_only))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.list_rerank_models:
        result = asyncio.run(list_llm_candidates(expected_type="Rerank", local_only=args.local_only))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    output_root = args.output_root or default_runs_root() / f"local-embedding-{time.strftime('%Y%m%d-%H%M%S')}"
    if args.validate_only:
        result = asyncio.run(
            preflight_local_embedding_eval(
                text_embedding_model_id=args.text_embedding_model_id,
                rerank_model_id=args.rerank_model_id,
                probe_embedding=not args.skip_embedding_probe,
                auto_pick_local_embedding=args.auto_pick_local_embedding,
                use_active_config_embedding=args.use_active_config_embedding,
                direct_local_embedding_model_name=args.local_embedding_model_name,
                direct_local_embedding_base_url=args.local_embedding_base_url,
                direct_local_embedding_api_key=args.local_embedding_api_key,
            )
        )
        print(json.dumps(result, ensure_ascii=False))
        return

    result = asyncio.run(
        run_local_embedding_eval(
            manifest_path=args.manifest,
            dataset_path=args.dataset,
            knowledge_name=args.knowledge_name,
            text_embedding_model_id=args.text_embedding_model_id,
            rerank_model_id=args.rerank_model_id,
            profile_set=args.profile_set,
            output_root=output_root,
            probe_embedding=not args.skip_embedding_probe,
            auto_pick_local_embedding=args.auto_pick_local_embedding,
            use_active_config_embedding=args.use_active_config_embedding,
            direct_local_embedding_model_name=args.local_embedding_model_name,
            direct_local_embedding_base_url=args.local_embedding_base_url,
            direct_local_embedding_api_key=args.local_embedding_api_key,
        )
    )
    print(
        json.dumps(
            {
                "knowledge_id": result["knowledge_id"],
                "profile_set": result["profile_set"],
                "execution_mode": result.get("execution_mode"),
                "fallback_reason": result.get("fallback_reason"),
                "summary_json": result["summary_json"],
                "summary_md": result["summary_md"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
