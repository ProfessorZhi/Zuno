from pathlib import Path
import tempfile
from typing import AsyncIterator, List
from uuid import uuid4

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from zuno.api.services.dialog import DialogService
from zuno.api.services.history import HistoryService
from zuno.resources.prompts.completion import SYSTEM_PROMPT
from zuno.schema.completion import CompletionReq
from zuno.agent.runtime import RuntimeStartRequest, SQLiteAgentRunStore, UnifiedAgentRuntimeService
from zuno.utils.helpers import (
    build_completion_history_messages,
    build_completion_system_prompt,
    build_completion_user_input,
)


class CompletionService:
    _unified_runtime_store = SQLiteAgentRunStore(Path(tempfile.gettempdir()) / "zuno_completion_unified_runtime.db")

    @classmethod
    def configure_unified_runtime_store_for_tests(cls, store: SQLiteAgentRunStore) -> None:
        cls._unified_runtime_store = store

    @classmethod
    def unified_runtime_service(cls) -> UnifiedAgentRuntimeService:
        return UnifiedAgentRuntimeService(store=cls._unified_runtime_store)

    @classmethod
    async def stream_unified_runtime(
        cls,
        *,
        req: CompletionReq,
        login_user_id: str,
    ) -> AsyncIterator[dict]:
        task_id = f"completion:{req.dialog_id}:{uuid4().hex[:8]}"
        request = RuntimeStartRequest(
            run_id=f"run:{task_id}",
            thread_id=req.dialog_id,
            workspace_id=str(getattr(req, "workspace_id", "") or "completion"),
            user_id=login_user_id,
            task_id=task_id,
            trace_id=f"trace:{task_id}",
            goal=req.user_input,
        )
        for event in cls.unified_runtime_service().stream(request):
            yield {
                "type": event.event_type,
                "data": {
                    "runtime_topology": "unified_agent_runtime",
                    "run_id": event.run_id,
                    "task_id": event.task_id,
                    "trace_id": event.trace_id,
                    "node": event.node,
                    "status": event.status,
                    **dict(event.payload),
                },
            }
        snapshot = cls.unified_runtime_service().get_snapshot(task_id)
        yield {
            "type": "response_chunk",
            "data": {
                "chunk": "Unified runtime completed.",
                "runtime_topology": "unified_agent_runtime",
                "task_id": task_id,
                "finalization_status": snapshot.finalization_status if snapshot else "unknown",
            },
        }

    @staticmethod
    async def create_chat_agent(req: CompletionReq, login_user_id: str):
        from zuno.core.agents.general_agent import AgentConfig, GeneralAgent

        db_config = await DialogService.get_agent_by_dialog_id(dialog_id=req.dialog_id)
        agent_config = AgentConfig(**db_config)
        agent_config.user_id = login_user_id
        agent_config.dialog_id = req.dialog_id
        agent_config.multi_agent_enabled = bool(req.multi_agent_enabled)
        agent_config.product_mode = req.product_mode
        agent_config.query_method = req.query_method

        chat_agent = GeneralAgent(agent_config)
        await chat_agent.init_agent()
        return chat_agent, agent_config

    @staticmethod
    async def build_history_text(*, agent_config, original_user_input: str, dialog_id: str) -> str:
        if agent_config.enable_memory:
            from zuno.services.memory.client import memory_client

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

        from zuno.services.memory.client import memory_client

        await memory_client.add(
            messages=[
                {"role": "user", "content": original_user_input},
                {"role": "assistant", "content": response_content},
            ],
            run_id=dialog_id,
        )


__all__ = ["CompletionService"]
