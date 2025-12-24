import requests
import json

# Step 1: Initialize the session
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

# Extract session ID from response headers
session_id = init_response.headers.get('Mcp-Session-Id')
if not session_id:
    print("Error: No session ID received from server")
    print("Response:", init_response.text)
    exit(1)

print(f"Session ID: {session_id}")
print(f"Initialize response: {init_response.text}\n")

# Step 2: Call the tool with session ID
response = requests.post(
    'http://localhost:8000/mcp',
    headers={
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'Mcp-Session-Id': session_id  # Include session ID
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

print("Streaming response:")
for chunk in response.iter_content(chunk_size=None):
    if chunk:
        print(chunk.decode('utf-8'), end='', flush=True)