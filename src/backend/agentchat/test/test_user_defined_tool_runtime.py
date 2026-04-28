from agentchat.services.user_defined_tool_runtime import build_stored_tool_auth_config


def test_build_stored_tool_auth_config_preserves_source_metadata_for_remote_api():
    result = build_stored_tool_auth_config(
        "remote_api",
        {"type": "api_key_query", "name": "access_key", "token": "demo-key"},
        None,
        {"base_url": "http://api.ipstack.com", "path": "/check"},
        {
            "endpoint_url": "http://api.ipstack.com/check",
            "docs_url": "https://docs.apilayer.com/ipstack/docs/quickstart-guide",
            "docs_urls": [
                "https://docs.apilayer.com/ipstack/docs/quickstart-guide",
                "https://docs.apilayer.com/ipstack/docs/getting-started",
            ],
            "sample_curl": "curl \"http://api.ipstack.com/check?access_key=demo-key\"",
        },
    )

    assert result["mode"] == "remote_api"
    assert result["source_metadata"]["endpoint_url"] == "http://api.ipstack.com/check"
    assert len(result["source_metadata"]["docs_urls"]) == 2


def test_build_stored_tool_auth_config_preserves_source_metadata_for_cli():
    result = build_stored_tool_auth_config(
        "cli",
        None,
        {"command": "uvx my-cli", "tool_dir": "cli_tools/my-cli"},
        None,
        {
            "github_url": "https://github.com/example/my-cli",
            "docs_url": "https://example.com/docs",
            "local_path": "cli_tools/my-cli",
            "notes": "install with uvx",
        },
    )

    assert result["mode"] == "cli"
    assert result["cli_config"]["command"] == "uvx my-cli"
    assert result["source_metadata"]["github_url"] == "https://github.com/example/my-cli"
