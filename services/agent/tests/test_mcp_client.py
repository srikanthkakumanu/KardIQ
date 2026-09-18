import httpx
import pytest

from app.errors import DownstreamError
from app.mcp.mcp_client import McpClient


def _client_with_handler(handler) -> McpClient:
    client = McpClient("http://test", timeout_seconds=1.0)
    client._client = httpx.Client(base_url="http://test", transport=httpx.MockTransport(handler))
    return client


def test_list_tools_returns_parsed_json():
    def handler(request):
        assert request.url.path == "/tools"
        return httpx.Response(200, json=[{"name": "list_cards"}])

    client = _client_with_handler(handler)

    assert client.list_tools("req-1") == [{"name": "list_cards"}]


def test_call_tool_posts_arguments_to_the_right_path_and_forwards_request_id():
    seen = {}

    def handler(request):
        seen["path"] = request.url.path
        seen["header"] = request.headers.get("x-request-id")
        return httpx.Response(200, json={"tool": "graph_search", "success": True})

    client = _client_with_handler(handler)

    result = client.call_tool("graph_search", {"query": "LangChain"}, "req-42")

    assert seen["path"] == "/tools/graph_search/call"
    assert seen["header"] == "req-42"
    assert result["success"] is True


def test_error_status_raises_downstream_error_with_status_code():
    def handler(request):
        return httpx.Response(500, json={"detail": "boom"})

    client = _client_with_handler(handler)

    with pytest.raises(DownstreamError) as exc_info:
        client.list_tools("req-1")

    assert exc_info.value.status_code == 500
    assert exc_info.value.message == "boom"


def test_connection_failure_raises_downstream_unavailable():
    def handler(request):
        raise httpx.ConnectError("down")

    client = _client_with_handler(handler)

    with pytest.raises(DownstreamError) as exc_info:
        client.list_tools("req-1")

    assert exc_info.value.code == "MCP_UNAVAILABLE"


def test_timeout_raises_downstream_timeout():
    def handler(request):
        raise httpx.ReadTimeout("too slow")

    client = _client_with_handler(handler)

    with pytest.raises(DownstreamError) as exc_info:
        client.list_tools("req-1")

    assert exc_info.value.code == "MCP_TIMEOUT"
