from typing import Generic, TypeVar, Optional, Literal
from pydantic import BaseModel
import litellm
import logging
import os
import pathlib
import shutil


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

        # Configure tiktoken to use local cache file before any imports that might use it
        self._setup_tiktoken_cache()

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
    
    def _setup_tiktoken_cache(self):
        """Configure tiktoken to use local cache file to avoid SSL certificate issues.
        
        This sets up the TIKTOKEN_CACHE_DIR environment variable to point to a directory
        containing the pre-cached cl100k_base.tiktoken file, preventing tiktoken from
        attempting to download it over the network (which can fail in corporate environments
        with SSL certificate verification issues).
        
        Tiktoken expects files to be in TIKTOKEN_CACHE_DIR/encodings/ directory.
        """
        # Only set if not already configured
        if os.environ.get("TIKTOKEN_CACHE_DIR"):
            return
        
        # Find the project root directory (where this config.py file is located)
        # and look for cl100k_base.tiktoken file
        project_root = pathlib.Path(__file__).parent.absolute()
        source_tiktoken_file = project_root / "cl100k_base.tiktoken"
        
        if source_tiktoken_file.exists():
            # Create a cache directory structure: .tiktoken_cache/encodings/
            cache_dir = project_root / ".tiktoken_cache"
            encodings_dir = cache_dir / "encodings"
            encodings_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy the file to the encodings directory if it doesn't exist there
            target_tiktoken_file = encodings_dir / "cl100k_base.tiktoken"
            if not target_tiktoken_file.exists():
                shutil.copy2(source_tiktoken_file, target_tiktoken_file)
                logging.info(f"Copied cl100k_base.tiktoken to cache directory: {target_tiktoken_file}")
            
            # Set TIKTOKEN_CACHE_DIR to the cache directory
            os.environ["TIKTOKEN_CACHE_DIR"] = str(cache_dir)
            logging.info(f"Configured tiktoken cache directory to: {cache_dir}")
        else:
            # If file doesn't exist, log a warning
            logging.warning(
                f"cl100k_base.tiktoken file not found at {source_tiktoken_file}. "
                "Tiktoken will attempt to download it, which may fail in corporate networks."
            )