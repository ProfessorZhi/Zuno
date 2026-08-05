"""Dynamic Runtime construction via ``getattr`` — UNRESOLVED.

The verifier cannot statically resolve ``getattr(module, "SomeRuntime")``
to a specific class name. The dynamic loader retrieves a Runtime-shaped
class whose identity cannot be proven. The verifier must classify this
as ``UNRESOLVED`` because the target type is opaque.
"""


def get_dynamic_agent():
    module = __import__("synthetic.module", fromlist=[""])
    cls = getattr(module, "SomeRuntime")
    return cls()


def load_via_globals():
    cls = globals()["WorkSpaceSimpleAgent"]()
    return cls
