"""Factory pattern fixture — UNRESOLVED.

The factory function returns a class instance whose type cannot be proven
statically. The verifier must treat this as UNRESOLVED because the
constructor site looks like a class name but the verifier cannot link
``make_agent()`` back to a known runtime class.
"""


class WorkSpaceSimpleAgent:
    def __init__(self, *, model_config):
        self._model_config = model_config


def make_agent(*, model_config):
    """Factory that returns a Runtime class instance.

    The verifier cannot statically resolve ``make_agent()`` to a known
    runtime class, so the candidate is UNRESOLVED.
    """
    return WorkSpaceSimpleAgent(model_config=model_config)


def build_via_factory(model_config):
    return make_agent(model_config=model_config)
