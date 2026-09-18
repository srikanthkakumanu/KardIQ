from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    card_service_url: str = "http://localhost:8080"
    graph_rag_url: str = "http://localhost:8020"
    mcp_server_port: int = 8010
    downstream_timeout_seconds: float = 5.0

    model_config = SettingsConfigDict(case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
