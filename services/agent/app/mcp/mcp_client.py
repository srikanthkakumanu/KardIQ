import httpx

from app.errors import DownstreamError

# The only network egress point to the MCP server, per services/agent/CLAUDE.md's
# boundary rule that the agent must not embed any other internal service URL.


class McpClient:
    def __init__(self, base_url: str, timeout_seconds: float):
        self._client = httpx.Client(base_url=base_url.rstrip("/"), timeout=timeout_seconds)

    def list_tools(self, request_id: str) -> list[dict]:
        return self._request("GET", "/tools", request_id)

    def call_tool(self, tool_name: str, arguments: dict, request_id: str) -> dict:
        return self._request("POST", f"/tools/{tool_name}/call", request_id, json=arguments)

    def _request(self, method: str, path: str, request_id: str, **kwargs):
        headers = {"X-Request-Id": request_id}
        try:
            response = self._client.request(method, path, headers=headers, **kwargs)
        except httpx.TimeoutException as exc:
            raise DownstreamError("MCP_TIMEOUT", "MCP server request timed out") from exc
        except httpx.RequestError as exc:
            raise DownstreamError("MCP_UNAVAILABLE", str(exc)) from exc

        if response.status_code >= 400:
            raise DownstreamError(
                "MCP_ERROR", _extract_message(response), status_code=response.status_code
            )
        return response.json()


def _extract_message(response: httpx.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        return response.text or f"HTTP {response.status_code}"
    if isinstance(body, dict) and "detail" in body:
        return str(body["detail"])
    return response.text or f"HTTP {response.status_code}"
