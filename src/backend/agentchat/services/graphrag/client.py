import asyncio

from agentchat.settings import app_settings


class Neo4jClient:
    def __init__(
        self,
        uri: str | None = None,
        username: str | None = None,
        password: str | None = None,
        database: str | None = None,
    ):
        config = app_settings.neo4j or {}
        self.uri = uri or config.get("uri", "")
        self.username = username or config.get("username", "")
        self.password = password or config.get("password", "")
        self.database = database or config.get("database", "neo4j")

    @classmethod
    def is_enabled(cls) -> bool:
        return bool((app_settings.neo4j or {}).get("enabled"))

    def _driver(self):
        from neo4j import GraphDatabase

        return GraphDatabase.driver(self.uri, auth=(self.username, self.password))

    async def upsert_entity(self, entity: dict):
        def _run():
            driver = self._driver()
            try:
                with driver.session(database=self.database) as session:
                    session.run(
                        """
                        MERGE (e:Entity {name: $name, knowledge_id: $knowledge_id})
                        SET e.type = $type
                        """,
                        {
                            "name": entity.get("name", ""),
                            "knowledge_id": entity.get("knowledge_id", ""),
                            "type": entity.get("type", "entity"),
                        },
                    )
            finally:
                driver.close()

        await asyncio.to_thread(_run)

    async def upsert_relation(self, relation: dict):
        def _run():
            driver = self._driver()
            try:
                with driver.session(database=self.database) as session:
                    session.run(
                        """
                        MERGE (s:Entity {name: $source, knowledge_id: $knowledge_id})
                        MERGE (t:Entity {name: $target, knowledge_id: $knowledge_id})
                        MERGE (s)-[r:RELATES_TO {type: $relation_type}]->(t)
                        SET r.chunk_id = $chunk_id
                        """,
                        {
                            "source": relation.get("source", ""),
                            "target": relation.get("target", ""),
                            "knowledge_id": relation.get("knowledge_id", ""),
                            "relation_type": relation.get("relation_type", "related_to"),
                            "chunk_id": relation.get("chunk_id", ""),
                        },
                    )
            finally:
                driver.close()

        await asyncio.to_thread(_run)

    async def query_neighbors(self, entity_name: str, knowledge_id: str, hops: int = 1) -> list[dict]:
        def _run():
            driver = self._driver()
            try:
                with driver.session(database=self.database) as session:
                    result = session.run(
                        """
                        MATCH (e:Entity {name: $name, knowledge_id: $knowledge_id})-[r:RELATES_TO*1..2]-(n:Entity {knowledge_id: $knowledge_id})
                        RETURN e.name AS source, n.name AS target
                        LIMIT 10
                        """,
                        {
                            "name": entity_name,
                            "knowledge_id": knowledge_id,
                            "hops": hops,
                        },
                    )
                    return [record.data() for record in result]
            finally:
                driver.close()

        return await asyncio.to_thread(_run)
