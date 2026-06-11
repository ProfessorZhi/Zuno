from typing import List

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from zuno.api.services.dialog import DialogService
from zuno.api.services.history import HistoryService
from zuno.prompts.completion import SYSTEM_PROMPT
from zuno.schema.completion import CompletionReq
from zuno.utils.helpers import (
    build_completion_history_messages,
    build_completion_system_prompt,
    build_completion_user_input,
)


class CompletionService:
    @staticmethod
    async def create_chat_agent(req: CompletionReq, login_user_id: str):
        from zuno.core.agents.general_agent import AgentConfig, GeneralAgent

        db_config = await DialogService.get_agent_by_dialog_id(dialog_id=req.dialog_id)
        agent_config = AgentConfig(**db_config)
        agent_config.user_id = login_user_id
        agent_config.dialog_id = req.dialog_id
        agent_config.multi_agent_enabled = bool(req.multi_agent_enabled)

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
