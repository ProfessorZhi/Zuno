import asyncio

from zuno.core.runtime.agent_runtime import AgentRuntime


def test_agent_runtime_uses_single_agent_graph_by_default():
    class FakeDomainGraph:
        def build_initial_state(self, **kwargs):
            return {"mode": "single", **kwargs}

        async def ainvoke(self, state):
            return {"status": "completed", "mode": "single", "state": state}

    class FakeMultiGraph:
        def build_initial_state(self, **kwargs):
            return {"mode": "multi", **kwargs}

        async def ainvoke(self, state):
            return {"status": "completed", "mode": "multi", "state": state}

    runtime = AgentRuntime(graph=FakeDomainGraph(), multi_agent_graph=FakeMultiGraph())

    result = asyncio.run(
        runtime.run_domain_qa(
            user_id="u1",
            agent_id="a1",
            dialog_id="d1",
            query="review contract",
            knowledge_ids=["kb_1"],
            runtime_settings={"knowledge_config": {"retrieval_settings": {}}},
            domain_pack={"id": "contract_review"},
        )
    )

    assert result["mode"] == "single"


def test_agent_runtime_uses_multi_agent_graph_when_enabled_in_runtime_settings():
    class FakeDomainGraph:
        def build_initial_state(self, **kwargs):
            return {"mode": "single", **kwargs}

        async def ainvoke(self, state):
            return {"status": "completed", "mode": "single", "state": state}

    class FakeMultiGraph:
        def build_initial_state(self, **kwargs):
            return {"mode": "multi", **kwargs}

        async def ainvoke(self, state):
            return {"status": "completed", "mode": "multi", "state": state}

    runtime = AgentRuntime(graph=FakeDomainGraph(), multi_agent_graph=FakeMultiGraph())

    result = asyncio.run(
        runtime.run_domain_qa(
            user_id="u1",
            agent_id="a1",
            dialog_id="d1",
            query="review contract",
            knowledge_ids=["kb_1"],
            runtime_settings={"knowledge_config": {"retrieval_settings": {"multi_agent_enabled": True}}},
            domain_pack={"id": "contract_review"},
        )
    )

    assert result["mode"] == "multi"


def test_agent_runtime_uses_multi_agent_graph_when_enabled_in_domain_pack():
    class FakeDomainGraph:
        def build_initial_state(self, **kwargs):
            return {"mode": "single", **kwargs}

        async def ainvoke(self, state):
            return {"status": "completed", "mode": "single", "state": state}

    class FakeMultiGraph:
        def build_initial_state(self, **kwargs):
            return {"mode": "multi", **kwargs}

        async def ainvoke(self, state):
            return {"status": "completed", "mode": "multi", "state": state}

    runtime = AgentRuntime(graph=FakeDomainGraph(), multi_agent_graph=FakeMultiGraph())

    result = asyncio.run(
        runtime.run_domain_qa(
            user_id="u1",
            agent_id="a1",
            dialog_id="d1",
            query="review contract",
            knowledge_ids=["kb_1"],
            runtime_settings={"knowledge_config": {"retrieval_settings": {}}},
            domain_pack={"id": "contract_review", "multi_agent_enabled": True},
        )
    )

    assert result["mode"] == "multi"
