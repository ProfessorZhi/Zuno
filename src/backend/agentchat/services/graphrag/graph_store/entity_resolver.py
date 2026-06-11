from __future__ import annotations


class EntityResolver:
    def resolve(self, entities: list[dict]) -> list[dict]:
        seen: set[str] = set()
        resolved: list[dict] = []
        for entity in entities:
            name = str(entity.get("name") or "").strip().lower()
            if not name or name in seen:
                continue
            seen.add(name)
            resolved.append(entity)
        return resolved
