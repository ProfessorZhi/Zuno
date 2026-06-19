import asyncio

from zuno.settings import app_settings


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
                        MERGE (e:Entity {name: $name, knowledge_id: $knowledge_id, knowledge_file_id: $knowledge_file_id})
                        SET e.type = $type,
                            e.domain_pack_id = $domain_pack_id,
                            e.index_version = $index_version,
                            e.status = $status,
                            e.source_chunk_id = $source_chunk_id,
                            e.document_hash = $document_hash,
                            e.chunk_hash = $chunk_hash
                        """,
                        {
                            "name": entity.get("name", ""),
                            "knowledge_id": entity.get("knowledge_id", ""),
                            "knowledge_file_id": entity.get("knowledge_file_id", ""),
                            "type": entity.get("type", "entity"),
                            "domain_pack_id": entity.get("domain_pack_id"),
                            "index_version": entity.get("index_version"),
                            "status": entity.get("status"),
                            "source_chunk_id": entity.get("source_chunk_id"),
                            "document_hash": entity.get("document_hash"),
                            "chunk_hash": entity.get("chunk_hash"),
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
                        MERGE (s:Entity {name: $source, knowledge_id: $knowledge_id, knowledge_file_id: $knowledge_file_id})
                        MERGE (t:Entity {name: $target, knowledge_id: $knowledge_id, knowledge_file_id: $knowledge_file_id})
                        MERGE (s)-[r:RELATES_TO {type: $relation_type, knowledge_file_id: $knowledge_file_id}]->(t)
                        SET r.chunk_id = $chunk_id,
                            r.domain_pack_id = $domain_pack_id,
                            r.index_version = $index_version,
                            r.status = $status,
                            r.source_chunk_id = $source_chunk_id,
                            r.document_hash = $document_hash,
                            r.chunk_hash = $chunk_hash,
                            s.domain_pack_id = COALESCE($domain_pack_id, s.domain_pack_id),
                            s.index_version = COALESCE($index_version, s.index_version),
                            s.status = COALESCE($status, s.status),
                            s.source_chunk_id = COALESCE($source_chunk_id, s.source_chunk_id),
                            s.document_hash = COALESCE($document_hash, s.document_hash),
                            s.chunk_hash = COALESCE($chunk_hash, s.chunk_hash),
                            t.domain_pack_id = COALESCE($domain_pack_id, t.domain_pack_id),
                            t.index_version = COALESCE($index_version, t.index_version),
                            t.status = COALESCE($status, t.status),
                            t.source_chunk_id = COALESCE($source_chunk_id, t.source_chunk_id),
                            t.document_hash = COALESCE($document_hash, t.document_hash),
                            t.chunk_hash = COALESCE($chunk_hash, t.chunk_hash)
                        """,
                        {
                            "source": relation.get("source", ""),
                            "target": relation.get("target", ""),
                            "knowledge_id": relation.get("knowledge_id", ""),
                            "knowledge_file_id": relation.get("knowledge_file_id", ""),
                            "relation_type": relation.get("relation_type", "related_to"),
                            "chunk_id": relation.get("chunk_id", ""),
                            "domain_pack_id": relation.get("domain_pack_id"),
                            "index_version": relation.get("index_version"),
                            "status": relation.get("status"),
                            "source_chunk_id": relation.get("source_chunk_id"),
                            "document_hash": relation.get("document_hash"),
                            "chunk_hash": relation.get("chunk_hash"),
                        },
                    )
            finally:
                driver.close()

        await asyncio.to_thread(_run)

    async def delete_by_knowledge_file(self, knowledge_file_id: str, knowledge_id: str):
        def _run():
            driver = self._driver()
            try:
                with driver.session(database=self.database) as session:
                    session.run(
                        """
                        MATCH (e:Entity {knowledge_id: $knowledge_id, knowledge_file_id: $knowledge_file_id})
                        DETACH DELETE e
                        """,
                        {
                            "knowledge_file_id": knowledge_file_id,
                            "knowledge_id": knowledge_id,
                        },
                    )
            finally:
                driver.close()

        await asyncio.to_thread(_run)

    async def delete_by_source_chunk(self, knowledge_file_id: str, knowledge_id: str, source_chunk_id: str):
        def _run():
            driver = self._driver()
            try:
                with driver.session(database=self.database) as session:
                    session.run(
                        """
                        MATCH (e:Entity {
                          knowledge_id: $knowledge_id,
                          knowledge_file_id: $knowledge_file_id,
                          source_chunk_id: $source_chunk_id
                        })
                        DETACH DELETE e
                        """,
                        {
                            "knowledge_file_id": knowledge_file_id,
                            "knowledge_id": knowledge_id,
                            "source_chunk_id": source_chunk_id,
                        },
                    )
            finally:
                driver.close()

        await asyncio.to_thread(_run)

    async def query_neighbors(
        self,
        entity_name: str,
        knowledge_id: str,
        hops: int = 1,
        limit: int = 10,
        domain_pack_id: str | None = None,
        index_version: str | None = None,
        status: str | None = None,
    ) -> list[dict]:
        safe_hops = max(1, min(int(hops or 1), 3))
        safe_limit = max(1, min(int(limit or 10), 50))

        def _run():
            driver = self._driver()
            try:
                with driver.session(database=self.database) as session:
                    result = session.run(
                        f"""
                        MATCH p=(e:Entity {{name: $name, knowledge_id: $knowledge_id}})-[:RELATES_TO*1..{safe_hops}]-(n:Entity {{knowledge_id: $knowledge_id}})
                        WHERE $domain_pack_id IS NULL OR (
                          e.domain_pack_id = $domain_pack_id
                          AND n.domain_pack_id = $domain_pack_id
                        )
                        AND ($index_version IS NULL OR (
                          e.index_version = $index_version
                          AND n.index_version = $index_version
                          AND ALL(rel IN relationships(p) WHERE rel.index_version = $index_version)
                        ))
                        AND ($status IS NULL OR (
                          e.status = $status
                          AND n.status = $status
                          AND ALL(rel IN relationships(p) WHERE rel.status = $status)
                        ))
                        WITH e, n, relationships(p) AS rels
                        RETURN
                          e.name AS source,
                          n.name AS target,
                          [rel IN rels WHERE rel.chunk_id IS NOT NULL AND rel.chunk_id <> "" | rel.chunk_id] AS chunk_ids
                        LIMIT $limit
                        """,
                        {
                            "name": entity_name,
                            "knowledge_id": knowledge_id,
                            "limit": safe_limit,
                            "domain_pack_id": domain_pack_id,
                            "index_version": index_version,
                            "status": status,
                        },
                    )
                    return [record.data() for record in result]
            finally:
                driver.close()

        return await asyncio.to_thread(_run)

    async def fetch_relation_edges(
        self,
        knowledge_id: str,
        *,
        index_version: str | None = None,
        status: str | None = None,
    ) -> list[dict]:
        def _run():
            driver = self._driver()
            try:
                with driver.session(database=self.database) as session:
                    result = session.run(
                        """
                        MATCH (s:Entity {knowledge_id: $knowledge_id})-[r:RELATES_TO]->(t:Entity {knowledge_id: $knowledge_id})
                        WHERE ($index_version IS NULL OR r.index_version = $index_version)
                        AND ($status IS NULL OR r.status = $status)
                        RETURN
                          s.name AS source,
                          t.name AS target,
                          r.type AS relation_type,
                          CASE
                            WHEN r.chunk_id IS NULL OR r.chunk_id = "" THEN []
                            ELSE [r.chunk_id]
                          END AS chunk_ids
                        """
                        ,
                        {
                            "knowledge_id": knowledge_id,
                            "index_version": index_version,
                            "status": status,
                        },
                    )
                    return [record.data() for record in result]
            finally:
                driver.close()

        return await asyncio.to_thread(_run)

    async def replace_communities(
        self,
        knowledge_id: str,
        communities: list,
        *,
        community_version: str = "v0",
        status: str = "ready",
    ):
        def _run():
            driver = self._driver()
            try:
                with driver.session(database=self.database) as session:
                    session.run(
                        """
                        MATCH (c:GraphCommunity {knowledge_id: $knowledge_id})
                        DETACH DELETE c
                        """,
                        {"knowledge_id": knowledge_id},
                    )
                    for community in communities:
                        payload = community.to_dict() if hasattr(community, "to_dict") else dict(community)
                        session.run(
                            """
                            MERGE (c:GraphCommunity {community_id: $community_id, knowledge_id: $knowledge_id})
                            SET c.level = $level,
                                c.report = $report,
                                c.entity_count = $entity_count,
                                c.relation_count = $relation_count,
                                c.supporting_chunks = $supporting_chunks,
                                c.community_version = $community_version,
                                c.status = $status
                            """,
                            {
                                "community_id": payload.get("community_id"),
                                "knowledge_id": knowledge_id,
                                "level": payload.get("level", 0),
                                "report": payload.get("report", ""),
                                "entity_count": len(payload.get("entities") or []),
                                "relation_count": payload.get("relation_count", 0),
                                "supporting_chunks": list(payload.get("supporting_chunks") or []),
                                "community_version": payload.get("community_version") or community_version,
                                "status": payload.get("status") or status,
                            },
                        )
                        for entity_name in payload.get("entities") or []:
                            session.run(
                                """
                                MATCH (e:Entity {name: $entity_name, knowledge_id: $knowledge_id})
                                MATCH (c:GraphCommunity {community_id: $community_id, knowledge_id: $knowledge_id})
                                MERGE (e)-[:IN_COMMUNITY]->(c)
                                """,
                                {
                                    "entity_name": entity_name,
                                    "community_id": payload.get("community_id"),
                                    "knowledge_id": knowledge_id,
                                },
                            )
            finally:
                driver.close()

        await asyncio.to_thread(_run)

    async def fetch_communities(
        self,
        knowledge_id: str,
        *,
        status: str | None = None,
        community_version: str | None = None,
    ) -> list[dict]:
        def _run():
            driver = self._driver()
            try:
                with driver.session(database=self.database) as session:
                    result = session.run(
                        """
                        MATCH (c:GraphCommunity {knowledge_id: $knowledge_id})
                        WHERE ($status IS NULL OR c.status = $status)
                        AND ($community_version IS NULL OR c.community_version = $community_version)
                        RETURN
                          c.community_id AS community_id,
                          c.knowledge_id AS knowledge_id,
                          c.level AS level,
                          c.report AS report,
                          c.relation_count AS relation_count,
                          c.supporting_chunks AS supporting_chunks,
                          c.community_version AS community_version
                        ORDER BY c.community_id
                        """,
                        {
                            "knowledge_id": knowledge_id,
                            "status": status,
                            "community_version": community_version,
                        },
                    )
                    rows = [record.data() for record in result]
                    for row in rows:
                        entity_result = session.run(
                            """
                            MATCH (e:Entity {knowledge_id: $knowledge_id})-[:IN_COMMUNITY]->(c:GraphCommunity {community_id: $community_id, knowledge_id: $knowledge_id})
                            RETURN e.name AS entity_name
                            ORDER BY e.name
                            """,
                            {
                                "knowledge_id": knowledge_id,
                                "community_id": row.get("community_id"),
                            },
                        )
                        row["entities"] = [entity["entity_name"] for entity in entity_result]
                    return rows
            finally:
                driver.close()

        return await asyncio.to_thread(_run)


__all__ = ["Neo4jClient"]
