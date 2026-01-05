from typing import Generic, TypeVar, Optional, Literal
from pydantic import BaseModel
import litellm
import logging
import os
import urllib3
import requests
from importlib.resources import files
import base64
from langfuse import Langfuse


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
    langfuse: Optional[Langfuse] = None
    

    def __new__(cls, *args, **kwargs):
        if cls is GlobalConfig:
            raise TypeError("GlobalConfig is abstract")

        if GlobalConfig._instance is None:
            GlobalConfig._instance = super().__new__(cls)
        
        return GlobalConfig._instance

    @classmethod
    def get(cls) -> "GlobalConfig":
        if GlobalConfig._instance is None:
            raise RuntimeError(
                "GlobalConfig is not initialized. "
                "Initialize it in the application bootstrap."
            )

        return GlobalConfig._instance


    def __init__(self, settings: TSettings | None = None):
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

        # Define the path to your pre-downloaded tiktoken cache folder
        # Works both in development and when installed as a library
        try:
            asset_path = files("stitchlab_agentcore").joinpath("assets", "tiktoken_cache")
            tiktoken_cache_dir = str(asset_path)
            if os.path.isdir(tiktoken_cache_dir):
                os.environ["TIKTOKEN_CACHE_DIR"] = tiktoken_cache_dir
        except (TypeError, ModuleNotFoundError):
            # Fallback for development environments
            tiktoken_cache_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "assets", "tiktoken_cache")
            )
            if os.path.isdir(tiktoken_cache_dir):
                os.environ["TIKTOKEN_CACHE_DIR"] = tiktoken_cache_dir

        if not self.settings.VERIFY_CERTIFICATE:        
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            # Patch the requests.get to accept the verify parameter and disable SSL
            _original_get = requests.get
            def patched_get(url, **kwargs):
                kwargs['verify'] = False
                return _original_get(url, **kwargs)

            requests.get = patched_get

        if settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY and settings.LANGFUSE_HOST:
            self.langfuse = Langfuse(
                public_key=settings.LANGFUSE_PUBLIC_KEY,
                secret_key=settings.LANGFUSE_SECRET_KEY,
                host=settings.LANGFUSE_HOST
            )
            
            # Set up OpenTelemetry exporter for Langfuse (Strands SDK native integration)
            langfuse_base_url = settings.LANGFUSE_HOST
            
            # Build Basic Auth header
            langfuse_auth = base64.b64encode(
                f"{settings.LANGFUSE_PUBLIC_KEY}:{settings.LANGFUSE_SECRET_KEY}".encode()
            ).decode()
            
            # Configure OpenTelemetry endpoint & headers for Strands SDK
            # Note: Langfuse OTLP endpoint uses /api/public/otel/v1/traces
            os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = f"{langfuse_base_url}/api/public/otel"
            os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {langfuse_auth}"
            os.environ["OTEL_EXPORTER_OTLP_TIMEOUT"] = "30"  # 30 seconds
            
            # Set up Strands OpenTelemetry exporter once at config initialization
            try:
                from strands.telemetry import StrandsTelemetry
                # This sets up the OTLP exporter (configured via env vars above)
                strands_telemetry = StrandsTelemetry()
                strands_telemetry.setup_otlp_exporter()
                self.logger.info(f"Strands OpenTelemetry exporter configured for Langfuse at {langfuse_base_url}")
                self.logger.debug(f"OTEL endpoint: {os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT')}")

            except ImportError as e:
                self.logger.error(f"Could not import StrandsTelemetry. Make sure opentelemetry-exporter-otlp-proto-http is installed: {e}")

            except Exception as e:
                self.logger.error(f"Could not set up Strands OpenTelemetry: {e}", exc_info=True)
            
            # Also set up litellm callbacks for any direct litellm usage
            litellm.success_callback = ["langfuse"]
            litellm.failure_callback = ["langfuse"]
        
        self._initialized = True

        return