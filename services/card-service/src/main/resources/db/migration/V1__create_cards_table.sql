CREATE TABLE cards (
    id UUID PRIMARY KEY,
    title VARCHAR(120) NOT NULL,
    body VARCHAR(4000) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE card_tags (
    card_id UUID NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    tag VARCHAR(32) NOT NULL
);

CREATE INDEX idx_card_tags_card_id ON card_tags (card_id);
