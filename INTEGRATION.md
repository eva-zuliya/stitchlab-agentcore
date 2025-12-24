# MCP Server and Agent Factory Integration

This document explains how the MCP server (`mcp_app/app.py`) integrates with the agent factory (`runtime/factory.py`).

## Architecture Overview

```
┌─────────────────┐
│  MCP Server     │  (mcp_app/app.py)
│  Port: 8000     │
│  /mcp endpoint  │
└────────┬────────┘
         │ HTTP/SSE
         │
         ▼
┌─────────────────┐
│ Agent Factory   │  (runtime/factory.py)
│ - Connects to   │
│   MCP server    │
│ - Fetches tools │
│ - Caches tools  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Agent         │  (main.py)
│   - Uses tools  │
│   - Processes   │
│     requests    │
└─────────────────┘
```

## Configuration Flow

### 1. MCP Server Configuration (`mcp_app/app.py`)

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Simple MCP Server", host="0.0.0.0", port=8000)

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b
```

### 2. Agent Configuration (`agent/config.py`)

```python
class GlobalSettings(BaseSettings):
    MCP_URL: Optional[str] = 'http://localhost:8000/mcp'
    MCP_TOOLS: Optional[list[str]] = None  # None = all tools, or ['add'] = only 'add'
```

### 3. Factory Configuration (`main.py`)

```python
FACTORY_CONFIG = AgentFactoryConfig(
    system_prompt=SYSTEM_PROMPT,
    local_tools=TOOLS,
    mcp_url=CONFIG.settings.MCP_URL,      # From config
    mcp_tools=CONFIG.settings.MCP_TOOLS,  # Tool filtering
    # ... other config
)
```

### 4. Factory Initialization (`runtime/factory.py`)

When `AgentFactory` is initialized:

1. **Checks for MCP URL**: If `mcp_url` is provided, creates transport factory
2. **Connects to MCP server**: Uses `MCPClient` to connect
3. **Fetches tools**: Calls `list_tools_sync()` to get all available tools
4. **Filters tools** (optional): If `mcp_tools` is specified, only includes those tools
5. **Caches tools**: Combines MCP tools with local tools and caches them
6. **Uses cached tools**: All agents created by this factory use the cached tools

## Tool Discovery Process

```python
# In runtime/factory.py _initialize_components()

if self.config.mcp_transport_factory:
    mcp_client = MCPClient(self.config.mcp_transport_factory)
    with mcp_client:
        all_mcp_tools = mcp_client.list_tools_sync()
        
        if self.config.allowed_mcp_tool_names:
            # Filter: only use specified tools
            mcp_tools = [tool for tool in all_mcp_tools 
                        if tool.tool_name in self.config.allowed_mcp_tool_names]
        else:
            # Use all tools
            mcp_tools = list(all_mcp_tools)

# Combine with local tools
self._cached_tools = mcp_tools + self.config.local_tools
```

## Usage Examples

### Example 1: Use All MCP Tools

```python
# agent/config.py
MCP_URL: Optional[str] = 'http://localhost:8000/mcp'
MCP_TOOLS: Optional[list[str]] = None  # All tools
```

### Example 2: Filter Specific Tools

```python
# agent/config.py
MCP_URL: Optional[str] = 'http://localhost:8000/mcp'
MCP_TOOLS: Optional[list[str]] = ['add']  # Only 'add' tool
```

### Example 3: Disable MCP Tools

```python
# agent/config.py
MCP_URL: Optional[str] = None  # No MCP server
MCP_TOOLS: Optional[list[str]] = None
```

## Running the System

### Step 1: Start MCP Server

```bash
python mcp_server.py
```

Server runs on `http://localhost:8000/mcp`

### Step 2: Start Agent Application

```bash
python main.py
```

The factory will automatically:
- Connect to the MCP server
- Discover available tools
- Cache them for agent use

## Adding New Tools

1. **Add tool to MCP server** (`mcp_app/app.py`):
   ```python
   @mcp.tool()
   def multiply(a: int, b: int) -> int:
       """Multiply two numbers."""
       return a * b
   ```

2. **Restart MCP server**

3. **Restart agent application** - Factory will discover the new tool automatically

4. **Optionally filter** - Add to `MCP_TOOLS` if you want to restrict it:
   ```python
   MCP_TOOLS: Optional[list[str]] = ['add', 'multiply']
   ```

## Troubleshooting

### Factory can't connect to MCP server

- Check MCP server is running: `python mcp_server.py`
- Verify URL in config: `MCP_URL = 'http://localhost:8000/mcp'`
- Check logs for connection errors

### Tools not appearing

- Check factory logs for MCP tool discovery
- Verify tool names match if using `MCP_TOOLS` filter
- Ensure MCP server has tools defined

### Session errors

- MCP server requires session initialization
- Factory handles this automatically via `MCPClient`
- If testing manually, follow session flow in `TESTING.md`

