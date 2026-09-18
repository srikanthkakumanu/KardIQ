from app.clients.base import BaseServiceClient


class CardServiceClient(BaseServiceClient):
    def __init__(self, base_url: str, timeout_seconds: float):
        super().__init__("card-service", base_url, timeout_seconds)

    def list_cards(self, page: int, size: int, request_id: str) -> dict:
        return self._request("GET", "/api/v1/cards", request_id, params={"page": page, "size": size})

    def create_card(self, payload: dict, request_id: str) -> dict:
        return self._request("POST", "/api/v1/cards", request_id, json=payload)

    def health(self, request_id: str) -> dict:
        return self._request("GET", "/actuator/health", request_id)
