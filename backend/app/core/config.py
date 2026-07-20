from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    project_name: str = "AI Interview Intelligence Platform"
    version: str = "0.1.0"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"


settings = Settings()
