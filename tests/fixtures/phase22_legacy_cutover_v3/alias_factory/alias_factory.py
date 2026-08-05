"""Alias factory fixture — module-level assignment alias whose target
class cannot be proven statically.

The verifier must surface this as AUDIT_UNRESOLVED.
"""

from tests.fixtures.phase22_legacy_cutover_v3.clean.clean_runtime import CleanRuntimeAdapter  # noqa: E402


Runtime = CleanRuntimeAdapter


def build_via_alias(*args, **kwargs):
    return Runtime(**kwargs)
