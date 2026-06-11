from __future__ import annotations


class GraphWriter:
    def build_entity_payload(self, entity: dict, *, domain_pack_id: str | None = None) -> dict:
        payload = dict(entity)
        if domain_pack_id:
            payload.setdefault("domain_pack_id", domain_pack_id)
        return payload

    def build_relation_payload(self, relation: dict, *, domain_pack_id: str | None = None) -> dict:
        payload = dict(relation)
        if domain_pack_id:
            payload.setdefault("domain_pack_id", domain_pack_id)
        return payload
