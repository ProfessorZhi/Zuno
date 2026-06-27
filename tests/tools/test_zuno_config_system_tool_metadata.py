import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICE_API_ROOT = REPO_ROOT / "src" / "backend"
BACKEND_ROOT = REPO_ROOT / "src/backend"
for runtime_root in (str(BACKEND_ROOT),):
    if runtime_root not in sys.path:
        sys.path.insert(0, runtime_root)


def test_zuno_system_tool_payload_exposes_strategy_install_and_config_metadata():
    from zuno.api.v1 import config as config_api

    payload = config_api._build_system_tool_payload("send_email", {})
    assert payload["tool_kind"] == "smtp_protocol"
    assert payload["strategy_code"] == "profile_credentials"
    assert payload["install_requirement"]["code"] == "none"
    assert payload["config_requirement"]["code"] == "credential_profiles"

    payload = config_api._build_system_tool_payload("convert_to_pdf", {})
    assert payload["strategy_code"] == "system_dependency_command"
    assert payload["install_requirement"]["code"] == "system_command"
    assert payload["install_requirement"]["subject"] == "libreoffice"
    assert payload["config_requirement"]["code"] == "none"

    payload = config_api._build_system_tool_payload("get_arxiv", {})
    assert payload["strategy_code"] == "builtin_internal"
    assert payload["install_requirement"]["code"] == "none"
    assert payload["config_requirement"]["code"] == "none"

    payload = config_api._build_system_tool_payload("get_weather", {})
    assert payload["strategy_code"] == "config_fields"
    assert payload["install_requirement"]["code"] == "none"
    assert payload["config_requirement"]["code"] == "fields"


def test_zuno_get_runtime_config_lists_strategy_metadata_for_system_tools(monkeypatch):
    from zuno.api.v1.config import get_runtime_config

    sample_config = {
        "tools": {
            "weather": {
                "api_key": "secret",
                "endpoint": "https://example.com/weather",
            }
        }
    }

    monkeypatch.setattr(
        "zuno.api.v1.config._load_runtime_config",
        lambda: ("config.yaml", sample_config),
    )

    response = asyncio.run(get_runtime_config(login_user=SimpleNamespace(user_id="u_test")))

    assert response.status_code == 200
    system_tools = {item["tool_name"]: item for item in response.data["system_tools"]}

    assert system_tools["send_email"]["strategy_code"] == "profile_credentials"
    assert system_tools["send_email"]["config_requirement"]["code"] == "credential_profiles"
    assert system_tools["convert_to_pdf"]["strategy_code"] == "system_dependency_command"
    assert system_tools["convert_to_pdf"]["install_requirement"]["code"] == "system_command"
    assert system_tools["get_arxiv"]["strategy_code"] == "builtin_internal"
    assert system_tools["get_arxiv"]["config_requirement"]["code"] == "none"
    assert system_tools["get_weather"]["strategy_code"] == "config_fields"
    assert system_tools["get_weather"]["config_requirement"]["code"] == "fields"


def test_zuno_get_system_tool_status_route_returns_status(monkeypatch):
    from zuno.api.v1.config import get_system_tool_status

    monkeypatch.setattr(
        "zuno.api.v1.config._load_runtime_config",
        lambda: ("config.yaml", {"tools": {"weather": {"api_key": "secret", "endpoint": "https://example.com"}}}),
    )

    response = asyncio.run(get_system_tool_status("get_weather", login_user=SimpleNamespace(user_id="u_test")))

    assert response.status_code == 200
    assert response.data["tool_name"] == "get_weather"
    assert response.data["status"]["code"] == "ready"
