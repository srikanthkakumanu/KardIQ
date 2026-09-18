from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_provider: str = "openai"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    groq_api_key: str | None = None
    groq_model: str = "llama-3.1-8b-instant"
    mcp_server_url: str = "http://localhost:8010"
    mcp_request_timeout_seconds: float = 5.0
    agent_port: int = 8000
    llm_request_timeout_seconds: float = 20.0
    llm_max_output_tokens: int = 800
    llm_max_retries: int = 2

    model_config = SettingsConfigDict(case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
