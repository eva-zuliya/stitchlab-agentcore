from mcp.server.fastmcp import FastMCP

# Initialize the MCP server with host and port
mcp = FastMCP("Simple MCP Server", host="0.0.0.0", port=8000)

# Define a simple tool (non-streaming)
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b