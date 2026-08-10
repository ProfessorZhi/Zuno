"""MCP / LangChain tool executor adapter.

The MCP / LangChain tool executor adapter wraps every LangChain tool
binding so that the actual ``tool.ainvoke`` call flows through the
formal ``ToolInvocationGateway``. Without this adapter, the product
runtime path calls ``binding.ainvoke`` directly, which is a real
product bypass — the dispatch never records a prepared-tool-action /
tool-attempt / tool-execution-receipt / idempotency key against the
tool runtime, so duplicate dispatches and UNKNOWN_EFFECT outcomes
cannot be reconciled against a Server-owned tool-attempt store.

The adapter is the ONLY path through which a product runtime is
allowed to invoke a LangChain ``BaseTool`` for a product MCP binding.

Authoritative call chain (product-side):

    WorkSpaceSimpleAgent / WeChatAgent (thin adapter)
        -> MCPLangChainToolAdapter.execute(args)
            -> ToolInvocationGateway.invoke_readonly(
                   tool_name=...,
                   args=...,
                   tenant_id=...,
                   workspace_id=...,
                   trace_id=...,
                   call_id=idempotency_key,
                   adapter_kind="LANGCHAIN_TOOL",
                   executor=actual_langchain_call,
                   readonly=...,
                   approval=...,
               )

The adapter never calls ``binding.ainvoke`` outside the gateway's
executor slot. Side-effect tools (WRITE_LOCAL / WRITE_EXTERNAL /
DESTRUCTIVE) MUST provide the canonical approval artifact; the gateway then handles prepared-action / approval /
budget / receipt / dispatch-certainty / reconciliation through the
ToolUnitOfWork / SecurityUnitOfWork / InfrastructureUnitOfWork.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Mapping

from zuno.capability.control_plane import ToolSideEffectLevel
from zuno.capability.tool_runtime import ToolApprovalBinding, ToolInvocationGateway


ADAPTER_KIND = "LANGCHAIN_TOOL"


@dataclass(frozen=True, slots=True)
class MCPLangChainToolAdapterContext:
    """Static context the adapter binds from the canonical runtime.

    The adapter is constructed once per binding per session, with the
    Server-owned tenant / workspace / principal / trace identity. The
    binding has its own declared ``side_effect_level`` and its
    ``idempotency_key`` is derived from the product session + run_id +
    step_run_id so duplicate deliveries are correctly identified.
    """

    tenant_id: str
    workspace_id: str
    principal_id: str
    run_id: str
    step_run_id: str
    trace_id: str
    side_effect_level: ToolSideEffectLevel

    def idempotency_key(self, *, tool_name: str, salt: str = "") -> str:
        return (
            f"idem:{self.tenant_id}:{self.workspace_id}:"
            f"{self.run_id}:{self.step_run_id}:{tool_name}:{salt}"
        )


class MCPLangChainToolAdapter:
    """Adapter that routes a LangChain tool binding through the gateway."""

    def __init__(
        self,
        *,
        binding: Any,
        gateway: ToolInvocationGateway,
        context: MCPLangChainToolAdapterContext,
        tool_name: str,
        approved_artifact: Mapping[str, Any] | None = None,
    ) -> None:
        self._binding = binding
        self._gateway = gateway
        self._context = context
        self._tool_name = tool_name
        self._approved_artifact = approved_artifact

    @property
    def tool_name(self) -> str:
        return self._tool_name

    @property
    def adapter_kind(self) -> str:
        return ADAPTER_KIND

    def is_read_only(self) -> bool:
        return self._context.side_effect_level in {
            ToolSideEffectLevel.NONE,
            ToolSideEffectLevel.READ,
        }

    def is_approved(self) -> bool:
        # Side-effect tools require an explicit approval artifact bound
        # from the Server-owned approval flow. Without it, the gateway
        # records FAILED with ``approval_missing`` and refuses to
        # dispatch.
        return self._approved_artifact is not None

    async def execute(
        self,
        args: Mapping[str, Any],
        *,
        salt: str = "",
    ) -> tuple[Any | None, str, str]:
        """Invoke the underlying LangChain tool through the gateway.

        Returns ``(result, receipt_id, status)``. ``status`` is one of
        ``ok``, ``replayed``, ``blocked``. ``result`` is ``None`` for
        ``blocked``.
        """
        if not self.is_read_only() and not self.is_approved():
            return (
                None,
                "",
                "blocked",
            )

        call_id = self._context.idempotency_key(
            tool_name=self._tool_name, salt=salt
        )

        binding = self._binding

        async def _actual_call() -> Any:
            return await binding.ainvoke(dict(args))

        result, gateway_receipt = await self._gateway.invoke_readonly(
            tool_name=self._tool_name,
            args=dict(args),
            tenant_id=self._context.tenant_id,
            workspace_id=self._context.workspace_id,
            trace_id=self._context.trace_id,
            call_id=call_id,
            adapter_kind=ADAPTER_KIND,
            executor=_actual_call,
            readonly=self.is_read_only(),
            approval=ToolApprovalBinding.from_artifact(self._approved_artifact),
        )
        return (result, gateway_receipt.receipt_id, gateway_receipt.status)


class MCPToolExecutorAdapterRegistry:
    """In-process registry of ``MCPLangChainToolAdapter`` instances.

    The registry is populated by the composition root when it builds
    the workspace tool control plane. The composition root is the
    Server-owned binding site — adapters are NEVER constructed inside
    a request path. A lookup that misses is a fail-closed
    ``MCPToolAdapterNotBound`` and the runtime surfaces it as a
    deterministic block before any ``tool.ainvoke`` call.
    """

    def __init__(self) -> None:
        self._adapters: dict[str, MCPLangChainToolAdapter] = {}

    def register(self, tool_id: str, adapter: MCPLangChainToolAdapter) -> None:
        self._adapters[tool_id] = adapter

    def lookup(self, tool_id: str) -> MCPLangChainToolAdapter:
        adapter = self._adapters.get(tool_id)
        if adapter is None:
            raise MCPToolAdapterNotBound(
                f"MCPToolExecutorAdapter not bound for tool_id={tool_id!r}"
            )
        return adapter

    def has(self, tool_id: str) -> bool:
        return tool_id in self._adapters

    def keys(self) -> tuple[str, ...]:
        return tuple(self._adapters.keys())


class MCPToolAdapterNotBound(RuntimeError):
    """Raised when a tool call has no registered MCP / LangChain adapter.

    The runtime must never call a product tool without going through
    a registered adapter. This is the canonical fail-closed token for
    missing gateway ownership.
    """


def build_mcp_langchain_tool_adapter(
    *,
    binding: Any,
    gateway: ToolInvocationGateway,
    tenant_id: str,
    workspace_id: str,
    principal_id: str,
    run_id: str,
    step_run_id: str,
    trace_id: str,
    side_effect_level: ToolSideEffectLevel,
    tool_name: str | None = None,
    approved_artifact: Mapping[str, Any] | None = None,
) -> MCPLangChainToolAdapter:
    """Convenience builder used by the workspace composition root."""
    resolved_tool_name = (
        tool_name or str(getattr(binding, "name", "") or "")
    )
    if not resolved_tool_name:
        raise ValueError(
            "MCPLangChainToolAdapter requires a non-empty tool_name"
        )
    context = MCPLangChainToolAdapterContext(
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        principal_id=principal_id,
        run_id=run_id,
        step_run_id=step_run_id,
        trace_id=trace_id,
        side_effect_level=side_effect_level,
    )
    return MCPLangChainToolAdapter(
        binding=binding,
        gateway=gateway,
        context=context,
        tool_name=resolved_tool_name,
        approved_artifact=approved_artifact,
    )


__all__ = [
    "ADAPTER_KIND",
    "MCPLangChainToolAdapter",
    "MCPLangChainToolAdapterContext",
    "MCPToolAdapterNotBound",
    "MCPToolExecutorAdapterRegistry",
    "build_mcp_langchain_tool_adapter",
]


# Internal type aliases used by tests and integration modules.
LangChainToolExecutor = Callable[[Mapping[str, Any]], Awaitable[Any]]
