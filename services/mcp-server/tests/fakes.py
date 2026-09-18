"""Fake downstream clients shared by the tool-level and route-level tests."""


class FakeCardServiceClient:
    def __init__(self):
        self.list_response = {"items": [], "page": 0, "size": 20, "totalElements": 0}
        self.create_response = {"id": "1", "title": "T", "body": "B", "tags": []}
        self.health_response = {"status": "UP"}
        self.raise_error: Exception | None = None

    def list_cards(self, page, size, request_id):
        if self.raise_error:
            raise self.raise_error
        return self.list_response

    def create_card(self, payload, request_id):
        if self.raise_error:
            raise self.raise_error
        return self.create_response

    def health(self, request_id):
        if self.raise_error:
            raise self.raise_error
        return self.health_response


class FakeGraphRagClient:
    def __init__(self):
        self.search_response = {"matchedCards": [], "relationships": [], "contextText": "", "sourceIds": []}
        self.health_response = {"status": "UP"}
        self.raise_error: Exception | None = None

    def search(self, query, limit, request_id):
        if self.raise_error:
            raise self.raise_error
        return self.search_response

    def health(self, request_id):
        if self.raise_error:
            raise self.raise_error
        return self.health_response
