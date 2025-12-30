"""Custom agent application library that encapsulates BedrockAgentCoreApp.

This module provides a reusable wrapper around BedrockAgentCoreApp with
custom functionality for agent projects.
"""

import ast
import json
from typing import Any, AsyncGenerator, Callable, Dict, Optional, Sequence
from bedrock_agentcore import BedrockAgentCoreApp
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from starlette.types import Lifespan


class StitchLabAgentCoreApp(BedrockAgentCoreApp):
    """Custom agent application that extends BedrockAgentCoreApp.
    
    This class encapsulates BedrockAgentCoreApp and adds custom functionality
    that can be reused across multiple agent projects. It handles:
    - CORS middleware setup
    - Metadata extraction from agent responses
    - Agent caching and optimization
    - Simplified entrypoint creation
    """
    
    def __init__(
        self,
        debug: bool = False,
        lifespan: Optional[Lifespan] = None,
        middleware: Sequence[Middleware] | None = None,
        enable_cors: bool = True,
        cors_origins: list[str] | str = "*",
        cors_credentials: bool = True,
        cors_methods: list[str] | str = "*",
        cors_headers: list[str] | str = "*",
        **kwargs
    ):
        """Initialize the custom agent application.
        
        Args:
            debug: Enable debug mode
            lifespan: Optional lifespan context manager
            middleware: Optional sequence of middleware
            enable_cors: Enable CORS middleware (default: True)
            cors_origins: CORS allowed origins (default: "*")
            cors_credentials: Allow credentials in CORS (default: True)
            cors_methods: CORS allowed methods (default: "*")
            cors_headers: CORS allowed headers (default: "*")
            **kwargs: Additional arguments passed to BedrockAgentCoreApp
        """
        super().__init__(debug=debug, lifespan=lifespan, middleware=middleware)
        self._custom_config: Dict[str, Any] = {}
        self._initialized = False
        self._create_agent_factory: Optional[Callable] = None
        
        # Setup CORS middleware if enabled
        if enable_cors:
            self.add_middleware(
                CORSMiddleware,
                allow_origins=cors_origins if isinstance(cors_origins, list) else cors_origins,
                allow_credentials=cors_credentials,
                allow_methods=cors_methods if isinstance(cors_methods, list) else cors_methods,
                allow_headers=cors_headers if isinstance(cors_headers, list) else cors_headers,
                expose_headers=["Content-Type"]
            )
        
    def configure(self, **config: Any) -> 'StitchLabAgentCoreApp':
        """Configure the app with custom settings.
        
        Args:
            **config: Configuration key-value pairs
            
        Returns:
            Self for method chaining
            
        Example:
            app.configure(api_key="xxx", timeout=30)
        """
        self._custom_config.update(config)
        return self
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self._custom_config.get(key, default)
    
    def initialize(self) -> 'StitchLabAgentCoreApp':
        """Initialize the app with custom setup logic.
        
        This method can be overridden in subclasses to add custom
        initialization logic that applies to all agent projects.
        
        Returns:
            Self for method chaining
        """
        if not self._initialized:
            # Add custom initialization logic here
            # This is where you'd add functionality common to all your agents
            self._initialized = True
            self.logger.info("StitchLabAgentCoreApp initialized")
        return self
    
    def extract_unique_metadata(self, data: Dict[str, Any]) -> list:
        """Extract unique metadata from agent response data.
        
        This method extracts unique commands/metadata from the agent's
        tool results, removing duplicates.
        
        Args:
            data: The event data from agent response
            
        Returns:
            List of unique metadata/commands
        """
        unique = []
        seen = set()

        try:
            # Step 1: Navigate to message.content (list)
            content_list = data.get("messages", [])
            
            if not isinstance(content_list, list):
                self.logger.debug(f"Expected messages to be a list, got {type(content_list)}")
                return unique

            for item in content_list:
                if not isinstance(item, dict):
                    self.logger.debug(f"Expected item to be a dict, got {type(item)}")
                    continue
                    
                item_contents = item.get('content', [])
                if not isinstance(item_contents, list):
                    self.logger.debug(f"Expected content to be a list, got {type(item_contents)}")
                    continue
                    
                for item_content in item_contents:
                    if not isinstance(item_content, dict):
                        self.logger.debug(f"Expected item_content to be a dict, got {type(item_content)}")
                        continue
                        
                    tool_result = item_content.get("toolResult")
                    if not tool_result or not isinstance(tool_result, dict):
                        continue

                    content_entries = tool_result.get("content", [])
                    if not isinstance(content_entries, list):
                        continue
                        
                    for content_entry in content_entries:
                        if not isinstance(content_entry, dict):
                            continue
                            
                        text_value = content_entry.get("text")
                        if not text_value:
                            continue

                        # Step 2: text_value is string containing Python dict -> convert using ast.literal_eval
                        try:
                            parsed = ast.literal_eval(text_value)
                        except Exception as e:
                            self.logger.debug(f"Failed to parse text_value: {e}")
                            continue

                        if not isinstance(parsed, dict):
                            continue

                        # Step 3: check if metadata exists
                        metadata = parsed.get("metadata")
                        if not metadata or not isinstance(metadata, dict):
                            continue

                        # Convert metadata list into each dict item
                        # metadata = {'commands': [...]}
                        commands = metadata.get("commands", [])
                        if not isinstance(commands, list):
                            continue

                        for cmd in commands:
                            # Make dict hashable for uniqueness
                            try:
                                key = json.dumps(cmd, sort_keys=True)
                                if key not in seen:
                                    seen.add(key)
                                    unique.append(cmd)
                            except Exception as e:
                                self.logger.debug(f"Failed to serialize command: {e}")
                                continue

        except Exception as e:
            self.logger.error(f"Error extracting metadata: {str(e)}", exc_info=True)
            
        return unique
    
    def agent_entrypoint(self, create_agent_func: Callable) -> Callable:
        """Decorator to create an agent entrypoint with automatic session handling.
        
        This decorator handles:
        - Extracting actor_id and session_id from payload
        - Creating/getting agent instance
        - Streaming agent responses
        - Extracting metadata from final results
        - Error handling
        
        Args:
            create_agent_func: Async function that takes (actor_id, session_id) and returns an Agent
            
        Returns:
            Decorated entrypoint function
            
        Example:
            @app.agent_entrypoint(create_agent)
            async def my_handler(payload):
                # This will be automatically called with the agent and message
                # You can override this if you need custom logic
                pass
        """
        async def entrypoint_wrapper(payload: Dict[str, Any]) -> AsyncGenerator[Any, None]:
            """Wrapper that handles agent invocation with session management."""
            self.logger.info(f"PAYLOAD : {payload}")
            input_data = payload.get("input", {})
            actor_id = input_data.get('actor_id', '')
            session_id = input_data.get('session_id', '')
            message = input_data.get('message', '')
            
            try:
                # Get or create agent for this session
                agent = await create_agent_func(actor_id=actor_id, session_id=session_id)
                
                if agent is None:
                    error_response = {"error": "Failed to create agent", "type": "agent_creation_error"}
                    self.logger.error(f"Agent creation failed: {error_response}")
                    yield error_response
                    return

                prev_event = None
                async for event in agent.stream_async(message):
                    if "data" in event:
                        yield event["data"]
                        prev_event = event
                    
                    # Check for end of turn to extract metadata
                    if "AgentResult(stop_reason='end_turn'" in str(event):
                        self.logger.info(f"FINAL RESULT : {event}")
                        if prev_event is not None:
                            metadata = self.extract_unique_metadata(prev_event)
                            if metadata:
                                yield metadata
                            
            except Exception as e:
                # Handle errors gracefully in streaming context
                error_response = {"error": str(e), "type": "stream_error"}
                self.logger.error(f"Agent invocation error: {error_response}")
                yield error_response
        
        # Register as entrypoint
        return self.entrypoint(entrypoint_wrapper)
    
    def tool(self, func: Callable) -> Callable:
        """Decorator to register a function as a tool.
        
        This is a convenience method that can be extended with custom
        tool registration logic.
        
        Args:
            func: The function to register as a tool
            
        Returns:
            The decorated function
        """
        # Add custom tool registration logic here if needed
        # For now, this is a placeholder for future functionality
        return func
    
    def health_check(self, func: Optional[Callable] = None) -> Callable:
        """Decorator to register a custom health check handler.
        
        This wraps the ping decorator with additional custom logic.
        
        Args:
            func: Optional function to register
            
        Returns:
            The decorated function or decorator
        """
        if func is None:
            # Used as @app.health_check()
            def decorator(f: Callable) -> Callable:
                return self.ping(f)
            return decorator
        else:
            # Used as @app.health_check
            return self.ping(func)
    
    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Add cleanup logic here if needed
        pass

