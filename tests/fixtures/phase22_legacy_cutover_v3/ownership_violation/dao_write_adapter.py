"""Public adapter ownership violation — direct DAO write inside a
public adapter.

The verifier must detect the ``session.add`` / ``session.commit`` call
as a direct DAO write inside a public adapter module.

This is a *fixture* that the test will use to verify the public
adapter modules detect ownership violations. The actual public adapter
modules are referenced via the verifier's public_adapter_modules set.
"""


def adapter_function():
    """Trivial example referenced by the ownership test."""
    pass
