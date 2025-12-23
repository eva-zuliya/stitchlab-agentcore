from dotenv import load_dotenv
load_dotenv()


from utils.config import GlobalConfig, BaseSettings, BaseModelRegistry


class GlobalSettings(BaseSettings):
    APP_NAME: str = 'Agent Test'
    MCP_URL: str = 'test'


class GlobalModelRegistry(BaseModelRegistry):
    pass


class AppConfig(GlobalConfig[GlobalSettings, BaseModelRegistry]):
    pass