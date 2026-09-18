from dataclasses import dataclass

from app.clients.card_service_client import CardServiceClient
from app.clients.graph_rag_client import GraphRagClient


@dataclass
class Clients:
    card_service: CardServiceClient
    graph_rag: GraphRagClient
