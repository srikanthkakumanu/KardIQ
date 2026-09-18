# Architecture Diagram

High-level component view. Every arrow is an HTTP call; there is no direct
cross-service database access.

```mermaid
graph LR
    Browser["Browser"]

    subgraph K["KardIQ"]
        FE["Frontend<br/>Next.js :3000"]
        AGENT["Agent<br/>FastAPI + LangChain :8000"]
        MCP["MCP Server<br/>FastAPI :8010"]
        CARD["Card Service<br/>Spring Boot :8080"]
        RAG["Graph RAG<br/>FastAPI :8020"]
        PG[("PostgreSQL")]
        NEO[("Neo4j")]
    end

    OPENAI["OpenAI / Groq API"]

    Browser --> FE
    FE --> AGENT
    AGENT --> MCP
    AGENT --> OPENAI
    MCP --> CARD
    MCP --> RAG
    CARD --> PG
    RAG --> NEO
```

- The browser only ever calls the agent.
- The agent only ever calls the MCP server (plus the LLM provider directly).
- The MCP server is the only caller of card-service and graph-rag.
- PostgreSQL is reachable only from card-service; Neo4j only from graph-rag.
