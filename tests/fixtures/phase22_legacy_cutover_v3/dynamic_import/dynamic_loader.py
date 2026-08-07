"""Dynamic import fixture — ``getattr`` / ``__import__`` that targets a
Runtime class.

The verifier cannot statically resolve the target; it must surface
this as AUDIT_UNRESOLVED.
"""


def load_dynamic_agent():
    module = __import__("synthetic.module", fromlist=[""])
    cls = getattr(module, "SomeRuntime")
    return cls()


def load_via_globals():
    cls = globals()["CleanRuntimeAdapter"]()
    return cls
