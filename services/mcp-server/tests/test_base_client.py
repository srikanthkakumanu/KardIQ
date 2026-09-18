import httpx
import pytest

from app.clients.base import BaseServiceClient
from app.errors import DownstreamError


def _client_with_handler(handler) -> BaseServiceClient:
    client = BaseServiceClient("test-service", "http://test", timeout_seconds=1.0)
    client._client = httpx.Client(base_url="http://test", transport=httpx.MockTransport(handler))
    return client


def test_successful_response_returns_parsed_json():
    def handler(request):
        return httpx.Response(200, json={"ok": True})

    client = _client_with_handler(handler)

    assert client._request("GET", "/thing", "req-1") == {"ok": True}


def test_request_forwards_the_inbound_x_request_id_header():
    seen = {}

    def handler(request):
        seen["header"] = request.headers.get("x-request-id")
        return httpx.Response(200, json={})

    client = _client_with_handler(handler)

    client._request("GET", "/thing", "abc-123")

    assert seen["header"] == "abc-123"


def test_404_raises_downstream_error_with_not_found_code_and_message():
    def handler(request):
        return httpx.Response(404, json={"code": "CARD_NOT_FOUND", "message": "nope"})

    client = _client_with_handler(handler)

    with pytest.raises(DownstreamError) as exc_info:
        client._request("GET", "/thing", "req-1")

    assert exc_info.value.code == "NOT_FOUND"
    assert exc_info.value.message == "nope"
    assert exc_info.value.status_code == 404


def test_500_raises_downstream_error():
    def handler(request):
        return httpx.Response(500, json={"code": "INTERNAL_ERROR", "message": "boom"})

    client = _client_with_handler(handler)

    with pytest.raises(DownstreamError) as exc_info:
        client._request("GET", "/thing", "req-1")

    assert exc_info.value.code == "DOWNSTREAM_ERROR"
    assert exc_info.value.status_code == 500


def test_connect_error_raises_downstream_unavailable():
    def handler(request):
        raise httpx.ConnectError("boom")

    client = _client_with_handler(handler)

    with pytest.raises(DownstreamError) as exc_info:
        client._request("GET", "/thing", "req-1")

    assert exc_info.value.code == "DOWNSTREAM_UNAVAILABLE"


def test_timeout_raises_downstream_timeout():
    def handler(request):
        raise httpx.ReadTimeout("too slow")

    client = _client_with_handler(handler)

    with pytest.raises(DownstreamError) as exc_info:
        client._request("GET", "/thing", "req-1")

    assert exc_info.value.code == "DOWNSTREAM_TIMEOUT"
