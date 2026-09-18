#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="kardiq"

require() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing prerequisite: $1 (install kubectl: https://kubernetes.io/docs/tasks/tools/)" >&2
    exit 1
  fi
}
require kubectl

echo "==> Deleting namespace '$NAMESPACE'"
echo "This deletes every KardIQ resource in the cluster, including the"
echo "PersistentVolumeClaims for Postgres and Neo4j - all data will be lost."
kubectl delete namespace "$NAMESPACE" --ignore-not-found
