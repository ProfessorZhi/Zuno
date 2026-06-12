from agentchat.api.services.tool import ToolService
from agentchat.database import ToolTable


def test_serialize_tool_sets_runtime_type_for_cli_user_defined_tool():
    tool = ToolTable(
        name="user_tool_cli",
        display_name="CLI Tool",
        description="cli",
        logo_url="logo",
        user_id="1",
        is_user_defined=True,
        auth_config={
            "mode": "cli",
            "cli_config": {
                "tool_dir": "zuno_echo_tool",
                "command": "python",
            },
        },
    )

    payload = ToolService._serialize_tool(tool)

    assert payload["runtime_type"] == "cli"

