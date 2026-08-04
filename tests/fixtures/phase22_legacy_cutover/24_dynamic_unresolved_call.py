"""Contract fixture 24: dynamic call site that the AST cannot resolve.

The verifier MUST classify this as ``AUDIT_UNRESOLVED`` because no
static resolution is possible.
"""

from __future__ import annotations

from typing import Any


def dispatch(payload: dict[str, Any]) -> dict[str, Any]:
    target = payload.get("target")
    method = getattr(target, "execute", None)
    return method() if callable(method) else {"unresolved": True}