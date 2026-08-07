"""PHASE22 (Slice C) — fixture: MCP Discovery / Registration surface.

Must be classified as ``MCP_DISCOVERY_REGISTRATION`` and NOT flagged as
a tool bypass. The fixture exercises legitimate discovery surfaces —
list tools / schema discovery / resource discovery / prompt discovery /
ToolCard registration / executor registration.

The verifier must NOT flag any of the call sites in this file as
``tool_bypass_*`` / ``REAL_PRODUCT_BYPASS``. The intent is to prove
that the hardened verifier recognises the discovery / registration
shape without resorting to receiver-name Allowlists.
"""


class McpToolRegistry:
    """ToolCard / executor registration surface."""

    def __init__(self):
        self._cards = {}
        self._executors = {}

    def register_executor_adapter(self, *, executor_id, execute):
        # Canonical registration site — proves ownership for downstream
        # canonical executor dispatch.
        self._executors[executor_id] = execute
        return executor_id

    def register_tool_card(self, *, card):
        self._cards[card["name"]] = card
        return card["name"]


class McpDiscovery:
    """Tool / schema / resource / prompt discovery."""

    def __init__(self, *, registry):
        self._registry = registry

    def list_tools(self):
        # Read-only discovery; not a Product Tool invocation.
        return list(self._registry._cards.keys())

    def list_resources(self):
        return []

    def list_prompts(self):
        return []

    def get_tool_schema(self, *, name):
        return self._registry._cards.get(name)