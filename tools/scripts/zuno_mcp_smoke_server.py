from mcp.server.fastmcp import FastMCP


mcp = FastMCP("zuno_smoke")


@mcp.tool()
def echo_text(text: str) -> str:
    """Return the provided text for MCP connectivity smoke tests."""
    return text


@mcp.tool()
def public_source_note() -> str:
    """Return the public sources used by the Zuno connectivity test."""
    return "Open-Meteo docs: https://open-meteo.com/en/docs; GitHub REST repos docs: https://docs.github.com/rest/repos/repos"


if __name__ == "__main__":
    mcp.run()
