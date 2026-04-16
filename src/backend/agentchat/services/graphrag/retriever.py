import re

from agentchat.services.graphrag.client import Neo4jClient


class GraphRetriever:
    ENTITY_PATTERN = re.compile(r"\b[A-Z][a-zA-Z0-9_-]{1,}\b")

    def __init__(self, client: Neo4jClient | None = None):
        self.client = client or Neo4jClient()

    async def retrieve(self, query: str, knowledge_id: str) -> dict:
        entities = []
        paths = []
        for entity_name in self.ENTITY_PATTERN.findall(query):
            neighbor_paths = await self.client.query_neighbors(entity_name, knowledge_id)
            if neighbor_paths:
                entities.append(entity_name)
                paths.extend(neighbor_paths)

        path_lines = [f"{item['source']} -> {item['target']}" for item in paths]
        content = "\n".join(path_lines)
        return {
            "content": content,
            "entities": entities,
            "paths": path_lines,
        }
