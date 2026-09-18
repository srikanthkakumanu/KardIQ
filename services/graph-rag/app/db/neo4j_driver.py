import logging

from neo4j import Driver, GraphDatabase

from app.config import Settings

logger = logging.getLogger(__name__)


def create_driver(settings: Settings) -> Driver:
    return GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
        connection_timeout=settings.neo4j_connection_timeout_seconds,
    )


def ensure_constraints(driver: Driver) -> None:
    """Creates the Card.id uniqueness constraint. Best-effort at startup: if
    Neo4j is not reachable yet, log a warning rather than crashing the
    service - /health will reflect the real dependency state per-request."""
    try:
        with driver.session() as session:
            session.run(
                "CREATE CONSTRAINT card_id_unique IF NOT EXISTS "
                "FOR (c:Card) REQUIRE c.id IS UNIQUE"
            )
    except Exception:
        logger.warning("Could not verify/create Neo4j constraints at startup; Neo4j may not be reachable yet.")
