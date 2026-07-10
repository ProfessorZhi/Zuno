from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StructuredClaim:
    claim_id: str
    text: str
    required_citation: bool = True


class ClaimExtractor:
    def extract(self, *, goal: str, draft: str) -> tuple[StructuredClaim, ...]:
        text = draft.strip() or goal.strip()
        return (StructuredClaim(claim_id="claim:1", text=text, required_citation=True),)


__all__ = ["ClaimExtractor", "StructuredClaim"]
