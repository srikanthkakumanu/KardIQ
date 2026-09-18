import pytest

from app.config import Settings
from app.errors import ConfigurationError
from app.llm.llm_factory import build_chat_model


def test_builds_openai_model_when_provider_is_openai_and_key_present():
    settings = Settings(llm_provider="openai", openai_api_key="test-key", openai_model="gpt-4o-mini")

    model = build_chat_model(settings)

    assert model.model_name == "gpt-4o-mini"


def test_raises_when_openai_selected_without_api_key():
    settings = Settings(llm_provider="openai", openai_api_key=None)

    with pytest.raises(ConfigurationError):
        build_chat_model(settings)


def test_builds_groq_model_when_provider_is_groq_and_key_present():
    settings = Settings(llm_provider="groq", groq_api_key="test-key", groq_model="llama-3.1-8b-instant")

    model = build_chat_model(settings)

    assert model.model_name == "llama-3.1-8b-instant"


def test_raises_when_groq_selected_without_api_key():
    settings = Settings(llm_provider="groq", groq_api_key=None)

    with pytest.raises(ConfigurationError):
        build_chat_model(settings)


def test_raises_for_unsupported_provider():
    settings = Settings(llm_provider="anthropic")

    with pytest.raises(ConfigurationError):
        build_chat_model(settings)
