from app.services.retrieval_service import RetrievalService


class FakeRepository:
    def __init__(self, matches, expanded):
        self._matches = matches
        self._expanded = expanded

    def keyword_match(self, query, limit):
        return self._matches

    def one_hop_expand(self, card_ids):
        return self._expanded


def test_exact_title_match_is_ranked_before_body_only_match():
    matches = [
        {"id": "2", "title": "Body mentions LangChain", "tags": [], "exact_match": False},
        {"id": "1", "title": "LangChain", "tags": ["framework"], "exact_match": True},
    ]
    service = RetrievalService(FakeRepository(matches, []))

    result = service.search("LangChain", limit=5)

    assert [card["id"] for card in result["matched_cards"]] == ["1", "2"]


def test_context_text_includes_expanded_relationships_in_the_true_stored_direction():
    matches = [{"id": "1", "title": "LangChain", "tags": [], "exact_match": True}]
    expanded = [
        {"source_id": "1", "source_title": "LangChain", "target_id": "2", "target_title": "OpenAI", "label": "USES"}
    ]
    service = RetrievalService(FakeRepository(matches, expanded))

    result = service.search("LangChain", limit=5)

    assert result["relationships"] == [{"source_id": "1", "target_id": "2", "label": "USES"}]
    assert result["context_text"].endswith("LangChain USES OpenAI")
    assert set(result["source_ids"]) == {"1", "2"}


def test_source_ids_include_both_endpoints_even_when_only_the_target_card_matched():
    # Only "2" (OpenAI) matched the keyword search, but the expansion found
    # the true edge "1" (LangChain) --USES--> "2" (OpenAI); both ids should
    # still show up in source_ids so a caller can trace back to LangChain.
    matches = [{"id": "2", "title": "OpenAI", "tags": [], "exact_match": True}]
    expanded = [
        {"source_id": "1", "source_title": "LangChain", "target_id": "2", "target_title": "OpenAI", "label": "USES"}
    ]
    service = RetrievalService(FakeRepository(matches, expanded))

    result = service.search("OpenAI", limit=5)

    assert set(result["source_ids"]) == {"1", "2"}


def test_no_matches_returns_empty_result():
    service = RetrievalService(FakeRepository([], []))

    result = service.search("nothing", limit=5)

    assert result["matched_cards"] == []
    assert result["relationships"] == []
    assert result["context_text"] == ""
    assert result["source_ids"] == []
