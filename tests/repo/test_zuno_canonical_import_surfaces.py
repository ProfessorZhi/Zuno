from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


CANONICAL_MODULE_SPECS = [
    "zuno.agent.core.models.manager",
    "zuno.api.dto.common",
    "zuno.api.router",
    "zuno.api.services.knowledge",
    "zuno.api.v1.workspace",
    "zuno.capability.mcp.servers.remote_proxy.main",
    "zuno.capability.tools.send_email.cli",
    "zuno.platform.common.file_utils",
    "zuno.platform.common.runtime_observability",
    "zuno.platform.database.metadata",
    "zuno.platform.database.models.knowledge_file",
    "zuno.platform.middleware.trace_id_middleware",
    "zuno.platform.middleware.white_list_middleware",
    "zuno.platform.services.application.knowledge",
    "zuno.platform.services.graphrag.query_service",
    "zuno.platform.services.graphrag.retriever",
    "zuno.platform.services.queue.runner",
    "zuno.platform.services.rag.handler",
    "zuno.platform.services.rag.retrieval",
    "zuno.platform.services.rag.vector_db",
    "zuno.platform.services.retrieval.fusion",
    "zuno.platform.services.retrieval.orchestrator",
    "zuno.platform.services.retrieval.planner",
    "zuno.platform.services.storage",
]


def test_canonical_module_specs_resolve_without_legacy_guard_suite() -> None:
    for module_name in CANONICAL_MODULE_SPECS:
        spec = importlib.util.find_spec(module_name)
        assert spec is not None, module_name
        assert spec.origin is None or "/src/backend/zuno/" in Path(spec.origin).as_posix()


def test_canonical_config_resources_point_at_target_runtime_paths() -> None:
    resource_names = ["tool.json", "avatars.json", "mcp_server.json"]
    for resource_name in resource_names:
        resource_path = REPO_ROOT / "src/backend/zuno/platform/config" / resource_name
        assert resource_path.exists()

        payload = json.loads(resource_path.read_text(encoding="utf-8"))
        serialized = json.dumps(payload, ensure_ascii=False)
        assert "zuno/capability/mcp/servers/remote_proxy/main.py" in serialized or resource_name != "mcp_server.json"
        assert "zuno/mcp_servers/remote_proxy/main.py" not in serialized


def test_canonical_config_example_is_the_only_runtime_config_template() -> None:
    config_example = REPO_ROOT / "src/backend/zuno/platform/config/config.example.yaml"
    assert config_example.exists()
    assert "database:" in config_example.read_text(encoding="utf-8")
