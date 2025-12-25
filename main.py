from runtime.factory import AgentFactory, AgentFactoryConfig
from runtime.app import StitchLabAgentApp
from typing import Optional
from strands import Agent

from agent.config import GlobalSettings, GlobalModelRegistry, AppConfig
from agent.builder import SYSTEM_PROMPT, TOOLS

import litellm
litellm.success_callback = ["langfuse"]

CONFIG = AppConfig(GlobalSettings(), GlobalModelRegistry())

FACTORY_CONFIG = AgentFactoryConfig(
    system_prompt=SYSTEM_PROMPT,
    local_tools=TOOLS,
    memory_id=CONFIG.settings.MEMORY_ID,
    region_name=CONFIG.settings.BEDROCK_REGION,
    model_id=getattr(CONFIG.model_registry, CONFIG.settings.MODEL_ID),
    guardrail_id=CONFIG.settings.BEDROCK_GUARDRAIL_ID,
    guardrail_version=CONFIG.settings.BEDROCK_GUARDRAIL_VER,
    guardrail_trace=CONFIG.settings.BEDROCK_GUARDRAIL_TRACE,
    mcp_url=CONFIG.settings.MCP_URL,
    mcp_tools=CONFIG.settings.MCP_TOOLS
)

AGENT_FACTORY = AgentFactory(FACTORY_CONFIG)

async def create_agent(actor_id: str, session_id: str) -> Optional[Agent]:
    return await AGENT_FACTORY.create_agent(actor_id=actor_id, session_id=session_id)


app = StitchLabAgentApp(debug=True).initialize()

@app.agent_entrypoint(create_agent)
async def agent_invocation(payload):
    pass


if __name__ == "__main__":
    CONFIG.logger.info(f"Starting {CONFIG.settings.APP_NAME} on FastAPI server...")
    app.run()