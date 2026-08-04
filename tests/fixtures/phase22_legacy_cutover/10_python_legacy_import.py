"""Contract fixture 10: explicit Python ``from zuno.<legacy>`` import.

This file mimics the old root-alias pattern (``zuno.core``,
``zuno.services``, ...) that is forbidden in production source.
"""

from __future__ import annotations

from zuno.core import legacy_runner  # type: ignore[import-not-found]


def call_legacy() -> str:
    return legacy_runner()