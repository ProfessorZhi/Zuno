"""Contract fixture 12: ``sys.meta_path`` legacy finder injection."""

from __future__ import annotations

import sys


class _LegacyFinder:
    def find_spec(self, name, path, target=None):  # pragma: no cover - fixture
        return None


sys.meta_path.append(_LegacyFinder())