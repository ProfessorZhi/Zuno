"""Compatibility alias for legacy ``zuno.settings`` imports."""

import sys
from importlib import import_module

_target = import_module("zuno.platform.settings")
sys.modules[__name__] = _target
