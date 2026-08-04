"""Contract fixture 3: ``legacy_runner`` injection in production source.

The factory pattern below matches the live Phase08 cutover controller
usage: a callable named ``legacy_runner`` synthesised inside a method.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Request:
    request_id: str


def legacy_runner(request: Request, allow_side_effect: bool) -> dict[str, Any]:
    """Legacy runtime callable injected by the cutover controller."""
    return {"runtime": "legacy", "request": request.request_id}


def dispatch(request: Request) -> dict[str, Any]:
    """Legacy_runner dispatch helper."""
    return legacy_runner(request, allow_side_effect=False)