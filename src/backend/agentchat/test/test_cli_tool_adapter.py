from pathlib import Path


def test_cli_tool_adapter_resolves_repo_local_cli_tools_root(monkeypatch, tmp_path):
    from agentchat.tools.cli_tool.adapter import CLIToolAdapter

    repo_root = tmp_path / "repo"
    tool_dir = repo_root / "tools" / "cli" / "echo_tool"
    tool_dir.mkdir(parents=True)
    (tool_dir / "main.py").write_text("print('ok')", encoding="utf-8")

    monkeypatch.chdir(repo_root)

    adapter = CLIToolAdapter(
        tool_id="tool_1",
        display_name="Echo Tool",
        description="Echo input",
        cli_config={"tool_dir": "echo_tool"},
    )

    assert adapter._resolve_tool_dir() == tool_dir.resolve()


def test_cli_tool_adapter_executes_from_repo_local_cli_tools(monkeypatch, tmp_path):
    from agentchat.tools.cli_tool.adapter import CLIToolAdapter

    repo_root = tmp_path / "repo"
    tool_dir = repo_root / "tools" / "cli" / "echo_tool"
    tool_dir.mkdir(parents=True)
    script_path = tool_dir / "main.py"
    script_path.write_text(
        "import sys\nprint(f'ECHO:{sys.argv[1]}')\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(repo_root)

    adapter = CLIToolAdapter(
        tool_id="tool_2",
        display_name="Echo Tool",
        description="Echo input",
        cli_config={
            "tool_dir": "echo_tool",
            "command": "python",
            "args_template": ["main.py", "{{input}}"],
            "cwd_mode": "tool_dir",
            "timeout_ms": 5000,
        },
    )

    result = __import__("asyncio").run(adapter.execute("hello"))

    assert result == "ECHO:hello"


def test_cli_tool_adapter_runs_healthcheck_command(monkeypatch, tmp_path):
    from agentchat.tools.cli_tool.adapter import CLIToolAdapter

    repo_root = tmp_path / "repo"
    tool_dir = repo_root / "tools" / "cli" / "echo_tool"
    tool_dir.mkdir(parents=True)
    script_path = tool_dir / "health.py"
    script_path.write_text("print('CLI_OK')\n", encoding="utf-8")

    monkeypatch.chdir(repo_root)

    adapter = CLIToolAdapter(
        tool_id="tool_3",
        display_name="Echo Tool",
        description="Echo input",
        cli_config={
            "tool_dir": "echo_tool",
            "command": "python",
            "args_template": ["health.py"],
            "cwd_mode": "tool_dir",
            "timeout_ms": 5000,
            "healthcheck_command": "python health.py",
        },
    )

    result = __import__("asyncio").run(adapter.test_connectivity())

    assert result["ok"] is True
    assert result["executed"] is True
    assert "CLI_OK" in result["details"][-1]


def test_cli_tool_adapter_connectivity_without_healthcheck_is_not_ready(monkeypatch, tmp_path):
    from agentchat.tools.cli_tool.adapter import CLIToolAdapter

    repo_root = tmp_path / "repo"
    tool_dir = repo_root / "tools" / "cli" / "echo_tool"
    tool_dir.mkdir(parents=True)
    script_path = tool_dir / "main.py"
    script_path.write_text("print('ok')\n", encoding="utf-8")

    monkeypatch.chdir(repo_root)

    adapter = CLIToolAdapter(
        tool_id="tool_4",
        display_name="Echo Tool",
        description="Echo input",
        cli_config={
            "tool_dir": "echo_tool",
            "command": "python",
            "args_template": ["main.py"],
            "cwd_mode": "tool_dir",
            "timeout_ms": 5000,
        },
    )

    result = __import__("asyncio").run(adapter.test_connectivity())

    assert result["ok"] is False
    assert result["executed"] is False
    assert result["warnings"]
