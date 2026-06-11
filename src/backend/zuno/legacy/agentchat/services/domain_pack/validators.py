from __future__ import annotations

from agentchat.services.domain_pack.models import DomainPack


class DomainPackValidator:
    REQUIRED_FIELDS = {
        "id",
        "name",
        "version",
        "description",
        "schema",
        "extraction_prompt",
        "retrieval_policy",
    }

    @classmethod
    def validate_payload(cls, payload: dict) -> None:
        missing = sorted(field for field in cls.REQUIRED_FIELDS if not payload.get(field))
        if missing:
            raise ValueError(f"domain pack missing required fields: {', '.join(missing)}")

    @classmethod
    def validate_pack(cls, pack: DomainPack) -> None:
        cls.validate_payload(pack.to_dict())
