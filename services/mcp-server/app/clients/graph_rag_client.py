from app.clients.base import BaseServiceClient


class GraphRagClient(BaseServiceClient):
    def __init__(self, base_url: str, timeout_seconds: float):
        super().__init__("graph-rag", base_url, timeout_seconds)

    def search(self, query: str, limit: int, request_id: str) -> dict:
        return self._request("POST", "/rag/search", request_id, json={"query": query, "limit": limit})

    def health(self, request_id: str) -> dict:
        return self._request("GET", "/health", request_id)
