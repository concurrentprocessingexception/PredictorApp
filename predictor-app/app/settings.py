from pydantic_settings import BaseSettings
from pydantic import AnyUrl
from typing import List


class Settings(BaseSettings):
    database_url: AnyUrl
    finnhub_api_key: str
    allow_origins: List[str] = ["http://localhost:5173"]
    upload_enabled: bool = False

    class Config:
        env_file = ".env"
        env_prefix = ""
        case_sensitive = False


settings = Settings()