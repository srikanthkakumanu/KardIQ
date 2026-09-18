# Kubernetes Deployment Diagram

Everything lives in the `kardiq` namespace, one Pod per component (all
`replicas: 1`), matching `infra/k8s/`.

```mermaid
graph TD
    subgraph NS["Namespace: kardiq"]
        CM["ConfigMap<br/>kardiq-config"]
        SEC["Secret<br/>kardiq-secrets"]

        subgraph FEd["Deployment: frontend"]
            FEp["Pod"]
        end
        subgraph AGd["Deployment: agent"]
            AGp["Pod"]
        end
        subgraph MCPd["Deployment: mcp-server"]
            MCPp["Pod"]
        end
        subgraph CARDd["Deployment: card-service"]
            CARDp["Pod"]
        end
        subgraph RAGd["Deployment: graph-rag"]
            RAGp["Pod"]
        end
        subgraph PGd["Deployment: postgres"]
            PGp["Pod"]
        end
        subgraph NEOd["Deployment: neo4j"]
            NEOp["Pod"]
        end

        PGpvc[("PVC: postgres-pvc")]
        NEOpvc[("PVC: neo4j-pvc")]

        FEsvc["Service: frontend"] --> FEp
        AGsvc["Service: agent"] --> AGp
        MCPsvc["Service: mcp-server"] --> MCPp
        CARDsvc["Service: card-service"] --> CARDp
        RAGsvc["Service: graph-rag"] --> RAGp
        PGsvc["Service: postgres"] --> PGp
        NEOsvc["Service: neo4j"] --> NEOp

        FEp --> AGsvc
        AGp --> MCPsvc
        MCPp --> CARDsvc
        MCPp --> RAGsvc
        CARDp --> PGsvc
        RAGp --> NEOsvc
        PGp --> PGpvc
        NEOp --> NEOpvc

        CM -.-> AGp
        CM -.-> MCPp
        CM -.-> CARDp
        CM -.-> RAGp
        SEC -.-> AGp
        SEC -.-> CARDp
        SEC -.-> RAGp
    end
```

Every Deployment sets `enableServiceLinks: false` - without it, Kubernetes
auto-injects `<SERVICE>_PORT`-style environment variables for every
Service in the namespace, which collided with (and corrupted) Neo4j's own
`NEO4J_`-prefixed config-from-env mechanism during testing. `card-service`,
`graph-rag`, `mcp-server`, and `agent` read `kardiq-config`/`kardiq-secrets`
via `envFrom`; `postgres` and `neo4j` map only the specific keys they need.
`frontend` needs neither at runtime - its agent URL is baked in at image
build time.
