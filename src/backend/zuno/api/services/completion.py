from typing import AsyncIterator, List

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from zuno.api.services.history import HistoryService
from zuno.api.services.product import ProductService
from zuno.api.dto.completion import CompletionReq
from zuno.platform.contracts import canonical_sha256
from zuno.platform.common.helpers import (
    build_completion_history_messages,
    build_completion_system_prompt,
    build_completion_user_input,
)
from zuno.platform.resources.prompts.completion import SYSTEM_PROMPT
from zuno.platform.services.workspace.single_controller_runtime import BlockedConfiguration


class CompletionService:
    @classmethod
    async def stream_product_command(
        cls,
        *,
        req: CompletionReq,
        login_user_id: str,
        tenant_id: str = "",
    ) -> AsyncIterator[dict]:
        product_runtime_record = cls.record_product_runtime_request(
            req=req,
            login_user_id=login_user_id,
            tenant_id=tenant_id,
        )
        yield {
            "type": "product_runtime_record",
            "data": product_runtime_record,
        }
        if product_runtime_record.get("status") == "blocked":
            return
        yield {
            "type": "runtime_accepted",
            "data": {
                "runtime_topology": "product-command-outbox",
                **product_runtime_record,
            },
        }

    @staticmethod
    def record_product_runtime_request(
        *,
        req: CompletionReq,
        login_user_id: str,
        tenant_id: str = "",
    ) -> dict:
        workspace_id = str(getattr(req, "workspace_id", "") or "completion")
        request_hash = canonical_sha256(
            {
                "runtime_surface": "completion",
                "dialog_id": req.dialog_id,
                "workspace_id": workspace_id,
                "user_input": req.user_input,
                "product_mode": req.product_mode,
                "query_method": req.query_method,
            }
        )[:24]
        # The Server-owned
        # tenant identity MUST come from the validated authentication
        # context. The caller (API layer) is responsible for resolving
        # the trusted tenant and passing it explicitly. ``req.tenant_id``
        # is untrusted request-body data and is NEVER used here. A
        # missing / synthetic / default tenant fails closed with the
        # canonical token BEFORE we touch the submitter.
        resolved_tenant = (tenant_id or "").strip()
        if (
            not resolved_tenant
            or resolved_tenant.startswith("user:")
            or resolved_tenant == "tenant:default"
        ):
            raise BlockedConfiguration(
                "BLOCKED_CONFIGURATION: tenant_identity_not_available — "
                "completion product surface requires Server-owned tenant_id "
                "from the validated auth context; user:* / tenant:default "
                "fallbacks are forbidden"
            )
        active_agent_version_id = ProductService.runtime_agent_version_id(
            surface="completion",
            tenant_id=resolved_tenant,
            workspace_id=workspace_id,
        )
        try:
            result = ProductService.submit_runtime_request(
                tenant_id=resolved_tenant,
                workspace_id=workspace_id,
                conversation_id=req.dialog_id,
                principal_id=login_user_id,
                active_agent_version_id=active_agent_version_id,
                client_request_id=f"completion:{req.dialog_id}:{request_hash}",
                runtime_request_ref=f"completion-runtime-request:{req.dialog_id}:{request_hash}",
                raw_intent_ref=f"completion-intent:{req.dialog_id}:{request_hash}",
                payload={
                    "runtime_surface": "completion",
                    "dialog_id": req.dialog_id,
                    "user_input_hash": canonical_sha256({"user_input": req.user_input}),
                    "product_mode": req.product_mode,
                    "query_method": req.query_method,
                },
                bootstrap_runtime_agent=True,
                runtime_surface="completion",
            )
        except Exception as exc:
            return {
                "status": "blocked",
                "runtime_surface": "completion",
                "request_hash": request_hash,
                "product_runtime_recorded": False,
                "failure_type": type(exc).__name__,
                "reason": str(exc),
            }
        return {
            "status": result.status,
            "runtime_surface": "completion",
            "request_hash": request_hash,
            "product_runtime_recorded": True,
            "command_id": result.command_id,
            "receipt_id": result.receipt_id,
            "projection_event_id": result.projection.projection_event_id,
            "stream_cursor_id": result.projection.stream_cursor_id,
            "available_action_tokens": [action.action_token_id for action in result.available_actions],
        }

    @staticmethod
    async def build_history_text(*, agent_config, original_user_input: str, dialog_id: str) -> str:
        if agent_config.enable_memory:
            from zuno.platform.services.memory.client import memory_client

            history = await memory_client.search(query=original_user_input, run_id=dialog_id)
            return "\n".join(msg.get("memory", "") for msg in history.get("results", []))

        history_records = await HistoryService.select_history(dialog_id=dialog_id)
        return build_completion_history_messages(history_records)

    @classmethod
    async def prepare_messages(
        cls,
        *,
        req: CompletionReq,
        agent_config,
    ) -> tuple[str, List[BaseMessage]]:
        original_user_input = req.user_input
        req.user_input = build_completion_user_input(file_url=req.file_url, user_input=req.user_input)

        system_prompt = agent_config.system_prompt if agent_config.system_prompt.strip() else SYSTEM_PROMPT
        history_text = await cls.build_history_text(
            agent_config=agent_config,
            original_user_input=original_user_input,
            dialog_id=req.dialog_id,
        )
        system_prompt = build_completion_system_prompt(system_prompt, history_text)

        messages: List[BaseMessage] = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=req.user_input),
        ]
        return original_user_input, messages

    @staticmethod
    async def save_memory_turn(*, agent_config, original_user_input: str, response_content: str, dialog_id: str) -> None:
        if not agent_config.enable_memory:
            return

        from zuno.platform.services.memory.client import memory_client

        await memory_client.add(
            messages=[
                {"role": "user", "content": original_user_input},
                {"role": "assistant", "content": response_content},
            ],
            run_id=dialog_id,
        )


__all__ = ["CompletionService"]
