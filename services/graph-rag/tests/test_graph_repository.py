from unittest.mock import MagicMock

from app.domain.models import CardNode, GraphRelationship
from app.repository.graph_repository import GraphRepository


def _mock_driver():
    driver = MagicMock()
    session = MagicMock()
    driver.session.return_value.__enter__.return_value = session
    return driver, session


def test_upsert_card_passes_values_as_parameters_not_string_concatenation():
    driver, session = _mock_driver()
    repository = GraphRepository(driver)

    repository.upsert_card(CardNode(id="1", title="T", body="B", tags=["a"], updated_at="2024-01-01T00:00:00Z"))

    args, kwargs = session.run.call_args
    query = args[0]
    assert "$id" in query and "$title" in query
    assert "1" not in query
    assert kwargs["id"] == "1"
    assert kwargs["title"] == "T"
    assert kwargs["tags"] == ["a"]


def test_upsert_relationship_passes_values_as_parameters():
    driver, session = _mock_driver()
    repository = GraphRepository(driver)

    repository.upsert_relationship(
        GraphRelationship(source_id="1", target_id="2", label="USES", weight=1.0, created_at="2024-01-01T00:00:00Z")
    )

    args, kwargs = session.run.call_args
    assert "$source_id" in args[0] and "$target_id" in args[0]
    assert kwargs["source_id"] == "1"
    assert kwargs["target_id"] == "2"
    assert kwargs["label"] == "USES"


def test_card_exists_returns_true_when_record_found():
    driver, session = _mock_driver()
    session.run.return_value.single.return_value = {"id": "1"}
    repository = GraphRepository(driver)

    assert repository.card_exists("1") is True


def test_card_exists_returns_false_when_no_record():
    driver, session = _mock_driver()
    session.run.return_value.single.return_value = None
    repository = GraphRepository(driver)

    assert repository.card_exists("missing") is False


def test_keyword_match_passes_extracted_keywords_as_a_parameter():
    driver, session = _mock_driver()
    session.run.return_value = []
    repository = GraphRepository(driver)

    repository.keyword_match("LangChain", 5)

    args, kwargs = session.run.call_args
    assert "LangChain" not in args[0]
    assert kwargs["keywords"] == ["langchain"]
    assert kwargs["limit"] == 5


def test_keyword_match_reduces_a_natural_language_question_to_meaningful_keywords():
    driver, session = _mock_driver()
    session.run.return_value = []
    repository = GraphRepository(driver)

    repository.keyword_match("How does LangChain connect to OpenAI?", 5)

    args, kwargs = session.run.call_args
    assert kwargs["keywords"] == ["langchain", "connect", "openai"]


def test_keyword_match_returns_empty_without_querying_when_no_keywords_remain():
    driver, session = _mock_driver()
    repository = GraphRepository(driver)

    result = repository.keyword_match("is the a", 5)

    assert result == []
    session.run.assert_not_called()


def test_one_hop_expand_passes_card_ids_as_a_parameter():
    driver, session = _mock_driver()
    session.run.return_value = []
    repository = GraphRepository(driver)

    repository.one_hop_expand(["1", "2"])

    args, kwargs = session.run.call_args
    assert kwargs["card_ids"] == ["1", "2"]
