from __future__ import annotations

import json

from agentchat.services.graphrag.extractors.structured_extractor import StructuredGraphExtractor


class CachedGraphExtractor:
    def __init__(self, extractor: StructuredGraphExtractor | None = None):
        self.extractor = extractor or StructuredGraphExtractor()
        self._cache: dict[str, dict] = {}

    async def extract_from_chunk(self, chunk: dict, knowledge_id: str, *, domain_pack: dict | None = None) -> dict:
        cache_key = json.dumps(
            {
                "knowledge_id": knowledge_id,
                "chunk_id": chunk.get("chunk_id"),
                "content": chunk.get("content"),
                "domain_pack_id": (domain_pack or {}).get("id"),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        if cache_key not in self._cache:
            self._cache[cache_key] = await self.extractor.extract_from_chunk(
                chunk,
                knowledge_id,
                domain_pack=domain_pack,
            )
        return self._cache[cache_key]
