from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from app.config import Settings
from app.errors import ConfigurationError


def build_chat_model(settings: Settings):
    """Fails fast (raises ConfigurationError) when the selected provider is
    missing its API key, per services/agent/CLAUDE.md. max_retries=0 here
    deliberately: retries are handled explicitly by app.llm.guardrails so
    the retry policy is inspectable and testable in one place."""
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise ConfigurationError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            timeout=settings.llm_request_timeout_seconds,
            max_tokens=settings.llm_max_output_tokens,
            max_retries=0,
        )
    if settings.llm_provider == "groq":
        if not settings.groq_api_key:
            raise ConfigurationError("GROQ_API_KEY is required when LLM_PROVIDER=groq")
        return ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            timeout=settings.llm_request_timeout_seconds,
            max_tokens=settings.llm_max_output_tokens,
            max_retries=0,
        )
    raise ConfigurationError(f"Unsupported LLM_PROVIDER: {settings.llm_provider!r}")
