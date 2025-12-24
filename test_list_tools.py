"""
Test script to list all available tools from MCP server.
"""
import requests
import json

# Step 1: Initialize session
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

# Extract session ID
session_id = init_response.headers.get('Mcp-Session-Id')
if not session_id:
    print("Error: No session ID received")
    print("Response:", init_response.text)
    exit(1)

print(f"✓ Session ID: {session_id}\n")

# Step 2: List all tools
print("=" * 60)
print("Listing All Available Tools")
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

print(f"\nStatus Code: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")
print(f"\nRaw Response Text:")
print(response.text)
print(f"\nResponse Length: {len(response.text)} bytes")

# Parse SSE format or regular JSON
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

# Try to parse response
try:
    if not response.text.strip():
        print("\n⚠️  Warning: Empty response received")
        exit(1)
    
    # Check if it's SSE format
    content_type = response.headers.get('Content-Type', '')
    if 'text/event-stream' in content_type:
        print("\n📡 Detected SSE (Server-Sent Events) format")
        result = parse_sse_response(response.text)
        if not result:
            print("❌ Could not extract JSON from SSE format")
            exit(1)
    else:
        # Regular JSON
        result = response.json()
    
    print(f"\n{'=' * 60}")
    print("Parsed JSON Response:")
    print('=' * 60)
    print(json.dumps(result, indent=2))
    
    # Pretty print tools
    if 'result' in result and 'tools' in result['result']:
        tools = result['result']['tools']
        print(f"\n{'=' * 60}")
        print(f"Found {len(tools)} tool(s):")
        print('=' * 60)
        
        for i, tool in enumerate(tools, 1):
            print(f"\n{i}. Tool Name: {tool.get('name', 'Unknown')}")
            print(f"   Description: {tool.get('description', 'No description')}")
            
            if 'inputSchema' in tool:
                schema = tool['inputSchema']
                if 'properties' in schema:
                    print(f"   Parameters:")
                    for param_name, param_info in schema['properties'].items():
                        param_type = param_info.get('type', 'unknown')
                        param_desc = param_info.get('description', '')
                        required = ' (required)' if param_name in schema.get('required', []) else ''
                        print(f"     - {param_name}: {param_type}{required}")
                        if param_desc:
                            print(f"       {param_desc}")
    elif 'error' in result:
        print(f"\n❌ Error from server: {result['error']}")
    else:
        print(f"\n⚠️  Unexpected response format. Keys: {result.keys()}")
        
except json.JSONDecodeError as e:
    print(f"\n❌ Error: Response is not valid JSON")
    print(f"JSON Error: {e}")
    print(f"\nRaw response (first 500 chars):")
    print(response.text[:500])
except Exception as e:
    print(f"\n❌ Error parsing response: {e}")
    import traceback
    traceback.print_exc()

