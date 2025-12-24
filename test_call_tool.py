"""
Test script to call a specific tool from MCP server.
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

# Step 2: Call a tool
# ============================================
# CONFIGURE THIS SECTION FOR YOUR TOOL
# ============================================
TOOL_NAME = "add"  # Change this to the tool name you want to call
TOOL_ARGUMENTS = {"a": 5, "b": 3}  # Change these to match your tool's parameters

# Examples:
# For 'add' tool: TOOL_NAME = "add", TOOL_ARGUMENTS = {"a": 5, "b": 3}
# For 'count_stream' tool: TOOL_NAME = "count_stream", TOOL_ARGUMENTS = {"start": 1, "end": 5}
# ============================================

print("=" * 60)
print(f"Calling Tool: {TOOL_NAME}")
print("=" * 60)
print(f"Arguments: {TOOL_ARGUMENTS}\n")

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
            "name": TOOL_NAME,
            "arguments": TOOL_ARGUMENTS
        },
        "id": 3
    },
    stream=True  # Enable streaming for streaming tools
)

print(f"Status Code: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")

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

# Handle streaming vs non-streaming responses
content_type = response.headers.get('Content-Type', '')
is_sse = 'text/event-stream' in content_type
is_chunked = 'chunked' in response.headers.get('Transfer-Encoding', '')

if is_sse and is_chunked:
    # SSE streaming response
    print("\n" + "=" * 60)
    print("SSE Streaming Response:")
    print("=" * 60)
    for chunk in response.iter_content(chunk_size=None):
        if chunk:
            chunk_text = chunk.decode('utf-8')
            print(chunk_text, end='', flush=True)
            
            # Try to parse JSON from SSE data lines
            if 'data: ' in chunk_text:
                result = parse_sse_response(chunk_text)
                if result:
                    print("\n\n" + "=" * 60)
                    print("Parsed JSON:")
                    print("=" * 60)
                    print(json.dumps(result, indent=2))
    print("\n" + "=" * 60)
elif is_sse:
    # SSE but not streaming (complete response)
    print("\n" + "=" * 60)
    print("SSE Response (parsed):")
    print("=" * 60)
    result = parse_sse_response(response.text)
    if result:
        print(json.dumps(result, indent=2))
    else:
        print("Raw SSE response:")
        print(response.text)
    print("=" * 60)
else:
    # Regular JSON response
    print("\n" + "=" * 60)
    print("Response:")
    print("=" * 60)
    try:
        if response.text.strip():
            print(json.dumps(response.json(), indent=2))
        else:
            print("⚠️  Empty response received")
    except json.JSONDecodeError as e:
        print(f"❌ Error: Response is not valid JSON")
        print(f"Raw response: {response.text}")
        print(f"JSON Error: {e}")
    print("=" * 60)

