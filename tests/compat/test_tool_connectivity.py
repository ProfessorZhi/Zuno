import asyncio
from types import SimpleNamespace


def test_tool_connectivity_service_dispatches_remote_api(monkeypatch):
    from agentchat.schema.tool import SimpleApiConfig, ToolConnectivityReq
    from agentchat.services.tool_connectivity_service import ToolConnectivityService

    captured = {}

    def fake_validate_and_resolve(**kwargs):
        captured["validate"] = kwargs
        return "remote_api", {"openapi": "3.1.0", "servers": [{"url": "https://example.com"}], "paths": {"/check": {"get": {"operationId": "lookup", "responses": {"200": {"description": "ok"}}}}}}, {}

    class FakeAdapter:
        def __init__(self, openapi_schema, auth_config):
            captured["adapter_init"] = {"openapi_schema": openapi_schema, "auth_config": auth_config}

        async def test_connectivity(self, test_args=None, *, operation_id=None):
            captured["adapter_call"] = {"test_args": test_args, "operation_id": operation_id}
            return {
                "ok": True,
                "runtime_type": "remote_api",
                "summary": "ok",
                "details": ["done"],
                "warnings": [],
                "executed": True,
                "operation_id": operation_id or "lookup",
                "tested_url": "https://example.com/check",
            }

    monkeypatch.setattr("agentchat.services.tool_connectivity_service.ToolCreationService.validate_and_resolve", fake_validate_and_resolve)
    monkeypatch.setattr("agentchat.services.tool_connectivity_service.OpenAPIToolAdapter", FakeAdapter)

    req = ToolConnectivityReq(
        runtime_type="remote_api",
        auth_config={"type": "api_key_query", "token": "secret", "name": "access_key"},
        simple_api_config=SimpleApiConfig(
            base_url="https://example.com",
            path="/check",
            method="GET",
            operation_id="lookup",
        ),
        probe_operation_id="lookup",
        probe_args={"hostname": 1},
    )

    result = asyncio.run(ToolConnectivityService.test(req))

    assert result.ok is True
    assert captured["adapter_call"] == {"test_args": {"hostname": 1}, "operation_id": "lookup"}


def test_tool_connectivity_route_returns_resp_200(monkeypatch):
    from agentchat.api.v1.tool import test_tool_connectivity
    from agentchat.schema.tool import ToolConnectivityReq

    async def fake_test(_req):
        return SimpleNamespace(
            model_dump=lambda: {
                "ok": True,
                "runtime_type": "cli",
                "summary": "CLI 健康检查成功",
                "details": ["ok"],
                "warnings": [],
                "executed": True,
                "command": "python --version",
            }
        )

    monkeypatch.setattr("agentchat.api.v1.tool.ToolConnectivityService.test", fake_test)

    response = asyncio.run(
        test_tool_connectivity(
            req=ToolConnectivityReq(runtime_type="cli", cli_config={"command": "python"}),
            login_user=SimpleNamespace(user_id="u_test"),
        )
    )

    assert response.status_code == 200
    assert response.data["ok"] is True
    assert response.data["runtime_type"] == "cli"


def test_saved_tool_connectivity_route_returns_status(monkeypatch):
    from agentchat.api.v1.tool import test_saved_tool_connectivity

    async def fake_verify(_tool_id, _user_id):
        return None

    async def fake_get_tool(_tool_id):
        return SimpleNamespace(
            tool_id="tool-1",
            display_name="IPStack",
            description="demo",
            auth_config={"mode": "remote_api"},
            openapi_schema={"openapi": "3.1.0"},
            is_user_defined=True,
        )

    async def fake_test_saved_tool(_tool):
        return SimpleNamespace(
            ok=True,
            runtime_type="remote_api",
            summary="ok",
            details=["done"],
            warnings=[],
            executed=True,
            model_dump=lambda: {
                "ok": True,
                "runtime_type": "remote_api",
                "summary": "ok",
                "details": ["done"],
                "warnings": [],
                "executed": True,
            },
        )

    monkeypatch.setattr("agentchat.api.v1.tool.ToolService.verify_user_permission", fake_verify)
    monkeypatch.setattr("agentchat.api.v1.tool.ToolService.get_tool_by_id", fake_get_tool)
    monkeypatch.setattr("agentchat.api.v1.tool.ToolConnectivityService.test_saved_tool", fake_test_saved_tool)
    monkeypatch.setattr(
        "agentchat.api.v1.tool.ToolConnectivityService.to_runtime_status",
        lambda result: {"code": "ready", "label": "已就绪", "detail": result.summary, "configurable": True},
    )

    response = asyncio.run(
        test_saved_tool_connectivity(
            tool_id="tool-1",
            login_user=SimpleNamespace(user_id="u_test"),
        )
    )

    assert response.status_code == 200
    assert response.data["ok"] is True
    assert response.data["status"]["code"] == "ready"


def test_connectivity_status_for_missing_cli_healthcheck_is_runtime_input():
    from agentchat.schema.tool import ToolConnectivityResp
    from agentchat.services.tool_connectivity_service import ToolConnectivityService

    status = ToolConnectivityService.to_runtime_status(
        ToolConnectivityResp(
            ok=False,
            runtime_type="cli",
            summary="CLI healthcheck command is missing",
            warnings=["configure a probe command"],
            executed=False,
        )
    )

    assert status["code"] == "runtime_input"


def test_system_tool_connectivity_route_returns_status(monkeypatch):
    from agentchat.api.v1.tool import test_system_tool_connectivity

    async def fake_test_system_tool(_tool_name):
        return SimpleNamespace(
            ok=False,
            runtime_type="remote_api",
            summary="missing config",
            details=[],
            warnings=["api_key"],
            executed=False,
            model_dump=lambda: {
                "ok": False,
                "runtime_type": "remote_api",
                "summary": "missing config",
                "details": [],
                "warnings": ["api_key"],
                "executed": False,
            },
        )

    monkeypatch.setattr("agentchat.api.v1.tool.ToolConnectivityService.test_system_tool", fake_test_system_tool)
    monkeypatch.setattr(
        "agentchat.api.v1.tool.ToolConnectivityService.to_runtime_status",
        lambda result: {"code": "needs_config", "label": "需配置", "detail": result.summary, "configurable": True},
    )

    response = asyncio.run(
        test_system_tool_connectivity(
            tool_name="get_weather",
            login_user=SimpleNamespace(user_id="u_test"),
        )
    )

    assert response.status_code == 200
    assert response.data["executed"] is False
    assert response.data["status"]["code"] == "needs_config"
