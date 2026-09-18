import pytest

from app.config import Settings
from app.errors import LlmGuardrailError
from app.llm.guardrails import invoke_with_guardrails


class FakeTimeoutError(Exception):
    pass


class FakeProviderStatusError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code
        super().__init__(f"status {status_code}")


class FakeResponse:
    def __init__(self, content):
        self.content = content


class FakeChatModel:
    def __init__(self, side_effects):
        self._side_effects = list(side_effects)
        self.calls = 0

    def invoke(self, messages):
        self.calls += 1
        effect = self._side_effects.pop(0)
        if isinstance(effect, Exception):
            raise effect
        return effect


@pytest.fixture(autouse=True)
def no_real_sleep(monkeypatch):
    monkeypatch.setattr("app.llm.guardrails.time.sleep", lambda _seconds: None)


def _settings(max_retries=2):
    return Settings(llm_provider="openai", openai_api_key="test-key", llm_max_retries=max_retries)


def test_returns_response_on_first_success():
    model = FakeChatModel([FakeResponse("hello")])

    result = invoke_with_guardrails(model, [], _settings())

    assert result.content == "hello"
    assert model.calls == 1


def test_retries_transient_error_then_succeeds():
    model = FakeChatModel([FakeProviderStatusError(503), FakeResponse("hello")])

    result = invoke_with_guardrails(model, [], _settings(max_retries=2))

    assert result.content == "hello"
    assert model.calls == 2


def test_gives_up_after_max_retries_exhausted():
    model = FakeChatModel([FakeProviderStatusError(503), FakeProviderStatusError(503)])

    with pytest.raises(LlmGuardrailError) as exc_info:
        invoke_with_guardrails(model, [], _settings(max_retries=1))

    assert exc_info.value.code == "LLM_RETRIES_EXHAUSTED"
    assert model.calls == 2


def test_timeout_raises_immediately_without_retry():
    model = FakeChatModel([FakeTimeoutError("too slow")])

    with pytest.raises(LlmGuardrailError) as exc_info:
        invoke_with_guardrails(model, [], _settings(max_retries=3))

    assert exc_info.value.code == "LLM_TIMEOUT"
    assert model.calls == 1


def test_non_retryable_error_raises_immediately():
    model = FakeChatModel([FakeProviderStatusError(400)])

    with pytest.raises(LlmGuardrailError) as exc_info:
        invoke_with_guardrails(model, [], _settings(max_retries=3))

    assert exc_info.value.code == "LLM_REQUEST_FAILED"
    assert model.calls == 1
