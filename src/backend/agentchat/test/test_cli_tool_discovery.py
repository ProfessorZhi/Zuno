from pathlib import Path
import asyncio
from types import SimpleNamespace


def test_cli_preview_local_directory_returns_recommended_candidate(monkeypatch, tmp_path):
    from agentchat.schema.tool import CLIToolPreviewReq
    from agentchat.services.cli_tool_discovery import CliToolDiscoveryService

    repo_root = tmp_path / "repo"
    tool_dir = repo_root / "tools" / "cli" / "demo_cli"
    tool_dir.mkdir(parents=True)
    (tool_dir / "README.md").write_text("# Demo CLI\n\nA demo tool.\n\n```bash\npython cli.py --help\n```", encoding="utf-8")
    (tool_dir / "cli.py").write_text("print('ok')", encoding="utf-8")

    monkeypatch.chdir(repo_root)

    result = CliToolDiscoveryService.preview_tool(CLIToolPreviewReq(tool_dir="demo_cli"))

    assert result.exists is True
    assert result.recommended is not None
    assert result.candidates
    assert result.recommended.command == "python"


def test_cli_preview_npm_package_suggests_install_and_healthcheck():
    from agentchat.schema.tool import CLIToolPreviewReq
    from agentchat.services.cli_tool_discovery import CliToolDiscoveryService

    result = CliToolDiscoveryService.preview_tool(
        CLIToolPreviewReq(
            source_type="npm_package",
            install_source="@playwright/cli",
        )
    )

    assert result.suggested_install_command == "pnpm dlx @playwright/cli"
    assert result.suggested_healthcheck_command == "pnpm dlx @playwright/cli --help"


def test_cli_preview_executable_uses_absolute_path(tmp_path):
    from agentchat.schema.tool import CLIToolPreviewReq
    from agentchat.services.cli_tool_discovery import CliToolDiscoveryService

    exe_path = tmp_path / "tool.exe"
    exe_path.write_text("binary", encoding="utf-8")

    result = CliToolDiscoveryService.preview_tool(
        CLIToolPreviewReq(
            source_type="executable",
            tool_dir=str(exe_path),
        )
    )

    assert result.exists is True
    assert result.recommended is not None
    assert result.recommended.command == str(exe_path)


def test_cli_tool_preview_request_accepts_richer_inputs_without_tool_dir():
    from agentchat.schema.tool import CLIToolPreviewReq

    req = CLIToolPreviewReq(
        source_type="python_package",
        install_source="zuno-send-email",
        command="send-email",
        doc_url="https://docs.example.com/send-email",
        local_path="F:/tools/send-email",
    )

    assert req.tool_dir == ""
    assert req.doc_url == "https://docs.example.com/send-email"
    assert req.local_path == "F:/tools/send-email"


def test_cli_preview_python_package_supports_structured_suggestions():
    from agentchat.schema.tool import CLIToolPreviewReq
    from agentchat.services.cli_tool_discovery import CliToolDiscoveryService

    result = CliToolDiscoveryService.preview(
        CLIToolPreviewReq(
            source_type="python_package",
            install_source="zuno-send-email",
            command="send-email",
            doc_url="https://docs.example.com/send-email",
        )
    )

    assert result.doc_url == "https://docs.example.com/send-email"
    assert result.install_suggestions[0].command == "pip"
    assert result.run_suggestions[0].command == "send-email"
    assert result.healthcheck_suggestions[0].healthcheck_command == "send-email --help"
    assert result.credential_mode_suggestions[0].mode == "none"
    assert result.structured_suggestions
    assert result.structured_suggestions[0].title in {"安装方式", "启动命令"}


def test_cli_preview_github_repo_accepts_github_and_docs_aliases():
    from agentchat.schema.tool import CLIToolPreviewReq
    from agentchat.services.cli_tool_discovery import CliToolDiscoveryService

    result = CliToolDiscoveryService.preview(
        CLIToolPreviewReq(
            source_type="github_repo",
            github_url="https://github.com/openai/zuno-echo-tool",
            docs_url="https://docs.example.com/zuno-echo-tool",
            notes="需要支持 Windows 安装路径。",
        )
    )

    assert result.install_source == "https://github.com/openai/zuno-echo-tool"
    assert result.doc_url == "https://docs.example.com/zuno-echo-tool"
    assert result.docs_url == "https://docs.example.com/zuno-echo-tool"
    assert result.github_url == "https://github.com/openai/zuno-echo-tool"
    assert "Windows" in (result.assist_summary or "")
    assert result.assist_sources


def test_cli_preview_endpoint_passes_full_request_to_service(monkeypatch):
    from agentchat.api.v1.tool import preview_cli_tool_directory
    from agentchat.schema.tool import CLIToolPreviewReq, CLIToolPreviewResp

    captured = {}

    def fake_preview(req):
        captured["req"] = req
        return CLIToolPreviewResp(
            tool_dir=req.tool_dir,
            source_type=req.source_type,
            install_source=req.install_source,
            doc_url=req.doc_url,
            local_path=req.local_path,
            resolved_path=req.local_path or "",
            exists=False,
            suggested_name="Echo Tool",
            display_name="Echo Tool",
            default_description="Echo tool",
            description="Echo tool",
            warnings=[],
        )

    monkeypatch.setattr(
        "agentchat.api.v1.tool.CliToolDiscoveryService.preview",
        fake_preview,
    )

    response = asyncio.run(
        preview_cli_tool_directory(
            CLIToolPreviewReq(
                source_type="github_repo",
                install_source="openai/zuno-echo-tool",
                command="zuno-echo",
                doc_url="https://docs.example.com/zuno-echo",
                local_path="F:/tools/zuno-echo",
            ),
            login_user=SimpleNamespace(user_id="u_test"),
        )
    )

    assert response.status_code == 200
    assert captured["req"].source_type == "github_repo"
    assert captured["req"].install_source == "openai/zuno-echo-tool"
    assert captured["req"].doc_url == "https://docs.example.com/zuno-echo"
    assert captured["req"].local_path == "F:/tools/zuno-echo"
