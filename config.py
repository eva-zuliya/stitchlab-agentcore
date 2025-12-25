from typing import Generic, TypeVar, Optional, Literal
from pydantic import BaseModel
import litellm
import logging


class BaseSettings(BaseModel):
    APP_NAME: str = "Strands Agent App"
    VERBOSE: bool = True
    DEBUG: bool = True
    VERIFY_CERTIFICATE: bool = False
    MODEL_ID: str
    MEMORY_ID: str
    BEDROCK_REGION: str
    BEDROCK_GUARDRAIL_TRACE: Optional[Literal["enabled", "disabled"]] = "disabled"
    BEDROCK_GUARDRAIL_ID: Optional[str] = None
    BEDROCK_GUARDRAIL_VER: Optional[str] = None
    MCP_URL: Optional[str] = None
    MCP_TOOLS: Optional[list[str]] = None
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_HOST: Optional[str] = None


TSettings = TypeVar("TSettings", bound=BaseModel)

class GlobalConfig(Generic[TSettings]):
    _instance: "GlobalConfig | None" = None
    _initialized: bool = False

    settings: TSettings
    logger: logging.Logger
    

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


    def __init__(
        self,
        settings: TSettings | None = None,
    ):
        if self._initialized:
            return

        if settings is None:
            raise RuntimeError(
                "GlobalConfig must be initialized once with settings. Inherit from class config.BaseSettings"
            )

        self.settings = settings

        logging.basicConfig(
            level=logging.DEBUG if settings.DEBUG else logging.INFO,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        )

        self.logger = logging.getLogger(settings.APP_NAME)

        if settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
            litellm.success_callback = ["langfuse"]
            litellm.failure_callback = ["langfuse"]
        
        self._initialized = True

        return