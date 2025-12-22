"""Agent builder with optimized caching for reusable components.

This module configures the reusable AgentFactory with project-specific settings.
Developers only need to modify this file to customize their agent configuration.
"""

from typing import Optional
from strands import Agent
from mcp.client.streamable_http import streamablehttp_client
from agent.tools.codegen import generate_abap_code
from config.settings import settings
from runtime.factory import AgentFactory, AgentFactoryConfig
from utils.app_logger import logger


def create_streamable_http_transport():
    """Create streamable HTTP transport for MCP.
    
    This is project-specific - modify as needed for your MCP setup.
    """
    return streamablehttp_client(settings.MCP_URL)


# Configure the factory with project-specific settings
_factory_config = AgentFactoryConfig(
    # Required configuration
    model_id=settings.MODEL_ID,
    memory_id=settings.MEMORY_ID,
    region_name=settings.REGION_BEDROCK,
    # Model configuration (optional)
    guardrail_id=settings.BEDROCK_GUARDRAIL_ID,
    guardrail_version=settings.BEDROCK_GUARDRAIL_VER,
    guardrail_trace="enabled",
    # MCP configuration (optional)
    mcp_transport_factory=create_streamable_http_transport,
    allowed_mcp_tool_names={"read_sap_tables"},  # Filter MCP tools by name
    # Local tools (project-specific)
    local_tools=[generate_abap_code],
    # System prompt (project-specific)
    system_prompt="""
        You are a technical engineer expert SAP Consultant specializing in SAP ECC and SAP S/4HANA with expertise in ABAP code generation.
        ABAP, which stands for Advanced Business Application Programming, is SAP's proprietary high-level programming language used to develop and customize applications within the SAP ecosystem, including ERP systems like S/4HANA.
        
        You are very PROFESSIONAL, CONVERSATIONAL, HELPFUL and FOCUS on your role for assisting the user on generating ABAP code based on their provided requirement.
        
        TIPS : If the user provide you specific knowledge about the code requirement, you should use the tool `generate_abap_code` to generate the ABAP code. Therefore you dont have to always call the tool for general knowledge or discussion about the code.
    """,
)

# Create singleton factory instance with project configuration
_agent_factory = AgentFactory(_factory_config)


async def create_agent(actor_id: str, session_id: str) -> Optional[Agent]:
    """Create an agent instance (optimized with caching).
    
    This function uses a cached factory to avoid rebuilding
    expensive components on every invocation.
    
    Args:
        actor_id: The actor ID for the session
        session_id: The session ID
        
    Returns:
        Agent instance or None if creation fails
    """
    return await _agent_factory.create_agent(actor_id=actor_id, session_id=session_id)