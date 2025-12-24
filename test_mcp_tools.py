import requests
import json

def get_session_id():
    """Initialize session and return session ID."""
    init_response = requests.post(
        'http://localhost:8000/mcp',
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        },
        json={
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            },
            "id": 1
        }
    )
    
    session_id = init_response.headers.get('Mcp-Session-Id')
    if not session_id:
        raise Exception(f"No session ID received. Response: {init_response.text}")
    
    print(f"✓ Session initialized. Session ID: {session_id}\n")
    return session_id


def parse_sse_response(text):
    """Parse Server-Sent Events format to extract JSON."""
    lines = text.strip().split('\n')
    json_data = None
    
    for line in lines:
        if line.startswith('data: '):
            json_str = line[6:]  # Remove 'data: ' prefix
            try:
                json_data = json.loads(json_str)
                break
            except json.JSONDecodeError:
                continue
    
    return json_data

def list_tools(session_id):
    """List all available tools from the MCP server."""
    print("=" * 60)
    print("TEST 1: Listing All Tools")
    print("=" * 60)
    
    response = requests.post(
        'http://localhost:8000/mcp',
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
            'Mcp-Session-Id': session_id
        },
        json={
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
    )
    
    print(f"Status Code: {response.status_code}")
    
    # Parse and display tools nicely
    try:
        if not response.text.strip():
            print("⚠️  Warning: Empty response received")
            return None
        
        # Check if it's SSE format
        content_type = response.headers.get('Content-Type', '')
        if 'text/event-stream' in content_type:
            result = parse_sse_response(response.text)
            if not result:
                print("❌ Could not extract JSON from SSE format")
                return None
        else:
            result = response.json()
        
        print(f"Response:\n{json.dumps(result, indent=2)}\n")
        
        if 'result' in result and 'tools' in result['result']:
            tools = result['result']['tools']
            print(f"Found {len(tools)} tool(s):")
            for i, tool in enumerate(tools, 1):
                print(f"\n  {i}. {tool.get('name', 'Unknown')}")
                print(f"     Description: {tool.get('description', 'No description')}")
                if 'inputSchema' in tool:
                    schema = tool['inputSchema']
                    if 'properties' in schema:
                        print(f"     Parameters: {', '.join(schema['properties'].keys())}")
        elif 'error' in result:
            print(f"❌ Error from server: {result['error']}")
        else:
            print(f"⚠️  Unexpected response format")
        
        return result
    except json.JSONDecodeError as e:
        print(f"❌ Error: Response is not valid JSON")
        print(f"Raw response: {response.text}")
        print(f"JSON Error: {e}")
        return None
    except Exception as e:
        print(f"Error parsing tools: {e}")
        import traceback
        traceback.print_exc()
        return None


def call_tool(session_id, tool_name, arguments):
    """Call a specific tool with given arguments."""
    print("=" * 60)
    print(f"TEST 2: Calling Tool '{tool_name}'")
    print("=" * 60)
    print(f"Arguments: {arguments}\n")
    
    response = requests.post(
        'http://localhost:8000/mcp',
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
            'Mcp-Session-Id': session_id
        },
        json={
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": 3
        },
        stream=True  # Enable streaming for streaming tools
    )
    
    print(f"Status Code: {response.status_code}")
    
    # Check if it's a streaming response
    content_type = response.headers.get('Content-Type', '')
    is_sse = 'text/event-stream' in content_type
    is_chunked = 'chunked' in response.headers.get('Transfer-Encoding', '')
    
    if is_sse and is_chunked:
        # SSE streaming response
        print("Streaming SSE response:")
        print("-" * 60)
        full_text = ""
        for chunk in response.iter_content(chunk_size=None):
            if chunk:
                chunk_text = chunk.decode('utf-8')
                print(chunk_text, end='', flush=True)
                full_text += chunk_text
        
        # Try to parse JSON from SSE
        result = parse_sse_response(full_text)
        if result:
            print("\n\nParsed JSON:")
            print(json.dumps(result, indent=2))
        print("\n" + "-" * 60)
        return result
    elif is_sse:
        # SSE but complete response
        result = parse_sse_response(response.text)
        if result:
            print(f"Response:\n{json.dumps(result, indent=2)}\n")
            return result
        else:
            print("⚠️  Could not parse SSE response")
            print(f"Raw: {response.text}")
            return None
    else:
        # Regular JSON response
        try:
            if response.text.strip():
                result = response.json()
                print(f"Response:\n{json.dumps(result, indent=2)}\n")
                return result
            else:
                print("⚠️  Empty response received")
                return None
        except json.JSONDecodeError as e:
            print(f"❌ Error: Response is not valid JSON")
            print(f"Raw response: {response.text}")
            print(f"JSON Error: {e}")
            return None


if __name__ == "__main__":
    try:
        # Step 1: Initialize session
        session_id = get_session_id()
        
        # Step 2: List all tools
        tools_result = list_tools(session_id)
        
        # Step 3: Call a tool (example: add tool)
        print("\n")
        call_tool(session_id, "add", {"a": 5, "b": 3})
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

