from __future__ import annotations

import argparse
import asyncio
import contextlib
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path, PureWindowsPath
from typing import Any

import yaml

SERVICE_API_SRC_ROOT = Path(__file__).resolve().parents[4] / "services" / "api" / "src"
if str(SERVICE_API_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_API_SRC_ROOT))

from agentchat.api.services.knowledge import DEFAULT_KNOWLEDGE_CONFIG
from agentchat.evals.rag_eval.ingest_prepared_corpus import build_eval_knowledge_config
from agentchat.evals.rag_eval.local_embedding_server import run_dev_server
from agentchat.evals.rag_eval.paths import default_runs_root
from agentchat.evals.rag_eval.local_rerank_server import run_dev_server as run_rerank_dev_server
from agentchat.evals.rag_eval.run_eval import PROFILE_SETTINGS, resolve_profiles, run_eval
from agentchat.evals.rag_eval.run_local_embedding_eval import preflight_local_embedding_eval
from agentchat.schema.chunk import ChunkModel
from agentchat.services.domain_pack.loader import DomainPackLoader
from agentchat.services.graphrag.extractor import GraphExtractor
from agentchat.services.graphrag.extractors.structured_extractor import StructuredGraphExtractor
from agentchat.services.graphrag.retriever import GraphRetriever
from agentchat.services.rag.handler import RagHandler
from agentchat.services.rag.parser import doc_parser
from agentchat.services.rag.vector_db import milvus_client
from agentchat.services.runtime_registry import clear_local_runtime_settings, register_local_runtime_settings
from agentchat.settings import initialize_app_settings, resolve_app_config_path


def _resolve_prepared_path(manifest_path: Path, item: dict[str, Any]) -> Path:
    raw_path = str(item.get("prepared_path") or "")
    candidates = []
    if raw_path:
        candidates.append(Path(raw_path))
        candidates.append(manifest_path.parent / "files" / PureWindowsPath(raw_path).name)
    if item.get("file_name"):
        candidates.extend(manifest_path.parent.glob(f"files/*_{item['file_name']}"))
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    raise FileNotFoundError(f"prepared file not found for manifest item: {item.get('file_name') or raw_path}")


def _filter_manifest_by_dataset(manifest: dict[str, Any], dataset_path: Path) -> dict[str, Any]:
    samples = [json.loads(line) for line in dataset_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    file_hints = {
        str(evidence.get("file_contains") or "").strip()
        for sample in samples
        for evidence in sample.get("gold_evidence") or []
        if str(evidence.get("file_contains") or "").strip()
    }
    if not file_hints:
        return manifest

    normalized_hints = set()
    for hint in file_hints:
        normalized_hints.add(hint)
        path_hint = Path(hint)
        if path_hint.suffix:
            normalized_hints.add(path_hint.stem)

    filtered_files = [
        item
        for item in manifest.get("files", [])
        if any(hint in str(item.get("file_name") or "") for hint in normalized_hints)
    ]
    if not filtered_files:
        return manifest
    narrowed = dict(manifest)
    narrowed["files"] = filtered_files
    narrowed["file_count"] = len(filtered_files)
    narrowed["dataset_focus_hints"] = sorted(file_hints)
    return narrowed


def _subset_dataset(dataset_path: Path, sample_limit: int | None) -> Path:
    if not sample_limit or sample_limit <= 0:
        return dataset_path
    rows = [json.loads(line) for line in dataset_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    subset_rows = rows[:sample_limit]
    temp_dir = Path(tempfile.mkdtemp(prefix="zuno-stackless-dataset-"))
    temp_dataset = temp_dir / dataset_path.name
    temp_dataset.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in subset_rows) + ("\n" if subset_rows else ""),
        encoding="utf-8",
    )
    return temp_dataset


def _synthetic_file_id(path: Path) -> str:
    return hashlib.md5(str(path).encode("utf-8")).hexdigest()


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
    ) -> list[dict[str, Any]]:
        matches: list[dict[str, Any]] = []
        needle = str(entity_name or "").strip().lower()
        for item in self.extracted_documents:
            for relation in item.get("relations") or []:
                source = str(relation.get("source") or "").strip()
                target = str(relation.get("target") or "").strip()
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
                        "relation_type": str(relation.get("relation_type") or "related_to"),
                        "chunk_ids": [chunk_id] if chunk_id else [],
                        "evidence": str(relation.get("evidence") or ""),
                        "confidence": relation.get("confidence"),
                    }
                )
                if len(matches) >= limit:
                    return matches
        return matches


class _LocalChunkStore:
    def __init__(self, chunks: list[ChunkModel]):
        self.by_chunk_id = {str(chunk.chunk_id): chunk.to_dict() for chunk in chunks}
        self.by_file_id: dict[str, list[dict[str, Any]]] = {}
        for chunk in chunks:
            payload = chunk.to_dict()
            file_id = str(payload.get("file_id") or "")
            if not file_id:
                continue
            self.by_file_id.setdefault(file_id, []).append(payload)
        for file_id, rows in self.by_file_id.items():
            rows.sort(key=lambda item: str(item.get("chunk_id") or ""))

    async def get_documents_by_chunk_ids(self, collection_name: str, chunk_ids: list[str]) -> list[dict[str, Any]]:
        documents: list[dict[str, Any]] = []
        for chunk_id in chunk_ids:
            payload = self.by_chunk_id.get(str(chunk_id))
            if payload:
                documents.append(dict(payload))
        return documents

    async def get_documents_by_file_id(
        self,
        collection_name: str,
        file_id: str,
        *,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        rows = [dict(item) for item in self.by_file_id.get(str(file_id or ""), [])]
        if limit:
            rows = rows[: max(int(limit), 0)]
        return rows


async def _load_chunks(
    *,
    manifest_path: Path,
    knowledge_id: str,
    knowledge_config: dict[str, Any],
    dataset_path: Path | None = None,
) -> list[ChunkModel]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if dataset_path is not None:
        manifest = _filter_manifest_by_dataset(manifest, dataset_path)
    chunks: list[ChunkModel] = []
    for item in manifest.get("files", []):
        prepared_path = _resolve_prepared_path(manifest_path, item)
        file_chunks = await doc_parser.parse_doc_into_chunks(
            _synthetic_file_id(prepared_path),
            str(prepared_path),
            knowledge_id,
            source_url=f"local://{prepared_path.name}",
            knowledge_config=knowledge_config,
        )
        chunks.extend(file_chunks)
    return chunks


async def _build_local_graph_retriever(
    chunks: list[ChunkModel],
    *,
    domain_pack_id: str | None = None,
) -> GraphRetriever:
    domain_pack = DomainPackLoader().load(domain_pack_id) if domain_pack_id else None
    extractor = StructuredGraphExtractor() if domain_pack else GraphExtractor()
    extracted_documents: list[dict[str, Any]] = []
    for chunk in chunks:
        if domain_pack:
            extraction = await extractor.extract_from_chunk(chunk, chunk.knowledge_id, domain_pack=domain_pack.to_dict())
        else:
            extraction = await extractor.extract_from_chunk(chunk, chunk.knowledge_id)
        extracted_documents.append(
            {
                "chunk": chunk.to_dict(),
                "entities": list(extraction.get("entities") or []),
                "relations": list(extraction.get("relations") or []),
            }
        )
    return GraphRetriever(
        client=_LocalGraphClient(extracted_documents),
        chunk_store=_LocalChunkStore(chunks),
    )


def _build_temp_config() -> Path:
    source_path = resolve_app_config_path()
    data = yaml.safe_load(source_path.read_text(encoding="utf-8")) or {}
    rag = data.setdefault("rag", {})
    rag["enable_elasticsearch"] = False
    vector_db = rag.setdefault("vector_db", {})
    vector_db["mode"] = "chroma"
    temp_dir = Path(tempfile.mkdtemp(prefix="zuno-stackless-eval-"))
    temp_config = temp_dir / "config.yaml"
    temp_config.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return temp_config


def _build_disabled_rerank_config() -> dict[str, Any]:
    return {
        "model_name": "",
        "api_key": "",
        "base_url": "",
        "llm_type": "Rerank",
        "provider": "disabled-local-fallback",
    }


def _build_local_rerank_config(*, model_name: str, base_url: str, api_key: str = "") -> dict[str, Any]:
    return {
        "model_name": str(model_name),
        "api_key": str(api_key or "local-rerank-dev"),
        "base_url": str(base_url),
        "llm_type": "Rerank",
        "provider": "openai-compatible-local-rerank",
    }


@contextlib.contextmanager
def _override_profile_thresholds(
    *,
    profiles: list[str],
    rerank_score_threshold_override: float | None = None,
):
    snapshots: dict[str, Any] = {}
    if rerank_score_threshold_override is None:
        yield
        return
    try:
        for profile in profiles:
            settings = PROFILE_SETTINGS.get(profile)
            if not settings:
                continue
            retrieval_options = settings.get("retrieval_options") or {}
            if not retrieval_options.get("rerank_enabled"):
                continue
            snapshots[profile] = retrieval_options.get("score_threshold")
            retrieval_options["score_threshold"] = float(rerank_score_threshold_override)
        yield
    finally:
        for profile, original_threshold in snapshots.items():
            PROFILE_SETTINGS[profile]["retrieval_options"]["score_threshold"] = original_threshold


async def run_stackless_local_eval(
    *,
    manifest_path: Path,
    dataset_path: Path,
    output_root: Path,
    profile_set: str | None = None,
    profiles: str | None = None,
    local_embedding_model_name: str | None = None,
    local_embedding_base_url: str | None = None,
    local_embedding_api_key: str = "",
    local_rerank_model_name: str | None = None,
    local_rerank_base_url: str | None = None,
    local_rerank_api_key: str = "",
    rerank_score_threshold_override: float | None = None,
    focus_on_dataset_evidence: bool = True,
    sample_limit: int | None = None,
    spawn_dev_embedding_server: bool = False,
    spawn_dev_rerank_server: bool = False,
    domain_pack_id: str | None = None,
    chunk_size_override: int | None = None,
    overlap_override: int | None = None,
) -> dict[str, Any]:
    temp_config = _build_temp_config()
    os.environ["ZUNO_CONFIG"] = str(temp_config)
    await initialize_app_settings(str(temp_config))

    if not profile_set and not profiles:
        raise ValueError("either profile_set or profiles must be provided")

    server_context = (
        run_dev_server(model_name=local_embedding_model_name or "zuno-local-embedding-dev", port=0)
        if spawn_dev_embedding_server
        else contextlib.nullcontext(None)
    )
    rerank_context = (
        run_rerank_dev_server(model_name=local_rerank_model_name or "zuno-local-rerank-dev", port=0)
        if spawn_dev_rerank_server
        else contextlib.nullcontext(None)
    )
    with server_context as dev_server, rerank_context as rerank_server:
        resolved_local_embedding_model_name = local_embedding_model_name or (
            str(dev_server["model_name"]) if dev_server else None
        )
        resolved_local_embedding_base_url = local_embedding_base_url or (
            str(dev_server["base_url"]) if dev_server else None
        )
        if not resolved_local_embedding_model_name or not resolved_local_embedding_base_url:
            raise ValueError("local embedding model name and base url are required")

        preflight = await preflight_local_embedding_eval(
            text_embedding_model_id=None,
            direct_local_embedding_model_name=resolved_local_embedding_model_name,
            direct_local_embedding_base_url=resolved_local_embedding_base_url,
            direct_local_embedding_api_key=local_embedding_api_key,
            probe_embedding=True,
            register_direct_local_embedding=False,
        )
        direct_local_config = dict(preflight["embedding_model"] or {})
        resolved_local_rerank_model_name = local_rerank_model_name or (
            str(rerank_server["model_name"]) if rerank_server else None
        )
        resolved_local_rerank_base_url = local_rerank_base_url or (
            str(rerank_server["base_url"]) if rerank_server else None
        )
        rerank_config = (
            _build_local_rerank_config(
                model_name=resolved_local_rerank_model_name,
                base_url=resolved_local_rerank_base_url,
                api_key=local_rerank_api_key,
            )
            if resolved_local_rerank_model_name and resolved_local_rerank_base_url
            else _build_disabled_rerank_config()
        )

        knowledge_id = f"stackless_eval_{int(time.time())}"
        knowledge_config = build_eval_knowledge_config(
            text_embedding_model_id=None,
            rerank_model_id=None,
            index_capability="rag_graph",
            default_mode="rag_graph",
        )
        merged_knowledge_config = json.loads(json.dumps(DEFAULT_KNOWLEDGE_CONFIG, ensure_ascii=False))
        merged_knowledge_config.update(knowledge_config)
        merged_knowledge_config.setdefault("index_settings", {}).update({"vector_backend": "chroma", "image_indexing_mode": "text_only"})
        if chunk_size_override is not None:
            merged_knowledge_config["index_settings"]["chunk_size"] = int(chunk_size_override)
        if overlap_override is not None:
            merged_knowledge_config["index_settings"]["overlap"] = int(overlap_override)

        effective_dataset_path = _subset_dataset(dataset_path, sample_limit)
        chunks = await _load_chunks(
            manifest_path=manifest_path,
            knowledge_id=knowledge_id,
            knowledge_config=merged_knowledge_config,
            dataset_path=effective_dataset_path if focus_on_dataset_evidence else None,
        )

        milvus_client._client = None
        try:
            await milvus_client.delete_collection(knowledge_id)
        except Exception:
            pass
        await RagHandler.index_milvus_documents(
            knowledge_id,
            chunks,
            text_embedding_config=direct_local_config,
            vl_embedding_config=None,
        )

        graph_retriever = await _build_local_graph_retriever(chunks, domain_pack_id=domain_pack_id)
        register_local_runtime_settings(
            knowledge_id,
            {
                "knowledge_config": merged_knowledge_config,
                "text_embedding_config": direct_local_config,
                "vl_embedding_config": None,
                "rerank_config": rerank_config,
                "domain_pack_id": domain_pack_id,
                "domain_pack": DomainPackLoader().load(domain_pack_id).to_dict() if domain_pack_id else None,
                "graph_retriever": graph_retriever,
            },
        )
        try:
            resolved_profiles = resolve_profiles(profiles=profiles, profile_set=profile_set)
            with _override_profile_thresholds(
                profiles=resolved_profiles,
                rerank_score_threshold_override=rerank_score_threshold_override,
            ):
                report = await run_eval(
                    dataset_path=effective_dataset_path,
                    knowledge_ids=[knowledge_id],
                    profiles=resolved_profiles,
                    output_dir=output_root,
                    trace_langsmith=False,
                    answer_mode="extractive",
                    judge_mode="heuristic",
                )
        finally:
            clear_local_runtime_settings(knowledge_id)

    return {
        "knowledge_id": knowledge_id,
        "chunk_count": len(chunks),
        "profiles": resolved_profiles,
        "output_root": str(output_root),
        "focus_on_dataset_evidence": focus_on_dataset_evidence,
        "effective_dataset_path": str(effective_dataset_path),
        "preflight": preflight,
        "rerank_config": rerank_config,
        "rerank_score_threshold_override": rerank_score_threshold_override,
        "domain_pack_id": domain_pack_id,
        "chunk_size_override": chunk_size_override,
        "overlap_override": overlap_override,
        "report": report,
        "temp_config": str(temp_config),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run stackless local RAG/GraphRAG eval without database-backed knowledge metadata.")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--output-root", type=Path, default=None)
    parser.add_argument("--profile-set", choices=["local_compare", "graph_compare"], default="local_compare")
    parser.add_argument("--profiles", default=None)
    parser.add_argument("--local-embedding-model-name", default=None)
    parser.add_argument("--local-embedding-base-url", default=None)
    parser.add_argument("--local-embedding-api-key", default="")
    parser.add_argument("--local-rerank-model-name", default=None)
    parser.add_argument("--local-rerank-base-url", default=None)
    parser.add_argument("--local-rerank-api-key", default="")
    parser.add_argument("--rerank-score-threshold-override", type=float, default=None)
    parser.add_argument("--disable-dataset-focus", action="store_true")
    parser.add_argument("--sample-limit", type=int, default=None)
    parser.add_argument("--spawn-dev-embedding-server", action="store_true")
    parser.add_argument("--spawn-dev-rerank-server", action="store_true")
    parser.add_argument("--domain-pack-id", default=None)
    parser.add_argument("--chunk-size-override", type=int, default=None)
    parser.add_argument("--overlap-override", type=int, default=None)
    args = parser.parse_args()

    output_root = args.output_root or default_runs_root() / f"stackless-local-{time.strftime('%Y%m%d-%H%M%S')}"
    result = asyncio.run(
        run_stackless_local_eval(
            manifest_path=args.manifest,
            dataset_path=args.dataset,
            output_root=output_root,
            profile_set=args.profile_set,
            profiles=args.profiles,
            local_embedding_model_name=args.local_embedding_model_name,
            local_embedding_base_url=args.local_embedding_base_url,
            local_embedding_api_key=args.local_embedding_api_key,
            local_rerank_model_name=args.local_rerank_model_name,
            local_rerank_base_url=args.local_rerank_base_url,
            local_rerank_api_key=args.local_rerank_api_key,
            rerank_score_threshold_override=args.rerank_score_threshold_override,
            focus_on_dataset_evidence=not args.disable_dataset_focus,
            sample_limit=args.sample_limit,
            spawn_dev_embedding_server=args.spawn_dev_embedding_server,
            spawn_dev_rerank_server=args.spawn_dev_rerank_server,
            domain_pack_id=args.domain_pack_id,
            chunk_size_override=args.chunk_size_override,
            overlap_override=args.overlap_override,
        )
    )
    print(
        json.dumps(
            {
                "knowledge_id": result["knowledge_id"],
                "chunk_count": result["chunk_count"],
                "profiles": result["profiles"],
                "output_root": result["output_root"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
