from zuno.core.graphs.domain_qa_graph import DomainQAGraph
from zuno.core.graphs.multi_agent_supervisor_graph import MultiAgentSupervisorGraph


class AgentRuntime:
    def __init__(
        self,
        graph: DomainQAGraph | None = None,
        multi_agent_graph: MultiAgentSupervisorGraph | None = None,
    ):
        self.graph = graph or DomainQAGraph()
        self.multi_agent_graph = multi_agent_graph or MultiAgentSupervisorGraph()

    @staticmethod
    def _use_multi_agent_runtime(runtime_settings: dict | None, domain_pack: dict | None) -> bool:
        runtime_settings = runtime_settings or {}
        retrieval_settings = (
            (runtime_settings.get("knowledge_config") or {}).get("retrieval_settings") or {}
        )
        if bool(runtime_settings.get("multi_agent_enabled")):
            return True
        if bool(retrieval_settings.get("multi_agent_enabled")):
            return True
        if bool((domain_pack or {}).get("multi_agent_enabled")):
            return True
        return False

    def create_domain_qa_state(self, **kwargs):
        return self.graph.build_initial_state(**kwargs)

    def create_multi_agent_state(self, **kwargs):
        return self.multi_agent_graph.build_initial_state(**kwargs)

    async def run_domain_qa(self, **kwargs):
        runtime_settings = kwargs.get("runtime_settings")
        domain_pack = kwargs.get("domain_pack")
        if self._use_multi_agent_runtime(runtime_settings, domain_pack):
            state = self.create_multi_agent_state(**kwargs)
            return await self.multi_agent_graph.ainvoke(state)

        state = self.create_domain_qa_state(**kwargs)
        return await self.graph.ainvoke(state)


__all__ = ["AgentRuntime"]
