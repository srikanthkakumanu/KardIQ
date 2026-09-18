from neo4j import Driver

from app.domain.models import CardNode, GraphRelationship
from app.repository.graph_repository import GraphRepository
from app.util import now_iso

# Same fixed ids as services/card-service's V2__seed_demo_cards.sql, so the
# two services describe the same two cards for the LangChain/OpenAI worked
# example without a lookup round trip.
LANGCHAIN_ID = "11111111-1111-1111-1111-111111111111"
OPENAI_ID = "22222222-2222-2222-2222-222222222222"


def seed_demo_data(driver: Driver) -> None:
    """Idempotent: safe to call on every startup or repeatedly from
    scripts/seed-data.sh, per the seed-data requirement in
    services/graph-rag/CLAUDE.md."""
    repository = GraphRepository(driver)
    timestamp = now_iso()

    repository.upsert_card(
        CardNode(
            id=LANGCHAIN_ID,
            title="LangChain",
            body=(
                "LangChain is a framework for building applications powered by large "
                "language models. It provides abstractions for prompts, chains, agents, "
                "and tool integrations."
            ),
            tags=["framework", "llm"],
            updated_at=timestamp,
        )
    )
    repository.upsert_card(
        CardNode(
            id=OPENAI_ID,
            title="OpenAI",
            body=(
                "OpenAI provides large language models, such as the GPT family, accessible "
                "through an API. It is commonly used as the reasoning engine behind "
                "LLM-powered applications like LangChain."
            ),
            tags=["llm", "provider"],
            updated_at=timestamp,
        )
    )
    repository.upsert_relationship(
        GraphRelationship(
            source_id=LANGCHAIN_ID,
            target_id=OPENAI_ID,
            label="USES",
            weight=1.0,
            created_at=timestamp,
        )
    )
