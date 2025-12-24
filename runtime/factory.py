"""Reusable AgentFactory for creating agents with optimized caching.

This module provides a configurable factory that caches expensive agent
components (model, tools, system prompt) and only creates session-specific
parts per invocation.
"""

import logging
from typing import List, Optional, Any, Literal
from strands import Agent
from strands.tools.mcp import MCPClient
from strands.models import BedrockModel
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from mcp.client.streamable_http import streamable_http_client


logger = logging.getLogger(__name__)


class AgentFactoryConfig:
    """Configuration for AgentFactory.
    
    This class holds all configuration needed to create agents.
    Developers should create an instance of this with their project-specific settings.
    """
    
    def __init__(
        self,
        system_prompt: str,
        model_id: str,
        memory_id: str,
        region_name: str,
        guardrail_id: Optional[str] = None,
        guardrail_version: Optional[str] = None,
        guardrail_trace: Literal["enabled", "disabled"] = "disabled",
        mcp_url: Optional[str] = None,
        mcp_tools: Optional[List[str]] = None,
        local_tools: Optional[List[Any]] = None
    ):
        """Initialize factory configuration.
        
        Args:
            model_id: Bedrock model ID to use (required)
            memory_id: Memory ID for session management (required)
            region_name: AWS region name (required)
            guardrail_id: Optional guardrail ID
            guardrail_version: Optional guardrail version
            guardrail_trace: Guardrail trace setting (default: "disabled")
            mcp_url: Optional MCP server URL (e.g., "http://localhost:8000/mcp")
            mcp_tools: Optional list of MCP tool names to filter/allow (if None, all tools are used)
            local_tools: Optional list of local tools to include
            system_prompt: System prompt for the agent
        """
        
        self.model_id = model_id
        self.guardrail_id = guardrail_id
        self.guardrail_version = guardrail_version
        self.guardrail_trace = guardrail_trace
        self.memory_id = memory_id
        self.region_name = region_name

        # Set up MCP transport factory if URL is provided
        self.mcp_transport_factory = streamable_http_client(mcp_url) if mcp_url else None
        # mcp_tools is a list of tool names to filter/allow
        self.allowed_mcp_tool_names = set(mcp_tools) if mcp_tools else None

        self.local_tools = local_tools or []
        self.system_prompt = system_prompt


class AgentFactory:
    """Factory class that caches expensive agent components and only creates session-specific parts.
    
    This factory is reusable across different agent projects. Each project
    should create an instance with their specific AgentFactoryConfig.
    """
    
    def __init__(self, config: AgentFactoryConfig):
        """Initialize the factory with configuration.
        
        Args:
            config: AgentFactoryConfig instance with project-specific settings
        """
        self.config = config
        self._bedrock_model: Optional[BedrockModel] = None
        self._cached_tools: Optional[List[Any]] = None
        self._initialized = False
    
    def _initialize_components(self):
        """Initialize and cache expensive components (model, tools, system_prompt)."""
        if self._initialized:
            return
        
        logger.info("Initializing agent factory components (this happens once)...")
        
        # Create bedrock model with guardrail (cached)
        model_kwargs = {
            "model_id": self.config.model_id,
            "guardrail_trace": self.config.guardrail_trace,
        }

        if self.config.guardrail_id:
            model_kwargs["guardrail_id"] = self.config.guardrail_id

        if self.config.guardrail_version:
            model_kwargs["guardrail_version"] = self.config.guardrail_version
        
        self._bedrock_model = BedrockModel(**model_kwargs)
        
        # Fetch and cache MCP tools if configured (expensive operation)
        mcp_tools = []
        if self.config.mcp_transport_factory:
            try:
                mcp_client = MCPClient(self.config.mcp_transport_factory)
                with mcp_client:
                    all_mcp_tools = mcp_client.list_tools_sync()
                    logger.info(f"MCP TOOLS: {all_mcp_tools}")
                    
                    if self.config.allowed_mcp_tool_names:
                        # Filter tools by allowed names
                        mcp_tools = [
                            tool for tool in all_mcp_tools
                            if tool.tool_name in self.config.allowed_mcp_tool_names
                        ]
                        logger.info(f"FILTERED MCP TOOLS: {mcp_tools}")

                    else:
                        # Use all MCP tools if no filter specified
                        mcp_tools = list(all_mcp_tools)

            except Exception as e:
                logger.error(f"Error initializing MCP tools: {str(e)}")
                mcp_tools = []
        
        # Combine MCP tools with local tools
        self._cached_tools = mcp_tools + self.config.local_tools
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
            memory_id=self.config.memory_id,
            session_id=session_id,
            actor_id=actor_id
        )
        
        session_manager = AgentCoreMemorySessionManager(
            agentcore_memory_config=agentcore_memory_config,
            region_name=self.config.region_name
        )
        
        # Create agent using cached components
        try:
            agent = Agent(
                model=self._bedrock_model,
                tools=self._cached_tools,
                system_prompt=self.config.system_prompt,
                session_manager=session_manager
            )
            return agent

        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}")
            return None
