from runtime.factory import AgentFactory
from runtime.app import StitchLabAgentApp
from typing import Optional
from strands import Agent
import logging

logger = logging.getLogger(__name__)

from test import CONFIG, SYSTEM_PROMPT, TOOLS
AGENT_FACTORY = AgentFactory(
    system_prompt=SYSTEM_PROMPT,
    local_tools=TOOLS,
    config=CONFIG
)

async def create_agent(actor_id: str, session_id: str) -> Optional[Agent]:
    return await AGENT_FACTORY.create_agent(actor_id=actor_id, session_id=session_id)


app = StitchLabAgentApp(debug=True).initialize()

@app.agent_entrypoint(create_agent)
async def agent_invocation(payload):
    pass


if __name__ == "__main__":
    CONFIG.logger.info(f"Starting {CONFIG.settings.APP_NAME} on FastAPI server...")
    app.run()