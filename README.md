# StitchLab Agent Core

A powerful agent core application built with modern Python frameworks for AI agent development.

## Features

- FastAPI-based runtime environment
- Support for multiple AI backends via LiteLLM
- Langfuse integration for monitoring and observability
- MCP (Model Context Protocol) support
- Pydantic-based schema validation
- Asyncio-native async/await support

## Installation

Install from PyPI:

```bash
pip install stitchlab-agentcore
```

### Requirements

- Python 3.11 or higher

## Quick Start

### Basic Example

Here's a complete example of how to use the StitchLab Agent Core library:

```python
import os
from dotenv import load_dotenv
load_dotenv()

from stitchlab_agentcore.runtime.factory import AgentFactory
from stitchlab_agentcore.runtime.app import StitchLabAgentCoreApp
from stitchlab_agentcore.config import GlobalConfig, BaseSettings

from typing import Optional
from strands import Agent, tool
import logging

logger = logging.getLogger(__name__)


class GlobalSettings(BaseSettings):
    APP_NAME: str = 'Strands Agent App'
    VERBOSE: bool = os.getenv('VERBOSE', 'True').lower() in ('true', '1', 'yes')
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
    VERIFY_CERTIFICATE: bool = os.getenv('VERIFY_CERTIFICATE', 'True').lower() in ('true', '1', 'yes')

    MCP_URL: str = os.getenv('MCP_URL', 'http://localhost:8000/mcp')
    MCP_TOOLS: list[str] = [tool.strip() for tool in os.getenv('MCP_TOOLS', '-').split(',')]
    
    MODEL_ID: str = os.getenv('BEDROCK_MODEL_ID', 'CLAUDE_3_5_SONNET')
    MEMORY_ID: str = os.getenv('BEDROCK_AGENTCORE_MEMORY_ID', '')
    BEDROCK_REGION: str = os.getenv('BEDROCK_REGION', '')
    BEDROCK_GUARDRAIL_TRACE: str = "disabled"
    BEDROCK_GUARDRAIL_ID: Optional[str] = None
    BEDROCK_GUARDRAIL_VER: Optional[str] = None

    LANGFUSE_PUBLIC_KEY: Optional[str] = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY: Optional[str] = os.getenv("LANGFUSE_SECRET_KEY")
    LANGFUSE_HOST: Optional[str] = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")


class AppConfig(GlobalConfig[GlobalSettings]):
    pass

CONFIG = AppConfig(GlobalSettings())


@tool
def subtract(a: int, b: int) -> int:
    """Calculate the difference between two numbers"""
    return a - b

@tool
def multiply(a: int, b: int) -> int:
    """Calculate the product of two numbers"""
    return a * b


SYSTEM_PROMPT = """
You are a good friend.. Be nice
"""


TOOLS = [
    subtract,
    multiply
]

AGENT_FACTORY = AgentFactory(
    system_prompt=SYSTEM_PROMPT,
    local_tools=TOOLS,
    config=CONFIG
)

async def create_agent(actor_id: str, session_id: str) -> Optional[Agent]:
    return await AGENT_FACTORY.create_agent(actor_id=actor_id, session_id=session_id)


app = StitchLabAgentCoreApp(debug=True).initialize()

@app.agent_entrypoint(create_agent)
async def agent_invocation(payload):
    pass


if __name__ == "__main__":
    CONFIG.logger.info(f"Starting {CONFIG.settings.APP_NAME} on FastAPI server...")
    app.run()
```

## Configuration

Configure the application using environment variables or `.env` file:

```env
# Add your configuration here
```

## Architecture

The StitchLab Agent Core provides:

- **Runtime**: FastAPI-based application runtime for agents
- **Schema**: Pydantic models for data validation
- **Config**: Centralized configuration management
- **Assets**: Built-in resources and caching

## Development

### Install dev dependencies

```bash
pip install -e ".[dev]"
```

### Running tests

```bash
pytest
```

### Code formatting

```bash
black src/
ruff check src/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/eva-zuliya/stitchlab-agentcore).
