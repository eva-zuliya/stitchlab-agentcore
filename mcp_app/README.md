# MCP Server Application

This directory contains the MCP (Model Context Protocol) server application that provides tools to the agent factory.

## Structure

- `app.py` - MCP server definition with tools
- `TESTING.md` - Testing guide for the MCP server

## Integration with Agent Factory

The MCP server is automatically discovered and used by the `AgentFactory` in `runtime/factory.py` when:

1. **MCP_URL is configured** in `agent/config.py`:
   ```python
   MCP_URL: Optional[str] = 'http://localhost:8000/mcp'
   ```

2. **MCP server is running**:
   ```bash
   python mcp_server.py
   ```

3. **Factory initialization** - The factory will:
   - Connect to the MCP server at startup
   - Fetch all available tools
   - Cache them for use by agents
   - Optionally filter tools if `MCP_TOOLS` is specified

## Tool Filtering

To allow only specific tools from the MCP server, set `MCP_TOOLS` in `agent/config.py`:

```python
MCP_TOOLS: Optional[list[str]] = ['add', 'count_stream']  # Only allow these tools
```

If `MCP_TOOLS` is `None`, all tools from the MCP server will be available.

## Adding New Tools

To add a new tool to the MCP server:

1. Edit `mcp_app/app.py`
2. Add a new function decorated with `@mcp.tool()`
3. Restart the MCP server
4. The factory will automatically discover the new tool on next initialization

Example:
```python
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b
```

## Running

Start the MCP server:
```bash
python mcp_server.py
```

The server will be available at `http://localhost:8000/mcp`

