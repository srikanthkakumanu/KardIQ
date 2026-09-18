import httpx

from app.errors import DownstreamError


class BaseServiceClient:
    """Shared request/error-mapping logic for the two typed downstream
    clients. Every downstream call has a timeout and forwards the inbound
    X-Request-Id, per services/mcp-server/CLAUDE.md."""

    def __init__(self, service_name: str, base_url: str, timeout_seconds: float):
        self._service_name = service_name
        self._client = httpx.Client(base_url=base_url.rstrip("/"), timeout=timeout_seconds)

    def _request(self, method: str, path: str, request_id: str, **kwargs) -> dict:
        headers = {"X-Request-Id": request_id}
        try:
            response = self._client.request(method, path, headers=headers, **kwargs)
        except httpx.TimeoutException as exc:
            raise DownstreamError(self._service_name, "DOWNSTREAM_TIMEOUT", "Request timed out") from exc
        except httpx.RequestError as exc:
            raise DownstreamError(self._service_name, "DOWNSTREAM_UNAVAILABLE", str(exc)) from exc

        if response.status_code >= 400:
            raise DownstreamError(
                self._service_name,
                _error_code_for_status(response.status_code),
                _extract_message(response),
                status_code=response.status_code,
            )
        return response.json()


def _error_code_for_status(status_code: int) -> str:
    if status_code == 404:
        return "NOT_FOUND"
    if status_code in (400, 422):
        return "VALIDATION_ERROR"
    if status_code < 500:
        return "DOWNSTREAM_CLIENT_ERROR"
    return "DOWNSTREAM_ERROR"


def _extract_message(response: httpx.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        return response.text or f"HTTP {response.status_code}"
    if isinstance(body, dict) and "message" in body:
        return body["message"]
    return response.text or f"HTTP {response.status_code}"
