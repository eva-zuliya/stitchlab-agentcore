"""Main application entry point using StitchLabAgentApp.

This demonstrates the simplified usage where all boilerplate
(middleware, metadata extraction, session handling) is handled
by the StitchLabAgentApp library.
"""

from config.settings import settings
from agent import StitchLabAgentApp
from agent.builder import create_agent
from utils.app_logger import logger

# Create app with CORS enabled (handled automatically by StitchLabAgentApp)
app = StitchLabAgentApp(debug=True).initialize()

# Register agent entrypoint - just provide the create_agent function
# All the streaming, metadata extraction, and error handling is automatic
@app.agent_entrypoint(create_agent)
async def agent_invocation(payload):
    """Agent invocation handler.
    
    This function signature is required but the actual implementation
    is handled by StitchLabAgentApp.agent_entrypoint decorator.
    The decorator automatically:
    - Extracts actor_id, session_id, and message from payload
    - Creates agent with session management
    - Streams responses
    - Extracts metadata from final results
    - Handles errors
    """
    pass  # Implementation handled by decorator


if __name__ == "__main__":
    logger.info(f"Starting {settings.APP_NAME} on FastAPI server...")
    app.run()