"""Compatibility module for legacy ``zuno.middleware`` imports."""

from __future__ import annotations

import importlib
import sys

__path__: list[str] = []

_trace_id_module = importlib.import_module("zuno.platform.middleware.trace_id_middleware")
_white_list_module = importlib.import_module("zuno.platform.middleware.white_list_middleware")

sys.modules[f"{__name__}.trace_id_middleware"] = _trace_id_module
sys.modules[f"{__name__}.white_list_middleware"] = _white_list_module

TraceIDMiddleware = _trace_id_module.TraceIDMiddleware
WhitelistMiddleware = _white_list_module.WhitelistMiddleware

__all__ = ["TraceIDMiddleware", "WhitelistMiddleware"]
