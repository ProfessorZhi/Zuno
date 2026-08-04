"""Contract fixture 18: ``dual_read`` marker in production source."""

from __future__ import annotations


def read_legacy_table() -> dict[str, str]:
    """Read from the legacy shadow table alongside the canonical one."""
    # The marker below is what the AST/text scanner looks for.
    return {"path": "dual_read marker from legacy store"}