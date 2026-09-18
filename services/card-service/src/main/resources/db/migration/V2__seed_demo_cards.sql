-- Seed data for the LangChain/OpenAI worked example from the root CLAUDE.md.
-- Fixed UUIDs so downstream services (graph-rag, scripts/seed-data.sh) can
-- reference these cards deterministically without a lookup round trip.
INSERT INTO cards (id, title, body, created_at, updated_at) VALUES
    (
        '11111111-1111-1111-1111-111111111111',
        'LangChain',
        'LangChain is a framework for building applications powered by large language models. It provides abstractions for prompts, chains, agents, and tool integrations.',
        now(),
        now()
    ),
    (
        '22222222-2222-2222-2222-222222222222',
        'OpenAI',
        'OpenAI provides large language models, such as the GPT family, accessible through an API. It is commonly used as the reasoning engine behind LLM-powered applications like LangChain.',
        now(),
        now()
    );

INSERT INTO card_tags (card_id, tag) VALUES
    ('11111111-1111-1111-1111-111111111111', 'framework'),
    ('11111111-1111-1111-1111-111111111111', 'llm'),
    ('22222222-2222-2222-2222-222222222222', 'llm'),
    ('22222222-2222-2222-2222-222222222222', 'provider');
