from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from zuno.memory.contracts import MemoryScope


@dataclass(frozen=True, slots=True)
class EntityMemoryFact:
    fact_id: str
    scope: MemoryScope
    entity_id: str
    attribute: str
    value: str
    effective_at: str = ""
    supersedes: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class EntityMemoryStore:
    def __init__(self) -> None:
        self._facts: dict[tuple[str, str, str, str | None], EntityMemoryFact] = {}
        self._superseded: set[str] = set()

    def upsert(self, fact: EntityMemoryFact) -> EntityMemoryFact:
        key = (*_scope_key(fact.scope), fact.entity_id, fact.attribute)
        existing = self.current(
            scope=fact.scope,
            entity_id=fact.entity_id,
            attribute=fact.attribute,
        )
        supersedes = fact.supersedes or (existing.fact_id if existing else None)
        if supersedes:
            self._superseded.add(supersedes)
        stored = EntityMemoryFact(
            fact_id=fact.fact_id,
            scope=fact.scope,
            entity_id=fact.entity_id,
            attribute=fact.attribute,
            value=fact.value,
            effective_at=fact.effective_at,
            supersedes=supersedes,
            metadata=dict(fact.metadata),
        )
        self._facts[key] = stored
        return stored

    def current(self, *, scope: MemoryScope, entity_id: str, attribute: str) -> EntityMemoryFact | None:
        return self._facts.get((*_scope_key(scope), entity_id, attribute))

    def trace(self, *, scope: MemoryScope) -> dict[str, Any]:
        facts = [
            fact
            for key, fact in self._facts.items()
            if key[:4] == _scope_key(scope)
        ]
        return {
            "entity_fact_count": len(facts),
            "facts": [
                {
                    "fact_id": fact.fact_id,
                    "entity_id": fact.entity_id,
                    "attribute": fact.attribute,
                    "value": fact.value,
                    "effective_at": fact.effective_at,
                    "supersedes": fact.supersedes,
                    "superseded": fact.fact_id in self._superseded,
                }
                for fact in facts
            ],
        }


def _scope_key(scope: MemoryScope) -> tuple[str, str | None, str | None, str | None]:
    return (scope.user_id, scope.agent_id, scope.project_id, scope.thread_id)


__all__ = ["EntityMemoryFact", "EntityMemoryStore"]
