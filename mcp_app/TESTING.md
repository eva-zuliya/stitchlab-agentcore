# Testing MCP Server with Insomnia

## Important: Use HTTP POST Requests (Not SSE)

Since the server uses `streamable-http` transport, you should use **regular HTTP POST requests** in Insomnia, not SSE (Server-Sent Events).

## Method 1: Using Insomnia's Built-in MCP Client (Recommended)

If Insomnia has built-in MCP client support:

1. **Start your MCP server**:
   ```bash
   python mcp_server.py
   ```
   The server will be available at `http://localhost:8000/mcp`

2. **In Insomnia**:
   - Open Insomnia
   - In the sidebar, click on **MCP Clients** (or look for MCP section)
   - Click **New MCP Client**
   - Enter a name (e.g., "Simple MCP Server")
   - In **MCP Server URL**, enter: `http://localhost:8000/mcp`
   - Click **Connect**

3. **Test the `add` tool**:
   - In the sidebar under **Tools**, select the `add` tool
   - In the request pane, click the **Params** tab
   - Enter parameters:
     - `a`: `5`
     - `b`: `3`
   - Click **Call Tool**
   - You should see the result: `8`

## Method 2: Manual HTTP POST Requests (JSON-RPC)

**Use HTTP POST requests** - this is the correct method for `streamable-http` transport.

**Important**: MCP requires session initialization. You must:
1. First send an `initialize` request
2. Extract the `Mcp-Session-Id` header from the response
3. Include this session ID in all subsequent requests

MCP uses JSON-RPC 2.0 protocol. You can test it with regular HTTP requests:

### 1. Initialize Session (REQUIRED FIRST STEP)

**In Insomnia:**
- Create a **new HTTP request** (not SSE)
- **Method**: `POST`
- **URL**: `http://localhost:8000/mcp`
- **Headers**:
  ```
  Content-Type: application/json
  Accept: application/json, text/event-stream
  ```
- **Body** (select JSON):
  ```json
  {
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "insomnia",
        "version": "1.0.0"
      }
    },
    "id": 0
  }
  ```

**Response**: Check the response headers for `Mcp-Session-Id`. Copy this value for use in subsequent requests.

### 2. List Available Tools

**In Insomnia:**
- Create a **new HTTP request** (not SSE)
- **Method**: `POST`
- **URL**: `http://localhost:8000/mcp`
- **Headers**:
  ```
  Content-Type: application/json
  Accept: application/json, text/event-stream
  ```
- **Body** (select JSON):
  ```json
  {
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 1
  }
  ```

### 3. Call the `add` Tool

**In Insomnia:**
- Create a **new HTTP request** (not SSE)
- **Method**: `POST`
- **URL**: `http://localhost:8000/mcp`
- **Headers**:
  ```
  Content-Type: application/json
  Accept: application/json, text/event-stream
  Mcp-Session-Id: YOUR_SESSION_ID_HERE
  ```
  (Replace `YOUR_SESSION_ID_HERE` with the session ID from step 1)
- **Body** (select JSON):
  ```json
  {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "add",
      "arguments": {
        "a": 5,
        "b": 3
      }
    },
    "id": 2
  }
  ```

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "8"
      }
    ]
  },
  "id": 2
}
```


## Streaming Responses

MCP **does support streaming** through the `streamable-http` transport using HTTP chunked transfer encoding. However, **Insomnia has limitations** when displaying streaming responses:

- ✅ **Streaming works at the protocol level** - the server will stream data
- ⚠️ **Insomnia may not display streaming responses in real-time** - it may wait for the full response
- ✅ **The streaming functionality is available** - tools that return async generators will stream

### Testing Streaming Tools

The server includes a `count_stream` tool that demonstrates streaming. To test it:

**In Insomnia:**
- **Method**: `POST`
- **URL**: `http://localhost:8000/mcp`
- **Headers**:
  ```
  Content-Type: application/json
  Accept: application/json, text/event-stream
  Mcp-Session-Id: YOUR_SESSION_ID_HERE
  ```
  (Replace `YOUR_SESSION_ID_HERE` with the session ID from initialization)
- **Body**:
  ```json
  {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "count_stream",
      "arguments": {
        "start": 1,
        "end": 5
      }
    },
    "id": 3
  }
  ```

**Note**: Insomnia may buffer the response and show it all at once, but the server is streaming it chunk by chunk.

### Better Tools for Testing Streaming

For better visualization of streaming responses, consider:

1. **cURL** (command line):
   ```bash
   # Step 1: Initialize and get session ID
   INIT_RESPONSE=$(curl -X POST http://localhost:8000/mcp \
     -H "Content-Type: application/json" \
     -H "Accept: application/json, text/event-stream" \
     -d '{
       "jsonrpc": "2.0",
       "method": "initialize",
       "params": {
         "protocolVersion": "2024-11-05",
         "capabilities": {},
         "clientInfo": {"name": "curl", "version": "1.0"}
       },
       "id": 1
     }' \
     -i)
   
   # Extract session ID (you'll need to manually copy from response headers)
   # Then use it in step 2:
   
   # Step 2: Call tool with session ID
   curl -X POST http://localhost:8000/mcp \
     -H "Content-Type: application/json" \
     -H "Accept: application/json, text/event-stream" \
     -H "Mcp-Session-Id: YOUR_SESSION_ID_HERE" \
     -d '{
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
         "name": "count_stream",
         "arguments": {"start": 1, "end": 5}
       },
       "id": 3
     }' \
     --no-buffer
   ```

2. **Python script**:
   ```python
   import requests
   import json
   
   response = requests.post(
       'http://localhost:8000/mcp',
       headers={
           'Content-Type': 'application/json',
           'Accept': 'application/json, text/event-stream'  # Required by MCP
       },
       json={
           "jsonrpc": "2.0",
           "method": "tools/call",
           "params": {
               "name": "count_stream",
               "arguments": {"start": 1, "end": 5}
           },
           "id": 3
       },
       stream=True
   )
   
   for chunk in response.iter_content(chunk_size=None):
       if chunk:
           print(chunk.decode('utf-8'), end='', flush=True)
   ```

## Summary

- ✅ **Use HTTP POST requests** (regular HTTP, not SSE)
- ✅ **URL**: `http://localhost:8000/mcp`
- ✅ **Content-Type**: `application/json`
- ✅ **Accept**: `application/json, text/event-stream` (REQUIRED - MCP specification)
- ✅ **Mcp-Session-Id**: Required header for all requests after initialization
- ✅ **Body**: JSON-RPC 2.0 format
- ✅ **Session initialization required** - Must call `initialize` first, then use session ID in subsequent requests
- ✅ **Streaming is supported** - tools can return async generators
- ⚠️ **Insomnia limitations** - may not show streaming in real-time, but streaming works at protocol level
- ❌ **Do NOT use SSE/Event Stream** - that's for a different transport type

## Quick Test Collection for Insomnia

You can create these requests in Insomnia (in order):

1. **Initialize** → `initialize` method (get session ID from response headers)
2. **List Tools** → `tools/list` method (include session ID header)
3. **Call Add Tool** (non-streaming) → `tools/call` method with `add` tool (include session ID header)
4. **Call Count Stream Tool** (streaming) → `tools/call` method with `count_stream` tool (include session ID header)

**Remember**: After step 1, copy the `Mcp-Session-Id` from the response headers and include it in all subsequent requests!

