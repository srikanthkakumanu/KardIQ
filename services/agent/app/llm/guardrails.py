import logging
import time

from app.config import Settings
from app.errors import LlmGuardrailError

logger = logging.getLogger(__name__)

_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
_BASE_BACKOFF_SECONDS = 0.5


def invoke_with_guardrails(model, messages, settings: Settings):
    """Calls model.invoke(messages), retrying transient provider failures
    (429/5xx) up to LLM_MAX_RETRIES times with exponential backoff. Timeouts
    and non-retryable failures raise immediately as a structured
    LlmGuardrailError rather than an unhandled exception, per
    services/agent/CLAUDE.md's Guardrails section. The actual per-call HTTP
    timeout is enforced by the `timeout=` the provider client was built
    with in llm_factory.py; this function only decides whether to retry."""
    attempt = 0
    while True:
        attempt += 1
        try:
            return model.invoke(messages)
        except Exception as exc:
            if _is_timeout(exc):
                raise LlmGuardrailError("LLM_TIMEOUT", "The LLM provider did not respond in time") from exc

            status_code = getattr(exc, "status_code", None)
            if status_code in _RETRYABLE_STATUS_CODES and attempt <= settings.llm_max_retries:
                backoff_seconds = _BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))
                logger.warning(
                    "Retrying LLM call after transient error (attempt %s/%s): %s",
                    attempt, settings.llm_max_retries, exc,
                )
                time.sleep(backoff_seconds)
                continue

            if status_code in _RETRYABLE_STATUS_CODES:
                raise LlmGuardrailError("LLM_RETRIES_EXHAUSTED", "LLM provider failed after retries") from exc

            raise LlmGuardrailError("LLM_REQUEST_FAILED", str(exc)) from exc


def _is_timeout(exc: Exception) -> bool:
    return "Timeout" in type(exc).__name__
