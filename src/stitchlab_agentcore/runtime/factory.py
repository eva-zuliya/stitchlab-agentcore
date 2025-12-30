"""Reusable AgentFactory for creating agents with optimized caching.

This module provides a configurable factory that caches expensive agent
components (model, tools, system prompt) and only creates session-specific
parts per invocation.
"""

import logging
from typing import List, Optional, Any, Literal
from strands import Agent
from strands.tools.mcp import MCPClient
from strands.models.litellm import LiteLLMModel
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from mcp.client.streamable_http import streamable_http_client
from config import GlobalConfig, BaseSettings


logger = logging.getLogger(__name__)

class AgentFactory:
    """Factory class that caches expensive agent components and only creates session-specific parts.
    
    This factory is reusable across different agent projects. Each project
    should create an instance with their specific AgentFactoryConfig.
    """
    
    def __init__(self, 
        config: GlobalConfig[BaseSettings],
        system_prompt: str,
        local_tools: Optional[List[Any]] = None,
    ):
        """Initialize the factory with configuration.
        
        Args:
            config: AgentFactoryConfig instance with project-specific settings
        """
        self.config = config
        self.local_tools = local_tools or []
        self.system_prompt = system_prompt

        self.model: Optional[LiteLLMModel] = None
        self._cached_tools: Optional[List[Any]] = None
        self._mcp_client: Optional[MCPClient] = None
        self._initialized = False
    
    def _initialize_components(self):
        """Initialize and cache expensive components (model, tools, system_prompt)."""
        if self._initialized:
            return
        
        logger.info("Initializing agent factory components (this happens once)...")
        
        # Use the litellm model with the configured model_id
        self.model = LiteLLMModel(
            model_id=self.config.settings.MODEL_ID
        )
        logger.info(f"Using LiteLLM model with model_id: {self.config.settings.MODEL_ID}")
        
        # Fetch and cache MCP tools if configured (expensive operation)
        mcp_tools = []
        if self.config.settings.MCP_URL:
            try:
                logger.info("Initializing MCP client...")
                # Create MCPClient and keep it open for the lifetime of the factory
                self._mcp_client = MCPClient(
                    lambda: streamable_http_client(self.config.settings.MCP_URL)
                )
                # Enter the context manager to activate the client session
                self._mcp_client.__enter__()
                
                # List all available tools from the MCP server
                all_mcp_tools = self._mcp_client.list_tools_sync()
                logger.info(f"MCP TOOLS discovered: {[tool.tool_name for tool in all_mcp_tools]}")
                    
                if self.config.settings.MCP_TOOLS:
                    # Filter tools by allowed names
                    mcp_tools = [
                        tool for tool in all_mcp_tools
                        if tool.tool_name in self.config.settings.MCP_TOOLS
                    ]
                    logger.info(f"FILTERED MCP TOOLS: {[tool.tool_name for tool in mcp_tools]}")
                else:
                    # Use all MCP tools if no filter specified
                    mcp_tools = list(all_mcp_tools)

            except Exception as e:
                logger.error(f"Error initializing MCP tools: {str(e)}", exc_info=True)
                mcp_tools = []
        
        # Combine MCP tools with local tools
        self._cached_tools = mcp_tools + (self.local_tools or [])
        logger.info(f"TOTAL TOOLS: {len(self._cached_tools)}")
        
        self._initialized = True
        logger.info("Agent factory components initialized and cached")
    
    async def create_agent(self, actor_id: str, session_id: str) -> Optional[Agent]:
        """Create an agent instance with session-specific configuration.
        
        This method only creates a new session_manager per invocation,
        reusing all other expensive components (model, tools, system_prompt).
        
        Args:
            actor_id: The actor ID for the session
            session_id: The session ID
            
        Returns:
            Agent instance or None if creation fails
        """
        # Initialize components on first call (lazy initialization)
        self._initialize_components()
        
        # Only create session-specific parts (cheap operation)
        agentcore_memory_config = AgentCoreMemoryConfig(
            memory_id=self.config.settings.MEMORY_ID,
            session_id=session_id,
            actor_id=actor_id
        )
        
        session_manager = AgentCoreMemorySessionManager(
            agentcore_memory_config=agentcore_memory_config,
            region_name=self.config.settings.BEDROCK_REGION
        )
        
        # Create agent using cached components
        try:
            agent = Agent(
                model=self.model,
                tools=self._cached_tools,
                system_prompt=self.system_prompt,
                session_manager=session_manager
            )
            return agent

        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}")
            return None
    
    def cleanup(self):
        """Clean up MCP client resources."""
        if self._mcp_client:
            try:
                self._mcp_client.__exit__(None, None, None)
                logger.info("MCP client closed")
            except Exception as e:
                logger.error(f"Error closing MCP client: {str(e)}")
