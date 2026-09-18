# infra/k8s

Manifests for a local Kubernetes deployment of KardIQ, one replica per
component, matching the same 7 runtime pieces as `docker-compose.yml`.

## Quick start (local cluster)

Requires a local cluster where images built by `docker compose build` are
already visible to the cluster's image store - Docker Desktop's built-in
Kubernetes, `kind` (with `kind load docker-image`), and Minikube (with
`minikube image load` or its Docker daemon) all work; every Deployment
uses `imagePullPolicy: IfNotPresent` for exactly this reason.

```bash
docker compose build                 # build the 5 custom images locally
cp infra/k8s/secret.example.yaml infra/k8s/secret.yaml
# edit infra/k8s/secret.yaml with real values (see its own comments)
scripts/k8s-apply.sh
kubectl -n kardiq port-forward svc/agent 8000:8000 &
kubectl -n kardiq port-forward svc/frontend 3000:3000 &
open http://localhost:3000
```

Port-forwarding both `agent` and `frontend` to their default local ports
matters: `NEXT_PUBLIC_AGENT_URL` is baked into the frontend image at build
time (`http://localhost:8000` by default), so the browser only reaches
the agent if it's forwarded to that same port.

Tear down with `scripts/k8s-delete.sh` (deletes the whole `kardiq`
namespace, including the Postgres/Neo4j PersistentVolumeClaims and their
data).

## Using a real image registry

For a real (non-local) cluster, push the 5 images to a registry and
change each Deployment's `image:` field to the registry reference (and
drop `imagePullPolicy: IfNotPresent` back to the default `Always`, or set
it explicitly).

## Deliberate simplifications

- `kardiq-config` (ConfigMap) and `kardiq-secrets` (Secret) are shared
  across every app Deployment via `envFrom`, rather than one ConfigMap/
  Secret per component. Simpler to maintain for a small reference system;
  it does mean e.g. card-service's pod also receives `OPENAI_API_KEY` in
  its environment even though it never reads it. Scope these tighter
  per-service in a real deployment.
- `NEO4J_AUTH` in the secret must be manually kept in sync with
  `NEO4J_PASSWORD` (both present) - see `secret.example.yaml`'s comment.
