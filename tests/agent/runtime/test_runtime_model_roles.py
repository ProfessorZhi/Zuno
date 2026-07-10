from __future__ import annotations

from zuno.agent.core.agents.general_agent import AgentConfig, GeneralAgent
from zuno.platform.model_gateway import ModelGateway, MockModelProvider
from zuno.platform.model_roles import ModelRole, ROLE_DEFAULT_SLOT


class RecordingGateway(ModelGateway):
    def __init__(self) -> None:
        super().__init__(providers=[MockModelProvider()])
        self.calls: list[tuple[dict, ModelRole]] = []

    def get_chat_model(self, binding=None, *, role=ModelRole.EXECUTOR):
        normalized_role = ModelRole(role)
        self.calls.append((dict(binding or {}), normalized_role))
        return object()


def _agent_config(*, llm_id: str = "") -> AgentConfig:
    return AgentConfig(
        user_id="user-1",
        llm_id=llm_id,
        mcp_ids=[],
        knowledge_ids=[],
        tool_ids=[],
        agent_skill_ids=[],
        system_prompt="You are Zuno.",
    )


def test_general_agent_uses_model_gateway_for_default_conversation_model() -> None:
    gateway = RecordingGateway()
    agent = GeneralAgent(_agent_config(), model_gateway=gateway)

    import asyncio

    asyncio.run(agent.setup_language_model())

    assert gateway.calls == [({"model_slot": "conversation_model"}, ModelRole.EXECUTOR)]
    assert agent.conversation_model is not None


def test_general_agent_uses_model_gateway_for_user_model(monkeypatch) -> None:
    gateway = RecordingGateway()

    async def fake_get_llm_by_id(llm_id: str):
        return {
            "llm_id": llm_id,
            "model": "deepseek-chat",
            "provider": "DeepSeek",
            "api_key": "secret-key",
            "base_url": "https://api.deepseek.com",
        }

    monkeypatch.setattr("zuno.api.services.llm.LLMService.get_llm_by_id", fake_get_llm_by_id)
    agent = GeneralAgent(_agent_config(llm_id="llm-1"), model_gateway=gateway)

    import asyncio

    asyncio.run(agent.setup_language_model())

    assert gateway.calls == [
        (
            {
                "llm_id": "llm-1",
                "model": "deepseek-chat",
                "provider": "DeepSeek",
                "api_key": "secret-key",
                "base_url": "https://api.deepseek.com",
            },
            ModelRole.EXECUTOR,
        )
    ]


def test_model_roles_have_default_slots() -> None:
    assert ROLE_DEFAULT_SLOT[ModelRole.PLANNER] == "reasoning_model"
    assert ROLE_DEFAULT_SLOT[ModelRole.EXECUTOR] == "conversation_model"
    assert ROLE_DEFAULT_SLOT[ModelRole.CRITIC] == "reasoning_model"
    assert ROLE_DEFAULT_SLOT[ModelRole.SYNTHESIS] == "conversation_model"
    assert ROLE_DEFAULT_SLOT[ModelRole.TOOL_CALL] == "tool_call_model"
