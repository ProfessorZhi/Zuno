from mcp.server.fastmcp import FastMCP


mcp = FastMCP("qa-echo-mcp")


@mcp.tool()
def qa_mcp_ping(message: str) -> str:
    """Echo a QA marker for MCP smoke tests."""
    return f"QA_MCP_ECHO:{message}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
