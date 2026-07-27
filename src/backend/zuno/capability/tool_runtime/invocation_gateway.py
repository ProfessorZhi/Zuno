from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from zuno.platform.database.tool_runtime import (
    PreparedToolActionInput,
    ToolAttemptInput,
    ToolExecutionReceiptInput,
    ToolObservationInput,
    ToolUnitOfWork,
    ToolVersionInput,
)
from zuno.platform.security import redact_sensitive_payload


@dataclass(frozen=True, slots=True)
class ToolGatewayReceipt:
    status: str
    prepared_tool_action_id: str
    attempt_id: str
    receipt_id: str
    blocked_reason: str = ""


class ToolInvocationGateway:
    def __init__(self, *, unit_of_work_factory: Callable[[], ToolUnitOfWork]) -> None:
        self._unit_of_work_factory = unit_of_work_factory

    async def invoke_readonly(
        self,
        *,
        tool_name: str,
        args: dict[str, Any],
        tenant_id: str,
        workspace_id: str,
        trace_id: str,
        call_id: str,
        adapter_kind: str,
        executor: Callable[[], Awaitable[Any]],
        readonly: bool,
    ) -> tuple[Any | None, ToolGatewayReceipt]:
        prepared_id = f"prepared-tool-action:{call_id}"
        attempt_id = f"tool-attempt:{call_id}"
        receipt_id = f"tool-execution-receipt:{call_id}"
        tool_definition_id = f"tool-definition:{tool_name}"
        tool_version_id = f"tool-version:{tool_name}:v1"
        effect_level = "READ_ONLY" if readonly else "PHASE16_REQUIRED"

        with self._unit_of_work_factory() as repo:
            repo.publish_tool_version(
                ToolVersionInput(
                    tool_definition_id=tool_definition_id,
                    tool_version_id=tool_version_id,
                    tenant_id=tenant_id,
                    version_no=1,
                    input_schema={"type": "object"},
                    output_schema={"type": "object"},
                    adapter_kind=adapter_kind,
                    effect_level=effect_level,
                )
            )
            repo.record_adapter_binding(
                adapter_binding_id=f"tool-adapter-binding:{adapter_kind}:{tool_version_id}",
                tenant_id=tenant_id,
                tool_version_id=tool_version_id,
                adapter_kind=adapter_kind,
                adapter_version=f"{adapter_kind}:phase15",
                conformance_payload={"readonly": readonly, "gateway": "ToolInvocationGateway"},
            )
            repo.install_tool(
                tool_installation_id=f"tool-installation:{workspace_id}:{tool_name}",
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                tool_version_id=tool_version_id,
                policy_ref=f"tool-policy:{tool_name}:phase15",
            )
            repo.activate_tool(
                tool_activation_id=f"tool-activation:{workspace_id}:{tool_name}",
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                tool_installation_id=f"tool-installation:{workspace_id}:{tool_name}",
                expected_generation=1,
                activation_payload={"gateway": "ToolInvocationGateway", "readonly": readonly},
            )
            repo.prepare_action(
                PreparedToolActionInput(
                    prepared_tool_action_id=prepared_id,
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    tool_operation_id=f"{tool_version_id}:operation:default",
                    canonical_args=redact_sensitive_payload(args),
                    target_resources=_target_resources(args, tool_name),
                    effect_level=effect_level,
                    approval_required=False,
                    idempotency_key=call_id,
                    security_epoch_ref=f"security-epoch:{trace_id}",
                    status="READY" if readonly else "OBSOLETE",
                )
            )

        if not readonly:
            blocked_reason = "PHASE16_REQUIRED_FOR_SIDE_EFFECT_TOOL"
            self._record_terminal(
                tenant_id=tenant_id,
                prepared_id=prepared_id,
                attempt_id=attempt_id,
                receipt_id=receipt_id,
                status="FAILED",
                dispatch_certainty="NOT_DISPATCHED",
                effect_certainty="NO_EFFECT",
                adapter_kind=adapter_kind,
                payload={"blocked": True, "reason": blocked_reason},
            )
            return None, ToolGatewayReceipt("blocked", prepared_id, attempt_id, receipt_id, blocked_reason)

        try:
            result = await executor()
        except Exception as exc:
            self._record_terminal(
                tenant_id=tenant_id,
                prepared_id=prepared_id,
                attempt_id=attempt_id,
                receipt_id=receipt_id,
                status="FAILED",
                dispatch_certainty="DISPATCHED",
                effect_certainty="NO_EFFECT",
                adapter_kind=adapter_kind,
                payload={"error_type": type(exc).__name__, "error": str(exc)},
            )
            raise

        self._record_terminal(
            tenant_id=tenant_id,
            prepared_id=prepared_id,
            attempt_id=attempt_id,
            receipt_id=receipt_id,
            status="SUCCEEDED",
            dispatch_certainty="DISPATCHED",
            effect_certainty="NO_EFFECT",
            adapter_kind=adapter_kind,
            payload={"result": str(result)[:2000]},
        )
        return result, ToolGatewayReceipt("completed", prepared_id, attempt_id, receipt_id)

    def _record_terminal(
        self,
        *,
        tenant_id: str,
        prepared_id: str,
        attempt_id: str,
        receipt_id: str,
        status: str,
        dispatch_certainty: str,
        effect_certainty: str,
        adapter_kind: str,
        payload: dict[str, Any],
    ) -> None:
        with self._unit_of_work_factory() as repo:
            repo.record_attempt(
                ToolAttemptInput(
                    attempt_id=attempt_id,
                    tenant_id=tenant_id,
                    prepared_tool_action_id=prepared_id,
                    status=status,
                    dispatch_certainty=dispatch_certainty,
                    adapter_family=adapter_kind,
                    hidden_retry_count=0,
                    state_history=("STARTED", status),
                )
            )
            repo.record_observation(
                ToolObservationInput(
                    observation_id=f"tool-observation:{attempt_id}",
                    tenant_id=tenant_id,
                    attempt_id=attempt_id,
                    owner_module="08 Tool Runtime",
                    normalized_projection_owner="06 Agent Core / Planning & Control",
                    output_trusted=False,
                    schema_valid=status == "SUCCEEDED",
                    memory_write_allowed=False,
                    evidence_write_allowed=False,
                    payload=payload,
                )
            )
            repo.record_execution_receipt(
                ToolExecutionReceiptInput(
                    receipt_id=receipt_id,
                    tenant_id=tenant_id,
                    prepared_tool_action_id=prepared_id,
                    attempt_id=attempt_id,
                    status=status,
                    dispatch_certainty=dispatch_certainty,
                    effect_certainty=effect_certainty,
                    append_only_generation=1,
                    receipt_payload=payload,
                )
            )
            repo.record_bypass_guard(
                receipt_id=f"tool-bypass-guard:{attempt_id}",
                tenant_id=tenant_id,
                scope="langchain_tool_gateway",
                allowlist_count=0,
                guard_payload={"gateway": "ToolInvocationGateway", "direct_handler_bypass": False},
            )


def _target_resources(args: dict[str, Any], tool_name: str) -> tuple[str, ...]:
    resources = []
    for key in ("url", "path", "endpoint", "resource", "query"):
        value = args.get(key)
        if value:
            resources.append(str(value))
    return tuple(resources) or (f"tool://{tool_name}",)


__all__ = ["ToolGatewayReceipt", "ToolInvocationGateway"]
