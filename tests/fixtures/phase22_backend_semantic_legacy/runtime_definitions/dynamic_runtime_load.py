"""Dynamic Runtime construction fixture — UNRESOLVED.

Uses ``getattr`` to construct a runtime class whose identity cannot be
proven statically. The verifier must classify this as
``BACKEND_PRODUCT_RUNTIME_UNRESOLVED`` because the dynamic loader can
target any class.
"""


def get_dynamic_agent():
    module = __import__("zuno.agent.runtime", fromlist=[""])
    cls = getattr(module, "SomeRuntime")
    return cls()


def load_via_globals():
    cls = globals()["AgentFromGlobals"]()
    return cls