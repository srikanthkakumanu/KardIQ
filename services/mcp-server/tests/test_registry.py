from app.tools import TOOL_REGISTRY


def test_registry_contains_all_four_required_tools():
    assert set(TOOL_REGISTRY.keys()) == {"list_cards", "create_card", "graph_search", "health_report"}


def test_every_tool_declares_name_description_and_json_schemas():
    for name, spec in TOOL_REGISTRY.items():
        assert spec.name == name
        assert spec.description
        assert spec.primary_service
        assert spec.input_model.model_json_schema()["type"] == "object"
        assert spec.output_model.model_json_schema()["type"] == "object"
