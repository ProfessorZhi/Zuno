from __future__ import annotations

"""PHASE22 canonical entity / directed-relation PostgreSQL facts (Task E).

PostgreSQL is the domain fact owner for canonical entities and directed
relations. Neo4j remains an index / read-model owner only. Facts are consumed
from the formal canonical IR manifest (the frozen extractor output) — never
from ad-hoc token regexes. Every write is idempotent (unique key per
tenant/version/entity) and hash-verified. All queries are bound by
``tenant_id + workspace_id + knowledge_version_id``.
"""


import hashlib
import json
from dataclasses import dataclass
from typing import Any

from sqlalchemy import Engine, text


class EntityRelationFactError(RuntimeError):
    pass


class EntityRelationScopeMismatch(EntityRelationFactError):
    pass


@dataclass(frozen=True, slots=True)
class CanonicalEntityFact:
    entity_id: str
    tenant_id: str
    workspace_id: str
    knowledge_version_id: str
    entity_kind: str
    canonical_name: str
    source_chunk_id: str
    source_span_ref: str
    entity_hash: str
    authority_ref: str


@dataclass(frozen=True, slots=True)
class CanonicalRelationFact:
    relation_id: str
    tenant_id: str
    workspace_id: str
    knowledge_version_id: str
    from_entity_id: str
    to_entity_id: str
    relation_kind: str
    source_chunk_id: str
    source_span_ref: str
    relation_hash: str
    authority_ref: str


def entity_fact_hash(record: dict[str, Any]) -> str:
    payload = {
        "entity_id": record["entity_id"],
        "tenant_id": record["tenant_id"],
        "workspace_id": record["workspace_id"],
        "knowledge_version_id": record["knowledge_version_id"],
        "entity_kind": record["entity_kind"],
        "canonical_name": record["canonical_name"],
        "source_chunk_id": record["source_chunk_id"],
        "source_span_ref": record["source_span_ref"],
        "authority_ref": record["authority_ref"],
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def relation_fact_hash(record: dict[str, Any]) -> str:
    payload = {
        "relation_id": record["relation_id"],
        "tenant_id": record["tenant_id"],
        "workspace_id": record["workspace_id"],
        "knowledge_version_id": record["knowledge_version_id"],
        "from_entity_id": record["from_entity_id"],
        "to_entity_id": record["to_entity_id"],
        "relation_kind": record["relation_kind"],
        "source_chunk_id": record["source_chunk_id"],
        "source_span_ref": record["source_span_ref"],
        "authority_ref": record["authority_ref"],
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


class EntityRelationFactsStore:
    """Tenant/workspace/knowledge-version-scoped entity and relation facts."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    # --- write ----------------------------------------------------------------

    def record_entity_fact(
        self,
        *,
        entity_id: str,
        tenant_id: str,
        workspace_id: str,
        knowledge_version_id: str,
        entity_kind: str,
        canonical_name: str,
        source_chunk_id: str,
        source_span_ref: str,
        authority_ref: str,
    ) -> CanonicalEntityFact:
        if not str(entity_id or "").strip():
            raise EntityRelationFactError("entity_id must not be empty")
        if not str(entity_kind or "").strip():
            raise EntityRelationFactError("entity_kind must not be empty")
        if not str(canonical_name or "").strip():
            raise EntityRelationFactError("canonical_name must not be empty")
        record = {
            "entity_id": entity_id,
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "knowledge_version_id": knowledge_version_id,
            "entity_kind": entity_kind,
            "canonical_name": canonical_name,
            "source_chunk_id": source_chunk_id,
            "source_span_ref": source_span_ref,
            "authority_ref": authority_ref,
        }
        entity_hash = entity_fact_hash(record)
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO knowledge_entities(
                        entity_id, tenant_id, workspace_id, knowledge_version_id,
                        entity_kind, canonical_name, source_chunk_id,
                        source_span_ref, entity_hash, authority_ref
                    ) VALUES (
                        :entity_id, :tenant_id, :workspace_id, :knowledge_version_id,
                        :entity_kind, :canonical_name, :source_chunk_id,
                        :source_span_ref, :entity_hash, :authority_ref
                    )
                    ON CONFLICT (tenant_id, knowledge_version_id, entity_id)
                    DO NOTHING
                    """
                ),
                {**record, "entity_hash": entity_hash},
            )
        return CanonicalEntityFact(**record, entity_hash=entity_hash)

    def record_relation_fact(
        self,
        *,
        relation_id: str,
        tenant_id: str,
        workspace_id: str,
        knowledge_version_id: str,
        from_entity_id: str,
        to_entity_id: str,
        relation_kind: str,
        source_chunk_id: str,
        source_span_ref: str,
        authority_ref: str,
    ) -> CanonicalRelationFact:
        if not str(relation_id or "").strip():
            raise EntityRelationFactError("relation_id must not be empty")
        if not str(relation_kind or "").strip():
            raise EntityRelationFactError("relation_kind must not be empty")
        if from_entity_id == to_entity_id:
            raise EntityRelationFactError(
                "directed relation must not connect an entity to itself"
            )
        record = {
            "relation_id": relation_id,
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "knowledge_version_id": knowledge_version_id,
            "from_entity_id": from_entity_id,
            "to_entity_id": to_entity_id,
            "relation_kind": relation_kind,
            "source_chunk_id": source_chunk_id,
            "source_span_ref": source_span_ref,
            "authority_ref": authority_ref,
        }
        relation_hash = relation_fact_hash(record)
        with self.engine.begin() as connection:
            # from/to entities must belong to the same tenant/workspace/version
            scope_rows = connection.execute(
                text(
                    """
                    SELECT entity_id, tenant_id, workspace_id, knowledge_version_id
                    FROM knowledge_entities
                    WHERE entity_id IN (:from_entity_id, :to_entity_id)
                    """
                ),
                {
                    "from_entity_id": from_entity_id,
                    "to_entity_id": to_entity_id,
                },
            ).mappings().all()
            if len(scope_rows) != 2:
                raise EntityRelationScopeMismatch(
                    f"relation {relation_id} references entities that are not "
                    "both persisted facts"
                )
            for row in scope_rows:
                if (
                    str(row["tenant_id"]) != tenant_id
                    or str(row["workspace_id"]) != workspace_id
                    or str(row["knowledge_version_id"]) != knowledge_version_id
                ):
                    raise EntityRelationScopeMismatch(
                        f"relation {relation_id} crosses tenant/workspace/"
                        "knowledge-version scope"
                    )
            connection.execute(
                text(
                    """
                    INSERT INTO knowledge_relations(
                        relation_id, tenant_id, workspace_id, knowledge_version_id,
                        from_entity_id, to_entity_id, relation_kind,
                        source_chunk_id, source_span_ref, relation_hash, authority_ref
                    ) VALUES (
                        :relation_id, :tenant_id, :workspace_id, :knowledge_version_id,
                        :from_entity_id, :to_entity_id, :relation_kind,
                        :source_chunk_id, :source_span_ref, :relation_hash, :authority_ref
                    )
                    ON CONFLICT (tenant_id, knowledge_version_id, relation_id)
                    DO NOTHING
                    """
                ),
                {**record, "relation_hash": relation_hash},
            )
        return CanonicalRelationFact(**record, relation_hash=relation_hash)

    # --- readback ---------------------------------------------------------------

    def entity_facts(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        knowledge_version_id: str,
    ) -> tuple[CanonicalEntityFact, ...]:
        rows = self._all(
            """
            SELECT entity_id, tenant_id, workspace_id, knowledge_version_id,
                   entity_kind, canonical_name, source_chunk_id,
                   source_span_ref, entity_hash, authority_ref
            FROM knowledge_entities
            WHERE tenant_id = :tenant_id
              AND workspace_id = :workspace_id
              AND knowledge_version_id = :knowledge_version_id
            ORDER BY entity_id
            """,
            {
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "knowledge_version_id": knowledge_version_id,
            },
        )
        return tuple(CanonicalEntityFact(**dict(row)) for row in rows)

    def relation_facts(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        knowledge_version_id: str,
    ) -> tuple[CanonicalRelationFact, ...]:
        rows = self._all(
            """
            SELECT relation_id, tenant_id, workspace_id, knowledge_version_id,
                   from_entity_id, to_entity_id, relation_kind,
                   source_chunk_id, source_span_ref, relation_hash, authority_ref
            FROM knowledge_relations
            WHERE tenant_id = :tenant_id
              AND workspace_id = :workspace_id
              AND knowledge_version_id = :knowledge_version_id
            ORDER BY relation_id
            """,
            {
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "knowledge_version_id": knowledge_version_id,
            },
        )
        return tuple(CanonicalRelationFact(**dict(row)) for row in rows)

    def entity_facts_cross_tenant(
        self, *, owner_tenant_id: str, other_tenant_id: str, knowledge_version_id: str
    ) -> None:
        rows = self._all(
            """
            SELECT entity_id FROM knowledge_entities
            WHERE tenant_id = :tenant_id
              AND knowledge_version_id = :knowledge_version_id
            """,
            {"tenant_id": other_tenant_id, "knowledge_version_id": knowledge_version_id},
        )
        if rows:
            raise EntityRelationScopeMismatch(
                f"entities of tenant {owner_tenant_id} visible to tenant "
                f"{other_tenant_id}"
            )

    def relation_facts_cross_tenant(
        self, *, owner_tenant_id: str, other_tenant_id: str, knowledge_version_id: str
    ) -> None:
        rows = self._all(
            """
            SELECT relation_id FROM knowledge_relations
            WHERE tenant_id = :tenant_id
              AND knowledge_version_id = :knowledge_version_id
            """,
            {"tenant_id": other_tenant_id, "knowledge_version_id": knowledge_version_id},
        )
        if rows:
            raise EntityRelationScopeMismatch(
                f"relations of tenant {owner_tenant_id} visible to tenant "
                f"{other_tenant_id}"
            )

    # --- helpers ---------------------------------------------------------------

    def _all(self, sql: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        with self.engine.connect() as connection:
            rows = connection.execute(text(sql), params).mappings().all()
        return [dict(row) for row in rows]


__all__ = [
    "CanonicalEntityFact",
    "CanonicalRelationFact",
    "EntityRelationFactError",
    "EntityRelationFactsStore",
    "EntityRelationScopeMismatch",
    "entity_fact_hash",
    "relation_fact_hash",
]
