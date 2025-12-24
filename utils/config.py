from typing import Generic, TypeVar, Optional, Literal
from pydantic import BaseModel
from litellm import Router
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


class BaseModelRegistry(BaseModel):
    CLAUDE3_5_SONNET: str = "bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0"
    NOVA_PRO: str = "bedrock/us.amazon.nova-pro-v1:0"
    QWEN3_480B: str = "bedrock/qwen.qwen3-coder-480b-a35b-v1:0"


TSettings = TypeVar("TSettings", bound=BaseModel)
TModelRegistry = TypeVar("TModelRegistry", bound=BaseModel)


class GlobalConfig(Generic[TSettings, TModelRegistry]):
    _instance: "GlobalConfig | None" = None
    _initialized: bool = False
    _model_router: Router

    settings: TSettings
    model_registry: TModelRegistry
    logger: logging.Logger
    

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


    def __init__(
        self,
        settings: TSettings | None = None,
        models: TModelRegistry | None = None
    ):
        if self._initialized:
            return

        if settings is None:
            raise RuntimeError(
                "GlobalConfig must be initialized once with settings. Inherit from class config.BaseModel"
            )

        if models is None:
            raise RuntimeError(
                "GlobalConfig must be initialized once with models registry. Inherit from class config.BaseModelRegistry"
            )

        self.settings = settings
        self.model_registry = models

        model_list = []
        for name, value in models.model_dump().items():
            litellm_params = {
                "model": value
            }
            
            if settings.BEDROCK_GUARDRAIL_ID is not None and settings.BEDROCK_GUARDRAIL_VER is not None:
                litellm_params["guardrailIdentifier"] = settings.BEDROCK_GUARDRAIL_ID
                litellm_params["guardrailVersion"] = settings.BEDROCK_GUARDRAIL_VER
            
            model_list.append(
                {
                    "model_name": name,
                    "litellm_params": litellm_params
                }
            )

        self._model_router = Router(model_list=model_list)

        logging.basicConfig(
            level=logging.DEBUG if settings.DEBUG else logging.INFO,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        )

        self.logger = logging.getLogger(settings.APP_NAME)
        
        self._initialized = True

        return