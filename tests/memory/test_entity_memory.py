from __future__ import annotations

from zuno.memory.entity import EntityMemoryFact, EntityMemoryStore
from zuno.memory.contracts import MemoryScope


def _scope() -> MemoryScope:
    return MemoryScope(
        user_id="user_entity",
        agent_id="agent_entity",
        project_id="workspace_entity",
        thread_id="thread_entity",
    )


def test_entity_memory_uses_scope_entity_attribute_key_and_supersedes() -> None:
    store = EntityMemoryStore()
    first = store.upsert(
        EntityMemoryFact(
            fact_id="fact_1",
            scope=_scope(),
            entity_id="project:zuno",
            attribute="preferred_model",
            value="gpt-5",
            effective_at="2026-07-01",
        )
    )
    second = store.upsert(
        EntityMemoryFact(
            fact_id="fact_2",
            scope=_scope(),
            entity_id="project:zuno",
            attribute="preferred_model",
            value="deepseek-chat",
            effective_at="2026-07-10",
        )
    )

    current = store.current(scope=_scope(), entity_id="project:zuno", attribute="preferred_model")

    assert first.supersedes is None
    assert second.supersedes == "fact_1"
    assert current.value == "deepseek-chat"
    assert store.trace(scope=_scope())["facts"][0]["supersedes"] == "fact_1"
