from typing import Generic, TypeVar, Optional, Literal
from pydantic import BaseModel
import litellm
import logging
import os
import ssl
import urllib.request


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

        # Configure SSL verification based on VERIFY_CERTIFICATE setting
        self._configure_ssl_verification(settings.VERIFY_CERTIFICATE)

        if settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
            litellm.success_callback = ["langfuse"]
            litellm.failure_callback = ["langfuse"]
        
        self._initialized = True

        return
    
    def _configure_ssl_verification(self, verify: bool):
        """Configure SSL certificate verification for HTTP clients.
        
        This affects:
        - urllib (used by tiktoken for downloading encoding files)
        - requests (used by various libraries)
        - litellm HTTP clients
        
        Args:
            verify: If False, disable SSL verification (for corporate proxies)
        """
        if not verify:
            self.logger.warning(
                "SSL certificate verification is DISABLED. "
                "This should only be used in corporate environments with proxy certificates."
            )
            
            # Disable SSL verification for urllib (used by tiktoken)
            # Create an unverified SSL context
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Monkey patch urllib's default HTTPS handler to use unverified context
            # This is needed for tiktoken which uses urllib to download encoding files
            https_handler = urllib.request.HTTPSHandler(context=ssl_context)
            opener = urllib.request.build_opener(https_handler)
            urllib.request.install_opener(opener)
            
            # Configure requests library (used by litellm and other libraries)
            # Set environment variable that requests respects
            os.environ['CURL_CA_BUNDLE'] = ''
            os.environ['REQUESTS_CA_BUNDLE'] = ''
            
            # Configure litellm to not verify SSL
            litellm.ssl_verify = False
            
            self.logger.info("SSL verification disabled for urllib, requests, and litellm")
        else:
            self.logger.info("SSL certificate verification is ENABLED")
            # Ensure litellm uses default SSL verification
            litellm.ssl_verify = True