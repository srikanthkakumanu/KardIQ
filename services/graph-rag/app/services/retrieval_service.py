from app.repository.graph_repository import GraphRepository

# Transparent retrieval, per graph-rag/CLAUDE.md: keyword match -> one-hop
# expand -> rank exact title/tag matches above body matches -> contextText.
# No embeddings until this is working and documented.


class RetrievalService:
    def __init__(self, repository: GraphRepository):
        self._repository = repository

    def search(self, query: str, limit: int) -> dict:
        matches = self._repository.keyword_match(query, limit)
        matches_sorted = sorted(matches, key=lambda m: not m.get("exact_match", False))

        matched_card_ids = [m["id"] for m in matches_sorted]
        expanded = self._repository.one_hop_expand(matched_card_ids) if matched_card_ids else []

        matched_cards = [
            {"id": m["id"], "title": m["title"], "tags": m.get("tags") or []}
            for m in matches_sorted
        ]
        relationships = [
            {"source_id": e["source_id"], "target_id": e["target_id"], "label": e["label"]}
            for e in expanded
        ]
        source_ids = sorted(
            {c["id"] for c in matched_cards}
            | {e["source_id"] for e in expanded}
            | {e["target_id"] for e in expanded}
        )

        return {
            "matched_cards": matched_cards,
            "relationships": relationships,
            "context_text": self._build_context_text(matched_cards, expanded),
            "source_ids": source_ids,
        }

    @staticmethod
    def _build_context_text(matched_cards: list[dict], expanded: list[dict]) -> str:
        if not matched_cards:
            return ""
        lines = [f"{card['title']} (id={card['id']})" for card in matched_cards]
        for edge in expanded:
            lines.append(f"{edge['source_title']} {edge['label']} {edge['target_title']}")
        return " | ".join(lines)
