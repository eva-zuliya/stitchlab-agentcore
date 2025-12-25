import os
from dotenv import load_dotenv
load_dotenv()

from typing import Optional
from config import GlobalConfig, BaseSettings


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


from strands import tool


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