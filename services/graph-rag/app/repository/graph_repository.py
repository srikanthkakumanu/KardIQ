import re

from neo4j import Driver

from app.domain.models import CardNode, GraphRelationship

# All Cypher for this service lives in this module, and every query is
# parameterized - never string-concatenated - per graph-rag/CLAUDE.md.

# A generic (not example-specific) English stopword list, so a natural
# question like "How does LangChain connect to OpenAI?" reduces to
# meaningful keywords ("langchain", "openai") instead of being matched as
# one long literal string against short card titles.
_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "how", "does", "do", "did", "to", "of", "in", "on", "for", "and", "or",
    "with", "what", "why", "when", "who", "which", "this", "that", "these",
    "those", "it", "its", "as", "at", "by", "from", "about",
}


def _extract_keywords(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [word for word in words if len(word) >= 3 and word not in _STOPWORDS]


class GraphRepository:
    def __init__(self, driver: Driver):
        self._driver = driver

    def upsert_card(self, card: CardNode) -> None:
        cypher = (
            "MERGE (c:Card {id: $id}) "
            "SET c.title = $title, c.body = $body, c.tags = $tags, c.updatedAt = $updated_at"
        )
        with self._driver.session() as session:
            session.run(
                cypher,
                id=card.id,
                title=card.title,
                body=card.body,
                tags=card.tags,
                updated_at=card.updated_at,
            )

    def card_exists(self, card_id: str) -> bool:
        cypher = "MATCH (c:Card {id: $id}) RETURN c.id AS id LIMIT 1"
        with self._driver.session() as session:
            return session.run(cypher, id=card_id).single() is not None

    def upsert_relationship(self, relationship: GraphRelationship) -> None:
        cypher = (
            "MATCH (source:Card {id: $source_id}) "
            "MATCH (target:Card {id: $target_id}) "
            "MERGE (source)-[r:RELATED_TO {label: $label}]->(target) "
            "SET r.weight = $weight, r.createdAt = coalesce(r.createdAt, $created_at)"
        )
        with self._driver.session() as session:
            session.run(
                cypher,
                source_id=relationship.source_id,
                target_id=relationship.target_id,
                label=relationship.label,
                weight=relationship.weight,
                created_at=relationship.created_at,
            )

    def keyword_match(self, query_text: str, limit: int) -> list[dict]:
        # query_text may be a full natural-language question, not a single
        # term, so it's reduced to keywords in Python first (a Neo4j
        # uniqueness/full-text index isn't needed for this small a graph).
        # Cypher param is named `keywords`, not `query`: neo4j's Session.run()
        # already has a positional parameter literally named `query` (the
        # Cypher text itself), so a keyword arg named `query` would collide.
        keywords = _extract_keywords(query_text)
        if not keywords:
            return []

        cypher = (
            "MATCH (c:Card) "
            "WHERE any(word IN $keywords WHERE toLower(c.title) CONTAINS word "
            "                              OR toLower(c.body) CONTAINS word "
            "                              OR any(tag IN c.tags WHERE toLower(tag) CONTAINS word)) "
            "RETURN c.id AS id, c.title AS title, c.tags AS tags, "
            "       any(word IN $keywords WHERE toLower(c.title) = word "
            "                              OR any(tag IN c.tags WHERE toLower(tag) = word)) AS exact_match "
            "LIMIT $limit"
        )
        with self._driver.session() as session:
            result = session.run(cypher, keywords=keywords, limit=limit)
            return [dict(record) for record in result]

    def one_hop_expand(self, card_ids: list[str]) -> list[dict]:
        # Matched undirected so a card on either end of a relationship still
        # gets expanded, but source_id/target_id come from startNode/endNode
        # so the reported direction is the *true* stored direction, not the
        # order cards happened to be traversed in. DISTINCT collapses the
        # duplicate row that an undirected match produces when both
        # endpoints of the same edge are in card_ids.
        cypher = (
            "MATCH (c:Card)-[r:RELATED_TO]-(other:Card) "
            "WHERE c.id IN $card_ids "
            "RETURN DISTINCT startNode(r).id AS source_id, startNode(r).title AS source_title, "
            "       endNode(r).id AS target_id, endNode(r).title AS target_title, r.label AS label"
        )
        with self._driver.session() as session:
            result = session.run(cypher, card_ids=card_ids)
            return [dict(record) for record in result]
