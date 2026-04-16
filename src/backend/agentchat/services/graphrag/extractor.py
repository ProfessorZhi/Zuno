import re


class GraphExtractor:
    ENTITY_PATTERN = re.compile(r"\b[A-Z][a-zA-Z0-9_-]{1,}\b")

    async def extract_from_chunk(self, chunk: dict, knowledge_id: str) -> dict:
        content = (chunk.get("content") or "").strip()
        chunk_id = chunk.get("chunk_id", "")
        entities = []
        seen = set()
        for match in self.ENTITY_PATTERN.findall(content):
            if match not in seen:
                seen.add(match)
                entities.append(
                    {
                        "name": match,
                        "type": "entity",
                        "knowledge_id": knowledge_id,
                        "chunk_id": chunk_id,
                    }
                )

        relations = []
        for index in range(len(entities) - 1):
            relations.append(
                {
                    "source": entities[index]["name"],
                    "target": entities[index + 1]["name"],
                    "relation_type": "mentioned_with",
                    "knowledge_id": knowledge_id,
                    "chunk_id": chunk_id,
                }
            )

        return {
            "entities": entities,
            "relations": relations,
        }
