# Sequence Diagram: Asking a Question

The exact worked example from the root `CLAUDE.md`: "How does LangChain
connect to OpenAI?", assuming the demo cards and relationship are already
seeded.

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend
    participant AG as Agent
    participant MCP as MCP Server
    participant RAG as Graph RAG
    participant NEO as Neo4j
    participant LLM as OpenAI/Groq

    User->>FE: Ask "How does LangChain connect to OpenAI?"
    FE->>AG: POST /chat (X-Request-Id generated here)
    AG->>MCP: GET /tools (discover)
    MCP-->>AG: tool list
    AG->>MCP: POST /tools/graph_search/call {query}
    MCP->>RAG: POST /rag/search {query}
    RAG->>NEO: keyword match + one-hop expand (Cypher)
    NEO-->>RAG: LangChain, OpenAI, USES relationship
    RAG-->>MCP: matchedCards, relationships, contextText
    MCP-->>AG: tool result + downstream trace
    AG->>LLM: chat completion, grounded in contextText only
    LLM-->>AG: answer
    AG-->>FE: answer + provider/model + toolCalls + sources + requestId
    FE-->>User: renders answer, sources, and the trace inspector
```

If `graph_search` returns no context, the agent skips the LLM call
entirely and returns a fixed "not enough context" answer instead of
guessing from the model's own training data.
