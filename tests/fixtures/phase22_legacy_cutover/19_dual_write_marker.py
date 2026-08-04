"""Contract fixture 19: ``dual_write`` marker in production source."""

from __future__ import annotations


def write_to_legacy_and_canonical(payload: dict[str, str]) -> None:
    """Mirror writes to the legacy store as well as the canonical store."""
    # The marker below is what the AST/text scanner looks for.
    legacy_payload = dict(payload)
    legacy_payload["dual_write"] = "true"