"""PHASE22 (Slice C) — fixture: MCP Admin / Control Plane surface.

Must be classified as ``MCP_ADMIN_CONTROL_PLANE`` and NOT flagged as a
tool bypass. The fixture exercises legitimate admin / lifecycle / CRUD
surfaces — server bootstrap, connection lifecycle, config CRUD, admin
management, health. None of these are reachable from a Product Run
execution chain.

The verifier must NOT flag any of the call sites in this file as
``tool_bypass_*`` / ``REAL_PRODUCT_BYPASS``. The intent is to prove
that the hardened verifier recognises the admin / control-plane shape
without resorting to path substring Allowlists.
"""


class McpServerLifecycle:
    """Admin-only MCP server bootstrap / lifecycle surface."""

    def __init__(self, *, config):
        self._config = config

    def bootstrap(self):
        # Server lifecycle is admin — not a Product Tool invocation.
        return {"status": "bootstrapped", "config": self._config}

    def shutdown(self):
        return {"status": "shutdown"}


class McpConfigCrud:
    """Admin-only MCP configuration CRUD."""

    def __init__(self, *, store):
        self._store = store

    def upsert_config(self, *, key, value):
        self._store.put(key, value)
        return {"key": key, "value": value}

    def delete_config(self, *, key):
        self._store.pop(key, None)
        return {"key": key, "deleted": True}


class McpHealthCheck:
    """Admin-only MCP health endpoint."""

    def __init__(self, *, client):
        self._client = client

    def ping(self):
        # Health probes call admin endpoints, not Product Tools.
        return self._client.health.check()