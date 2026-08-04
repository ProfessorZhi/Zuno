"""Contract fixture 13: ``sys.modules`` alias table population."""

from __future__ import annotations

import sys
import types


class _LegacyModule(types.ModuleType):
    pass


sys.modules["zuno.legacy_aliases"] = _LegacyModule("zuno.legacy_aliases")