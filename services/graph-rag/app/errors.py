class CardNotFoundError(Exception):
    """Raised when a relation references a card id that does not exist in the graph."""

    def __init__(self, *card_ids: str):
        self.card_ids = card_ids
        super().__init__(f"Card(s) not found: {', '.join(card_ids)}")
