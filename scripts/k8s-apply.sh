#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
K8S_DIR="$ROOT_DIR/infra/k8s"
NAMESPACE="kardiq"

require() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing prerequisite: $1 (install kubectl: https://kubernetes.io/docs/tasks/tools/)" >&2
    exit 1
  fi
}
require kubectl

if [ ! -f "$K8S_DIR/secret.yaml" ]; then
  echo "infra/k8s/secret.yaml not found." >&2
  echo "Copy infra/k8s/secret.example.yaml to infra/k8s/secret.yaml, fill in real values, and re-run." >&2
  exit 1
fi

echo "==> Applying KardIQ manifests to namespace '$NAMESPACE'"
kubectl apply -f "$K8S_DIR/namespace.yaml"
kubectl apply -n "$NAMESPACE" -f "$K8S_DIR/configmap.yaml"
kubectl apply -n "$NAMESPACE" -f "$K8S_DIR/secret.yaml"

echo "==> Deploying PostgreSQL and Neo4j"
kubectl apply -n "$NAMESPACE" \
  -f "$K8S_DIR/postgres-pvc.yaml" \
  -f "$K8S_DIR/postgres-deployment.yaml" \
  -f "$K8S_DIR/postgres-service.yaml" \
  -f "$K8S_DIR/neo4j-pvc.yaml" \
  -f "$K8S_DIR/neo4j-deployment.yaml" \
  -f "$K8S_DIR/neo4j-service.yaml"
kubectl -n "$NAMESPACE" rollout status deployment/postgres --timeout=180s
kubectl -n "$NAMESPACE" rollout status deployment/neo4j --timeout=180s

echo "==> Deploying card-service and graph-rag"
kubectl apply -n "$NAMESPACE" \
  -f "$K8S_DIR/card-service-deployment.yaml" \
  -f "$K8S_DIR/card-service-service.yaml" \
  -f "$K8S_DIR/graph-rag-deployment.yaml" \
  -f "$K8S_DIR/graph-rag-service.yaml"
kubectl -n "$NAMESPACE" rollout status deployment/card-service --timeout=180s
kubectl -n "$NAMESPACE" rollout status deployment/graph-rag --timeout=180s

echo "==> Deploying mcp-server"
kubectl apply -n "$NAMESPACE" -f "$K8S_DIR/mcp-server-deployment.yaml" -f "$K8S_DIR/mcp-server-service.yaml"
kubectl -n "$NAMESPACE" rollout status deployment/mcp-server --timeout=180s

echo "==> Deploying agent"
kubectl apply -n "$NAMESPACE" -f "$K8S_DIR/agent-deployment.yaml" -f "$K8S_DIR/agent-service.yaml"
kubectl -n "$NAMESPACE" rollout status deployment/agent --timeout=180s

echo "==> Deploying frontend"
kubectl apply -n "$NAMESPACE" -f "$K8S_DIR/frontend-deployment.yaml" -f "$K8S_DIR/frontend-service.yaml"
kubectl -n "$NAMESPACE" rollout status deployment/frontend --timeout=180s

cat <<EOF

KardIQ deployed to namespace '$NAMESPACE'.

  kubectl -n $NAMESPACE get pods
  kubectl -n $NAMESPACE port-forward svc/frontend 3000:3000

EOF
