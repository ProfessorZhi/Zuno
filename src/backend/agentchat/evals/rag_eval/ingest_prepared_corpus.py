from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path, PureWindowsPath

BACKEND_ROOT = Path(__file__).resolve().parents[3]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from agentchat.api.services.knowledge import KnowledgeService
from agentchat.api.services.knowledge_file import KnowledgeFileService
from agentchat.database.models.user import AdminUser
from agentchat.settings import app_settings, initialize_app_settings


DEFAULT_EVAL_CONFIG = {
    "index_capability": "rag_graph",
    "index_settings": {
        "chunk_mode": "parent_child",
        "chunk_size": 1024,
        "overlap": 120,
        "separator": "\n\n",
        "replace_consecutive_spaces": True,
        "remove_urls_emails": False,
        "image_indexing_mode": "dual",
        "vector_backend": "milvus",
    },
    "graph_index_settings": {
        "entity_extraction_mode": "rule_llm",
        "relation_schema": "open",
        "entity_normalization": True,
        "evidence_backlink": True,
        "use_rag_entry_chunk": True,
    },
    "retrieval_settings": {
        "default_mode": "rag_graph",
        "refill_policy": "smart",
        "top_k": 5,
        "rerank_enabled": True,
        "rerank_top_k": 3,
        "score_threshold": 0.7,
        "graph_hop_limit": 2,
        "max_paths_per_entity": 5,
    },
}


def _resolve_prepared_path(manifest_path: Path, item: dict) -> Path:
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


async def _resolve_or_create_knowledge(name: str, user_id: str) -> str:
    existing = await KnowledgeService.get_knowledge_ids_from_name([name], user_id)
    if existing:
        return str(existing[0])

    await KnowledgeService.create_knowledge(
        name,
        "Python notes evaluation knowledge base for RAG and GraphRAG metrics.",
        user_id,
        DEFAULT_EVAL_CONFIG,
    )
    created = await KnowledgeService.get_knowledge_ids_from_name([name], user_id)
    if not created:
        raise RuntimeError(f"failed to create knowledge: {name}")
    return str(created[0])


async def ingest_prepared_corpus(
    *,
    manifest_path: Path,
    knowledge_name: str,
    user_id: str = AdminUser,
    dispatch: str = "sync",
) -> dict:
    await initialize_app_settings()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    knowledge_id = await _resolve_or_create_knowledge(knowledge_name, user_id)
    previous_rabbitmq_enabled = bool((app_settings.rabbitmq or {}).get("enabled"))
    if dispatch == "sync":
        app_settings.rabbitmq["enabled"] = False

    results = []
    try:
        for item in manifest.get("files", []):
            prepared_path = _resolve_prepared_path(manifest_path, item)
            result = await KnowledgeFileService.create_knowledge_file(
                file_name=item["file_name"],
                file_path=str(prepared_path),
                knowledge_id=knowledge_id,
                user_id=user_id,
                oss_url=f"local://{prepared_path.name}",
                file_size_bytes=prepared_path.stat().st_size,
            )
            results.append(
                {
                    "file_name": item["file_name"],
                    "prepared_path": str(prepared_path),
                    **result,
                }
            )
    finally:
        app_settings.rabbitmq["enabled"] = previous_rabbitmq_enabled

    return {
        "knowledge_id": knowledge_id,
        "knowledge_name": knowledge_name,
        "file_count": len(results),
        "dispatch": dispatch,
        "files": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest prepared Python notes into a Zuno knowledge base.")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--knowledge-name", default="ZunoPythonEval")
    parser.add_argument("--user-id", default=AdminUser)
    parser.add_argument("--dispatch", choices=["sync"], default="sync")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = asyncio.run(
        ingest_prepared_corpus(
            manifest_path=args.manifest,
            knowledge_name=args.knowledge_name,
            user_id=args.user_id,
            dispatch=args.dispatch,
        )
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"knowledge_id": result["knowledge_id"], "file_count": result["file_count"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
