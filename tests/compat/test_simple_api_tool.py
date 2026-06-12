from agentchat.services.simple_api_tool import (
    build_openapi_schema_from_simple_config,
    build_remote_api_assist_draft_agentic,
    build_remote_api_assist_draft,
    normalize_remote_api_auth_config,
)
from agentchat.schema.tool import RemoteApiAssistReq, SimpleApiConfig
from agentchat.services import simple_api_tool
import asyncio


def test_build_remote_api_assist_draft_from_endpoint_and_query_key():
    draft = build_remote_api_assist_draft(
        RemoteApiAssistReq(
            endpoint_url="https://api.ipstack.com/check?access_key=demo",
            auth_type="api_key_query",
            api_key="secret",
            api_key_name="access_key",
            display_name="IPStack",
            description="lookup current ip",
        )
    )

    assert draft.simple_api_config.base_url == "https://api.ipstack.com"
    assert draft.simple_api_config.path == "/check"
    assert draft.auth_config["auth_type"] == "APIKey"
    assert draft.auth_config["in"] == "query"
    assert draft.auth_config["name"] == "access_key"
    assert all(param.name != "access_key" for param in draft.simple_api_config.params)


def test_build_openapi_schema_from_simple_config():
    schema = build_openapi_schema_from_simple_config(
        SimpleApiConfig(
            base_url="https://example.com",
            path="/echo/{id}",
            method="GET",
            operation_id="lookupEcho",
            summary="Echo",
            params=[
                {"name": "id", "in": "path", "required": True, "type": "string"},
                {"name": "lang", "in": "query", "required": False, "type": "string"},
            ],
        )
    )

    assert schema["servers"][0]["url"] == "https://example.com"
    operation = schema["paths"]["/echo/{id}"]["get"]
    assert operation["operationId"] == "lookupEcho"
    assert {item["name"] for item in operation["parameters"]} == {"id", "lang"}


def test_normalize_remote_api_auth_config_supports_api_key_variants():
    assert normalize_remote_api_auth_config(
        {"type": "api_key_query", "token": "secret", "key_name": "access_key"}
    ) == {
        "auth_type": "APIKey",
        "data": "secret",
        "in": "query",
        "name": "access_key",
    }


def test_build_remote_api_assist_draft_from_docs_url(monkeypatch):
    docs_text = """
    Quickstart Guide
    Base URL: http://api.ipstack.com/
    Standard IP Lookup
    http://api.ipstack.com/134.201.250.155?access_key=YOUR_ACCESS_KEY&fields=ip,location
    """

    monkeypatch.setattr(simple_api_tool, "_fetch_docs_page", lambda _: ("", docs_text))

    draft = build_remote_api_assist_draft(
        RemoteApiAssistReq(
            docs_url="https://ipstack.com/documentation",
            api_key="secret",
        )
    )

    assert draft.simple_api_config.base_url == "http://api.ipstack.com"
    assert draft.simple_api_config.path == "/134.201.250.155"
    assert draft.auth_config["auth_type"] == "APIKey"
    assert draft.auth_config["in"] == "query"
    assert draft.auth_config["name"] == "access_key"
    assert draft.display_name == "ipstack"
    assert draft.description
    assert {param.name for param in draft.simple_api_config.params} == {"fields"}


def test_build_remote_api_assist_prefers_docs_endpoint_when_endpoint_url_is_docs_page(monkeypatch):
    docs_map = {
        "https://docs.apilayer.com/ipstack/docs/quickstart-guide": (
            '<a href="/ipstack/docs/getting-started">Getting Started</a>',
            "Quickstart Guide Base URL: http://api.ipstack.com/ Requester IP Lookup "
            "http://api.ipstack.com/check?access_key=YOUR_ACCESS_KEY",
        ),
        "https://docs.apilayer.com/ipstack/docs/getting-started": (
            '<a href="/ipstack/docs/ipstack-api-v-1-0-0">OpenAPI</a>',
            "Getting Started access_key Requester IP Lookup http://api.ipstack.com/check?access_key=YOUR_ACCESS_KEY",
        ),
        "https://docs.apilayer.com/ipstack/docs/ipstack-api-v-1-0-0": (
            "",
            "OpenAPI /check?access_key=YOUR_ACCESS_KEY GET",
        ),
    }

    monkeypatch.setattr(simple_api_tool, "_fetch_docs_page", lambda url: docs_map[url])

    draft = build_remote_api_assist_draft(
        RemoteApiAssistReq(
            endpoint_url="https://docs.apilayer.com/ipstack/docs/quickstart-guide",
            docs_urls=list(docs_map.keys()),
            api_key="secret",
        )
    )

    assert draft.simple_api_config.base_url == "http://api.ipstack.com"
    assert draft.simple_api_config.path == "/check"
    assert draft.auth_config["auth_type"] == "APIKey"
    assert draft.auth_config["name"] == "access_key"


def test_fetch_docs_page_uses_browser_fallback_when_requests_fails(monkeypatch):
    class BrokenResponse:
        def raise_for_status(self):
            raise RuntimeError("ssl eof")

    monkeypatch.setattr(simple_api_tool.requests, "get", lambda *args, **kwargs: BrokenResponse())
    monkeypatch.setattr(
        simple_api_tool,
        "_fetch_docs_page_with_browser",
        lambda url: (
            '<a href="/marketstack/docs/getting-started">Getting Started</a>',
            "Quickstart Base URL http://api.marketstack.com/v1/tickers?access_key=YOUR_ACCESS_KEY",
        ),
    )

    html, text = simple_api_tool._fetch_docs_page("https://docs.apilayer.com/marketstack/docs/api-documentation")

    assert "getting-started" in html
    assert "api.marketstack.com" in text


def test_fetch_docs_page_uses_browser_fallback_for_react_shell(monkeypatch):
    class ShellResponse:
        text = '<html><body><div id="root"></div><script src="/app.js"></script></body></html>'

        def raise_for_status(self):
            return None

    monkeypatch.setattr(simple_api_tool.requests, "get", lambda *args, **kwargs: ShellResponse())
    monkeypatch.setattr(
        simple_api_tool,
        "_fetch_docs_page_with_browser",
        lambda url: (
            "<main>Rendered docs</main>",
            "Rendered docs Base URL http://api.marketstack.com/v1/tickers?access_key=YOUR_ACCESS_KEY",
        ),
    )

    _html, text = simple_api_tool._fetch_docs_page("https://docs.apilayer.com/marketstack/docs/api-documentation")

    assert text.startswith("Rendered docs")


def test_agentic_remote_api_assist_fills_from_docs_and_api_key(monkeypatch):
    monkeypatch.setattr(
        simple_api_tool,
        "_collect_docs_text_bundle",
        lambda urls: {
            "_source_text": "Marketstack API docs. Tickers endpoint GET http://api.marketstack.com/v1/tickers. "
            "Authenticate with access_key query parameter. The tickers endpoint returns a list of supported ticker symbols. "
            "Optional query parameters include exchange for filtering by stock exchange, limit for page size, and offset for pagination. "
            "Use GET requests against the API host, not the documentation host.",
            "warnings": [],
        },
    )

    async def fake_agent_infer(*, docs_urls, docs_text, req, docs_analysis):
        assert req.api_key == "actual-token-123"
        assert "actual-token-123" not in simple_api_tool._build_remote_api_agent_prompt(
            docs_urls=docs_urls,
            docs_text=docs_text,
            req=req,
            docs_analysis=docs_analysis,
        )
        return {
            "display_name": "marketstack tickers",
            "description": "List marketstack ticker symbols.",
            "endpoint_url": "http://api.marketstack.com/v1/tickers",
            "method": "GET",
            "auth_type": "api_key_query",
            "api_key_name": "access_key",
            "params": [
                {"name": "access_key", "in": "query", "required": True, "description": "API key", "type": "string"},
                {"name": "exchange", "in": "query", "required": False, "description": "Exchange code", "type": "string"},
            ],
        }

    monkeypatch.setattr(simple_api_tool, "_infer_remote_api_draft_with_agent", fake_agent_infer)

    draft = asyncio.run(
        build_remote_api_assist_draft_agentic(
            RemoteApiAssistReq(
                docs_url="https://docs.apilayer.com/marketstack/docs/api-documentation",
                api_key="actual-token-123",
            )
        )
    )

    assert draft.simple_api_config.base_url == "http://api.marketstack.com"
    assert draft.simple_api_config.path == "/v1/tickers"
    assert draft.auth_config["auth_type"] == "APIKey"
    assert draft.auth_config["in"] == "query"
    assert draft.auth_config["name"] == "access_key"
    assert draft.auth_config["data"] == "actual-token-123"
    assert {param.name for param in draft.simple_api_config.params} == {"exchange"}


def test_agentic_remote_api_assist_times_out_with_clear_message(monkeypatch):
    monkeypatch.setattr(simple_api_tool, "REMOTE_API_AGENT_TIMEOUT_SECONDS", 0.01)
    monkeypatch.setattr(
        simple_api_tool,
        "_collect_docs_text_bundle",
        lambda urls: {
            "_source_text": "Marketstack API docs. "
            "Tickers endpoint GET http://api.marketstack.com/v1/tickers. "
            "Authenticate with access_key query parameter. " * 20,
            "warnings": [],
        },
    )

    async def slow_agent_infer(**kwargs):
        await asyncio.sleep(1)
        return {}

    monkeypatch.setattr(simple_api_tool, "_infer_remote_api_draft_with_agent", slow_agent_infer)

    try:
        asyncio.run(
            build_remote_api_assist_draft_agentic(
                RemoteApiAssistReq(
                    docs_url="https://docs.apilayer.com/marketstack/docs/api-documentation",
                    api_key="secret",
                )
            )
        )
    except ValueError as err:
        assert "Agent" in str(err)
        assert "curl" in str(err)
    else:
        raise AssertionError("expected slow agent inference to time out")


def test_agentic_remote_api_assist_warns_about_required_business_params(monkeypatch):
    monkeypatch.setattr(
        simple_api_tool,
        "_collect_docs_text_bundle",
        lambda urls: {
            "_source_text": "Marketstack EOD endpoint GET http://api.marketstack.com/v1/eod. "
            "Authenticate with access_key query parameter. The endpoint requires symbols. " * 10,
            "warnings": [],
        },
    )

    async def fake_agent_infer(**kwargs):
        return {
            "display_name": "marketstack eod",
            "description": "查询 marketstack 每日收盘行情数据。",
            "endpoint_url": "http://api.marketstack.com/v1/eod",
            "method": "GET",
            "auth_type": "api_key_query",
            "api_key_name": "access_key",
            "params": [
                {"name": "access_key", "in": "query", "required": True, "description": "API key", "type": "string"},
                {"name": "symbols", "in": "query", "required": True, "description": "Ticker symbols", "type": "string"},
            ],
        }

    monkeypatch.setattr(simple_api_tool, "_infer_remote_api_draft_with_agent", fake_agent_infer)

    draft = asyncio.run(
        build_remote_api_assist_draft_agentic(
            RemoteApiAssistReq(
                docs_url="https://docs.apilayer.com/marketstack/docs/api-documentation",
                api_key="secret",
            )
        )
    )

    assert any("symbols" in warning for warning in draft.warnings)
    assert {param.name for param in draft.simple_api_config.params} == {"symbols"}


def test_agentic_remote_api_assist_keeps_agent_probe_args(monkeypatch):
    monkeypatch.setattr(
        simple_api_tool,
        "_collect_docs_text_bundle",
        lambda urls: {
            "_source_text": "Marketstack EOD endpoint GET http://api.marketstack.com/v1/eod. "
            "Authenticate with access_key query parameter. Example symbols=AAPL. " * 10,
            "warnings": [],
        },
    )

    async def fake_agent_infer(**kwargs):
        return {
            "display_name": "marketstack eod",
            "description": "查询 marketstack 每日收盘行情数据。",
            "endpoint_url": "http://api.marketstack.com/v1/eod",
            "method": "GET",
            "auth_type": "api_key_query",
            "api_key_name": "access_key",
            "params": [
                {"name": "symbols", "in": "query", "required": True, "description": "Ticker symbols", "type": "string"},
            ],
            "probe_args": {"symbols": "AAPL", "access_key": "should-not-survive", "unknown": "ignored"},
        }

    monkeypatch.setattr(simple_api_tool, "_infer_remote_api_draft_with_agent", fake_agent_infer)

    draft = asyncio.run(
        build_remote_api_assist_draft_agentic(
            RemoteApiAssistReq(
                docs_url="https://docs.apilayer.com/marketstack/docs/api-documentation",
                api_key="secret",
            )
        )
    )

    assert draft.probe_args == {"symbols": "AAPL"}
    assert any("生成测试值" in warning for warning in draft.warnings)


def test_agentic_remote_api_assist_does_not_fallback_when_docs_are_insufficient(monkeypatch):
    monkeypatch.setattr(
        simple_api_tool,
        "_collect_docs_text_bundle",
        lambda urls: {
            "_source_text": "",
            "endpoint_url": "http://api.marketstack.com/v1/tickers",
            "auth_type": "api_key_query",
            "api_key_name": "access_key",
            "warnings": ["docs fetch failed"],
        },
    )

    async def should_not_call_agent(**kwargs):
        raise AssertionError("agent should not run without enough document text")

    monkeypatch.setattr(simple_api_tool, "_infer_remote_api_draft_with_agent", should_not_call_agent)

    try:
        asyncio.run(
            build_remote_api_assist_draft_agentic(
                RemoteApiAssistReq(
                    docs_url="https://docs.apilayer.com/marketstack/docs/api-documentation",
                    api_key="secret",
                )
            )
        )
    except ValueError as err:
        assert "文档正文不足" in str(err)
        assert "curl" in str(err)
    else:
        raise AssertionError("expected insufficient docs to raise instead of using rule fallback")


def test_agentic_remote_api_assist_rejects_openapi_spec_url_as_endpoint(monkeypatch):
    monkeypatch.setattr(
        simple_api_tool,
        "_collect_docs_text_bundle",
        lambda urls: {
            "_source_text": "OpenAPI spec URL https://api.swaggerhub.com/apis/apilayer-863/MarketstackAPIv2/2.0.0/swagger.json "
            "Marketstack documentation mentions access_key authentication and tickers data. The rendered documentation includes "
            "many sections about end of day prices, intraday prices, tickers, exchanges, currencies, pagination, limits, "
            "and account access, but the agent must still avoid treating the SwaggerHub specification file as the business API endpoint.",
            "warnings": [],
        },
    )

    async def fake_agent_infer(**kwargs):
        return {
            "display_name": "marketstack",
            "description": "Wrongly selected spec URL.",
            "endpoint_url": "https://api.swaggerhub.com/apis/apilayer-863/MarketstackAPIv2/2.0.0/swagger.json",
            "method": "GET",
            "auth_type": "api_key_query",
            "api_key_name": "access_key",
            "params": [],
        }

    monkeypatch.setattr(simple_api_tool, "_infer_remote_api_draft_with_agent", fake_agent_infer)

    try:
        asyncio.run(
            build_remote_api_assist_draft_agentic(
                RemoteApiAssistReq(
                    docs_url="https://docs.apilayer.com/marketstack/docs/api-documentation",
                    api_key="secret",
                )
            )
        )
    except ValueError as err:
        assert "规格文件" in str(err) or "文档" in str(err)
    else:
        raise AssertionError("expected spec URL to be rejected as an API endpoint")


def test_agentic_remote_api_assist_rejects_missing_auth_location_when_api_key_provided(monkeypatch):
    monkeypatch.setattr(
        simple_api_tool,
        "_collect_docs_text_bundle",
        lambda urls: {
            "_source_text": "Marketstack API documentation with enough text about tickers, pagination, exchanges, "
            "end of day data, intraday data, currencies, and API access. It describes response fields, pagination, "
            "limits, sorting, exchange filtering, and several resource groups, but no explicit authentication location "
            "such as query access_key, x-api-key header, or bearer token.",
            "warnings": [],
        },
    )

    async def fake_agent_infer(**kwargs):
        return {
            "display_name": "marketstack tickers",
            "description": "List marketstack tickers.",
            "endpoint_url": "http://api.marketstack.com/v1/tickers",
            "method": "GET",
            "auth_type": "none",
            "api_key_name": "",
            "params": [],
        }

    monkeypatch.setattr(simple_api_tool, "_infer_remote_api_draft_with_agent", fake_agent_infer)

    try:
        asyncio.run(
            build_remote_api_assist_draft_agentic(
                RemoteApiAssistReq(
                    docs_url="https://docs.apilayer.com/marketstack/docs/api-documentation",
                    api_key="secret",
                )
            )
        )
    except ValueError as err:
        assert "API Key" in str(err)
        assert "Query" in str(err)
    else:
        raise AssertionError("expected missing API key auth location to be rejected")


def test_agentic_remote_api_assist_rejects_missing_generated_description(monkeypatch):
    monkeypatch.setattr(
        simple_api_tool,
        "_collect_docs_text_bundle",
        lambda urls: {
            "_source_text": "Marketstack tickers API documentation. The endpoint returns supported stock ticker symbols "
            "with exchange filtering, pagination, and metadata fields. Authentication uses access_key as a query parameter. "
            "The API is useful for discovering available symbols before requesting market prices.",
            "warnings": [],
        },
    )

    async def fake_agent_infer(**kwargs):
        return {
            "display_name": "marketstack tickers",
            "description": "",
            "endpoint_url": "http://api.marketstack.com/v1/tickers",
            "method": "GET",
            "auth_type": "api_key_query",
            "api_key_name": "access_key",
            "params": [],
        }

    monkeypatch.setattr(simple_api_tool, "_infer_remote_api_draft_with_agent", fake_agent_infer)

    try:
        asyncio.run(
            build_remote_api_assist_draft_agentic(
                RemoteApiAssistReq(
                    docs_url="https://docs.apilayer.com/marketstack/docs/api-documentation",
                    api_key="secret",
                )
            )
        )
    except ValueError as err:
        assert "描述" in str(err)
        assert "Agent" in str(err)
    else:
        raise AssertionError("expected missing generated description to be rejected")


def test_agentic_remote_api_assist_ignores_frontend_placeholder_description(monkeypatch):
    monkeypatch.setattr(
        simple_api_tool,
        "_collect_docs_text_bundle",
        lambda urls: {
            "_source_text": "Marketstack tickers API documentation. The endpoint returns supported stock ticker symbols "
            "with exchange filtering, pagination, and metadata fields. Authentication uses access_key as a query parameter. "
            "The API is useful for discovering available symbols before requesting market prices.",
            "warnings": [],
        },
    )

    async def fake_agent_infer(**kwargs):
        return {
            "display_name": "marketstack tickers",
            "description": "查询 marketstack 支持的股票代码列表，可按交易所筛选并用于后续行情数据请求。",
            "endpoint_url": "http://api.marketstack.com/v1/tickers",
            "method": "GET",
            "auth_type": "api_key_query",
            "api_key_name": "access_key",
            "params": [],
        }

    monkeypatch.setattr(simple_api_tool, "_infer_remote_api_draft_with_agent", fake_agent_infer)

    draft = asyncio.run(
        build_remote_api_assist_draft_agentic(
            RemoteApiAssistReq(
                docs_url="https://docs.apilayer.com/marketstack/docs/api-documentation",
                api_key="secret",
                description="调用 api.marketstack.com/v1/tickers",
            )
        )
    )

    assert draft.description == "查询 marketstack 支持的股票代码列表，可按交易所筛选并用于后续行情数据请求。"
