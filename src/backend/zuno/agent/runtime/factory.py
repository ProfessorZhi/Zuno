from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tempfile

from zuno.agent.runtime.configuration import RuntimeFactoryConfig
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.sqlite_store import SQLiteAgentRunStore
from zuno.agent.runtime.store import AgentRunStore


@dataclass(frozen=True, slots=True)
class RuntimeAssembly:
    dependencies: RuntimeDependencies
    store: AgentRunStore


class RuntimeDependencyFactory:
    def __init__(self, config: RuntimeFactoryConfig | None = None) -> None:
        self.config = config or RuntimeFactoryConfig()

    @classmethod
    def for_completion(
        cls,
        *,
        store: AgentRunStore | None = None,
        sqlite_path: Path | None = None,
        knowledge_index_runtime: object | None = None,
    ) -> RuntimeAssembly:
        factory = cls(RuntimeFactoryConfig(sqlite_path=sqlite_path, knowledge_index_runtime=knowledge_index_runtime))
        return factory.build(store=store)

    @classmethod
    def for_workspace_task(
        cls,
        *,
        store: AgentRunStore | None = None,
        sqlite_path: Path | None = None,
        knowledge_index_runtime: object | None = None,
    ) -> RuntimeAssembly:
        factory = cls(RuntimeFactoryConfig(sqlite_path=sqlite_path, knowledge_index_runtime=knowledge_index_runtime))
        return factory.build(store=store)

    def build(self, *, store: AgentRunStore | None = None) -> RuntimeAssembly:
        return RuntimeAssembly(
            dependencies=self.dependencies(),
            store=store or SQLiteAgentRunStore(self._sqlite_path()),
        )

    def dependencies(self) -> RuntimeDependencies:
        return RuntimeDependencies(
            model_gateway=self._model_gateway(),
            memory_engine=self._memory_engine(),
            knowledge_runtime=self._knowledge_runtime(),
            tool_control_plane=self._tool_control_plane(),
        )

    def _sqlite_path(self) -> Path:
        if self.config.sqlite_path is not None:
            return self.config.sqlite_path
        return Path(tempfile.gettempdir()) / "zuno_unified_agent_runtime.db"

    def _model_gateway(self) -> object | None:
        if not self.config.enable_default_model_gateway:
            return None
        from zuno.platform.model_gateway import build_default_model_gateway

        return build_default_model_gateway()

    def _memory_engine(self) -> object | None:
        if not self.config.enable_memory:
            return None
        from zuno.memory.engine import MemoryEngine

        return MemoryEngine()

    def _knowledge_runtime(self) -> object | None:
        if self.config.knowledge_index_runtime is None:
            return None
        from zuno.knowledge.agentic import CorrectiveAgenticRetrievalRuntime

        return CorrectiveAgenticRetrievalRuntime(index_runtime=self.config.knowledge_index_runtime)

    def _tool_control_plane(self) -> object | None:
        if not self.config.enable_local_tool_runtime:
            return None
        from zuno.capability.runtime import build_default_tool_control_plane_runtime

        return build_default_tool_control_plane_runtime()


__all__ = ["RuntimeAssembly", "RuntimeDependencyFactory"]
