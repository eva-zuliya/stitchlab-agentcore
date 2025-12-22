"""StitchLab Agent Core Runtime Library.

This package provides reusable components for building agents:
- AgentFactory: Optimized agent creation with caching
- AgentFactoryConfig: Configuration for agent factories
- StitchLabAgentApp: Custom application wrapper
"""

from .factory import AgentFactory, AgentFactoryConfig
from .app import StitchLabAgentApp

__all__ = ['AgentFactory', 'AgentFactoryConfig', 'StitchLabAgentApp']

