from agentchat.tools.openapi_tool.adapter import OpenAPIToolAdapter
import asyncio


def _schema(url: str):
    return {
        "openapi": "3.1.0",
        "info": {"title": "QA Echo API", "version": "1.0.0"},
        "servers": [{"url": url}],
        "paths": {
            "/echo": {
                "post": {
                    "operationId": "echoMessage",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"message": {"type": "string"}},
                                    "required": ["message"],
                                }
                            }
                        },
                    },
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }


def test_openapi_adapter_keeps_normal_base_url(monkeypatch):
    monkeypatch.setattr("os.path.exists", lambda path: False)

    adapter = OpenAPIToolAdapter(_schema("https://example.com"))

    assert adapter.base_url == "https://example.com"


def test_openapi_adapter_rewrites_localhost_inside_docker(monkeypatch):
    monkeypatch.setattr("os.path.exists", lambda path: path == "/.dockerenv")

    adapter = OpenAPIToolAdapter(_schema("http://127.0.0.1:9101"))

    assert adapter.base_url == "http://host.docker.internal:9101"


def test_openapi_adapter_supports_query_api_key(monkeypatch):
    captured = {}

    class FakeResponse:
        headers = {"content-type": "application/json"}

        def raise_for_status(self):
            return None

        def json(self):
            return {"ok": True}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def request(self, method, url, params=None, json=None, headers=None):
            captured["method"] = method
            captured["url"] = url
            captured["params"] = params or {}
            captured["headers"] = headers or {}
            return FakeResponse()

    monkeypatch.setattr("httpx.AsyncClient", FakeClient)

    adapter = OpenAPIToolAdapter(
        _schema("https://example.com"),
        auth_config={"auth_type": "APIKey", "in": "query", "name": "access_key", "data": "secret"},
    )

    result = asyncio.run(adapter.execute(_tool_name="echoMessage", message="hello"))

    assert result == {"ok": True}
    assert captured["params"]["message"] == "hello"
    assert captured["params"]["access_key"] == "secret"


def test_openapi_adapter_replaces_path_params_before_request(monkeypatch):
    captured = {}

    class FakeResponse:
        headers = {"content-type": "application/json"}

        def raise_for_status(self):
            return None

        def json(self):
            return {"ok": True}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def request(self, method, url, params=None, json=None, headers=None):
            captured["url"] = url
            return FakeResponse()

    monkeypatch.setattr("httpx.AsyncClient", FakeClient)

    adapter = OpenAPIToolAdapter(
        {
            "openapi": "3.1.0",
            "info": {"title": "Path API", "version": "1.0.0"},
            "servers": [{"url": "https://example.com"}],
            "paths": {
                "/echo/{message}": {
                    "get": {
                        "operationId": "echoPath",
                        "parameters": [
                            {"name": "message", "in": "path", "required": True, "schema": {"type": "string"}},
                        ],
                        "responses": {"200": {"description": "ok"}},
                    }
                }
            },
        }
    )

    result = asyncio.run(adapter.execute(_tool_name="echoPath", message="hello"))

    assert result == {"ok": True}
    assert captured["url"] == "https://example.com/echo/hello"


def test_openapi_connectivity_reports_missing_required_params():
    adapter = OpenAPIToolAdapter(
        {
            "openapi": "3.1.0",
            "info": {"title": "Path API", "version": "1.0.0"},
            "servers": [{"url": "https://example.com"}],
            "paths": {
                "/echo/{message}": {
                    "get": {
                        "operationId": "echoPath",
                        "parameters": [
                            {"name": "message", "in": "path", "required": True, "schema": {"type": "string"}},
                        ],
                        "responses": {"200": {"description": "ok"}},
                    }
                }
            },
        }
    )

    result = asyncio.run(adapter.test_connectivity())

    assert result["ok"] is False
    assert result["executed"] is False
    assert "message" in result["warnings"][0]
