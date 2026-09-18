#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ -f "$ROOT_DIR/.env" ]; then
  # shellcheck disable=SC1091
  set -a
  source "$ROOT_DIR/.env"
  set +a
fi

require() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing prerequisite: $1" >&2
    exit 1
  fi
}
require curl
require python3

CARD_SERVICE_URL="${CARD_SERVICE_URL:-http://localhost:${CARD_SERVICE_PORT:-8080}}"
GRAPH_RAG_URL="${GRAPH_RAG_URL:-http://localhost:${GRAPH_RAG_PORT:-8020}}"

echo "==> Fetching cards from card-service ($CARD_SERVICE_URL)"
cards_json="$(curl -sf "$CARD_SERVICE_URL/api/v1/cards?size=100")"

find_card() {
  python3 -c "
import json, sys
data = json.loads(sys.argv[2])
match = next((c for c in data['items'] if c['title'] == sys.argv[1]), None)
print(json.dumps(match) if match else '')
" "$1" "$cards_json"
}

langchain_card="$(find_card "LangChain")"
openai_card="$(find_card "OpenAI")"

if [ -z "$langchain_card" ] || [ -z "$openai_card" ]; then
  echo "Could not find both a 'LangChain' and an 'OpenAI' card in card-service." >&2
  echo "Create them first (via the frontend, or POST $CARD_SERVICE_URL/api/v1/cards), then re-run this script." >&2
  exit 1
fi

upsert_card_in_graph() {
  local card_json="$1"
  local id
  id="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["id"])' "$card_json")"
  echo "==> Upserting card $id into graph-rag"
  python3 -c "
import json, sys
card = json.loads(sys.argv[1])
print(json.dumps({
    'id': card['id'],
    'title': card['title'],
    'body': card['body'],
    'tags': card.get('tags', []),
    'updatedAt': card['updatedAt'],
}))
" "$card_json" | curl -sf -X POST "$GRAPH_RAG_URL/graph/cards" -H "Content-Type: application/json" -d @- >/dev/null
}

upsert_card_in_graph "$langchain_card"
upsert_card_in_graph "$openai_card"

langchain_id="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["id"])' "$langchain_card")"
openai_id="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["id"])' "$openai_card")"

echo "==> Creating the LangChain USES OpenAI relationship in graph-rag"
curl -sf -X POST "$GRAPH_RAG_URL/graph/relations" \
  -H "Content-Type: application/json" \
  -d "{\"sourceId\":\"$langchain_id\",\"targetId\":\"$openai_id\",\"label\":\"USES\"}" >/dev/null

echo "==> Verifying via graph-rag search for 'LangChain'"
curl -sf -X POST "$GRAPH_RAG_URL/rag/search" -H "Content-Type: application/json" -d '{"query":"LangChain"}'
echo
echo
echo "Seed data ready. This script is idempotent - safe to re-run any time."
