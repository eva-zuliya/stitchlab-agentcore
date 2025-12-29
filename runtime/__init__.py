"""StitchLab Agent Core Runtime Library.

This package provides reusable components for building agents:
- AgentFactory: Optimized agent creation with caching
- AgentFactoryConfig: Configuration for agent factories
- StitchLabAgentCoreApp: Custom application wrapper
"""

from .factory import AgentFactory
from .app import StitchLabAgentCoreApp

__all__ = ['AgentFactory', 'StitchLabAgentCoreApp']

