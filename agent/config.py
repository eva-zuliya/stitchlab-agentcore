from dotenv import load_dotenv
load_dotenv()

from typing import Optional
from utils.config import GlobalConfig, BaseSettings, BaseModelRegistry


class GlobalSettings(BaseSettings):
    APP_NAME: str = 'Agent Test'
    MCP_URL: Optional[str] = 'http://localhost:8000/mcp'  # Local MCP server URL
    MCP_TOOLS: Optional[list[str]] = None  # List of MCP tool names to allow (None = all tools)


class GlobalModelRegistry(BaseModelRegistry):
    pass


class AppConfig(GlobalConfig[GlobalSettings, BaseModelRegistry]):
    pass