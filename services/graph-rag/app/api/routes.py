from fastapi import APIRouter, Depends, Request

from app.api.schemas import (
    CardNodeIn,
    CardUpsertResponse,
    HealthResponse,
    MatchedCard,
    MatchedRelationship,
    RagSearchRequest,
    RagSearchResponse,
    RelationIn,
    RelationUpsertResponse,
)
from app.errors import CardNotFoundError
from app.repository.graph_repository import GraphRepository
from app.services.retrieval_service import RetrievalService
from app.util import now_iso

router = APIRouter()


def get_driver(request: Request):
    return request.app.state.driver


def get_repository(driver=Depends(get_driver)) -> GraphRepository:
    return GraphRepository(driver)


def get_retrieval_service(repository: GraphRepository = Depends(get_repository)) -> RetrievalService:
    return RetrievalService(repository)


@router.get("/health", response_model=HealthResponse)
def health(driver=Depends(get_driver)) -> HealthResponse:
    try:
        driver.verify_connectivity()
        neo4j_status = "UP"
    except Exception:
        neo4j_status = "DOWN"
    return HealthResponse(status=neo4j_status, dependencies={"neo4j": neo4j_status})


@router.post("/graph/cards", response_model=CardUpsertResponse)
def upsert_card(card: CardNodeIn, repository: GraphRepository = Depends(get_repository)) -> CardUpsertResponse:
    repository.upsert_card(card.to_domain())
    return CardUpsertResponse(id=card.id)


@router.post("/graph/relations", response_model=RelationUpsertResponse)
def upsert_relationship(
    relation: RelationIn, repository: GraphRepository = Depends(get_repository)
) -> RelationUpsertResponse:
    if not repository.card_exists(relation.source_id) or not repository.card_exists(relation.target_id):
        raise CardNotFoundError(relation.source_id, relation.target_id)
    repository.upsert_relationship(relation.to_domain(created_at=now_iso()))
    return RelationUpsertResponse(source_id=relation.source_id, target_id=relation.target_id, label=relation.label)


@router.post("/rag/search", response_model=RagSearchResponse)
def rag_search(
    search_request: RagSearchRequest, retrieval_service: RetrievalService = Depends(get_retrieval_service)
) -> RagSearchResponse:
    result = retrieval_service.search(search_request.query, search_request.limit)
    return RagSearchResponse(
        matched_cards=[MatchedCard(**card) for card in result["matched_cards"]],
        relationships=[MatchedRelationship(**relationship) for relationship in result["relationships"]],
        context_text=result["context_text"],
        source_ids=result["source_ids"],
    )
