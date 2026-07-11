from pathlib import Path
import tempfile
from typing import AsyncIterator, List
from uuid import uuid4

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from zuno.api.services.dialog import DialogService
from zuno.api.services.history import HistoryService
from zuno.resources.prompts.completion import SYSTEM_PROMPT
from zuno.schema.completion import CompletionReq
from zuno.agent.runtime import RuntimeDependencyFactory, RuntimeStartRequest, SQLiteAgentRunStore, UnifiedAgentRuntimeService
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
        assembly = RuntimeDependencyFactory.for_completion(store=cls._unified_runtime_store)
        return UnifiedAgentRuntimeService(store=assembly.store, dependencies=assembly.dependencies)

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
            payload = {
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
            yield payload
            if event.event_type == "runtime_node":
                yield {
                    "type": "node_started",
                    "data": {
                        "runtime_topology": "unified_agent_runtime",
                        "run_id": event.run_id,
                        "task_id": event.task_id,
                        "trace_id": event.trace_id,
                        "node": event.node,
                        "status": event.status,
                    },
                }
        snapshot = cls.unified_runtime_service().get_snapshot(task_id)
        if snapshot is not None:
            for derived_event in _derived_sse_events(snapshot):
                yield derived_event
        final_answer = _final_answer_from_snapshot(snapshot) if snapshot is not None else ""
        chunk_data = {
            "chunk": final_answer or "Unified runtime finished without a final answer.",
            "runtime_topology": "unified_agent_runtime",
            "task_id": task_id,
            "finalization_status": snapshot.finalization_status if snapshot else "unknown",
        }
        yield {
            "type": "answer_chunk",
            "data": chunk_data,
        }
        yield {
            "type": "response_chunk",
            "data": chunk_data,
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


def _final_answer_from_snapshot(snapshot) -> str:
    for observation in reversed(snapshot.observations):
        if observation.metadata.get("grounded_synthesis"):
            return str(observation.metadata.get("final_answer") or "")
    return ""


def _derived_sse_events(snapshot) -> list[dict]:
    events: list[dict] = []
    base = {
        "runtime_topology": "unified_agent_runtime",
        "run_id": snapshot.run_id,
        "task_id": snapshot.task_id,
        "trace_id": snapshot.trace_id,
    }
    for observation in snapshot.observations:
        if observation.kind == "model" and (
            observation.metadata.get("model_gateway_call") or observation.metadata.get("grounded_synthesis")
        ):
            source = "model_gateway" if observation.metadata.get("model_gateway_call") else "grounded_synthesis"
            events.append({"type": "model_call", "data": {**base, "model_call_source": source, **observation.metadata}})
        if observation.kind == "retrieval":
            events.append(
                {
                    "type": "retrieval_round",
                    "data": {
                        **base,
                        "evidence_ids": list(observation.evidence_ids),
                        "citation_ids": list(observation.citation_ids),
                        **observation.metadata,
                    },
                }
            )
        if observation.kind == "tool":
            event_type = "approval_required" if observation.status == "waiting" else "tool_call"
            events.append({"type": event_type, "data": {**base, **observation.metadata}})
        if observation.kind == "reflection":
            events.append({"type": "reflection", "data": {**base, **observation.metadata}})
        if observation.kind == "replan":
            events.append({"type": "replan", "data": {**base, **observation.metadata}})
        if observation.metadata.get("grounded_synthesis"):
            for binding in observation.metadata.get("citation_bindings", []):
                if binding.get("citation_id"):
                    events.append({"type": "citation", "data": {**base, **binding}})
    return events
