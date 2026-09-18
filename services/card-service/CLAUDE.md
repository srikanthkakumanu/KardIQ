# CLAUDE.md

## Component Ownership

This directory contains the Spring Boot card microservice. It owns the relational card model and PostgreSQL persistence. It is the source of truth for knowledge cards.

## Required Stack

- Spring Boot 4.x.
- Java 26.
- Gradle and Groovy DSL.
- Spring Web.
- Spring Data JPA.
- PostgreSQL JDBC driver.
- Flyway.
- Bean Validation.
- Springdoc OpenAPI.
- SLF4J through Spring Boot logging.
- JUnit 5.
- Mockito where useful.
- Testcontainers for PostgreSQL integration tests when practical.
- MapStruct for DTO/entity mapping.

If Spring Boot 4.x or Java 26 is not available, document the mismatch and use the closest stable version only after making the limitation explicit.

## Architecture

Use a conventional layered microservice architecture:

- `api`: REST controllers, request DTOs, response DTOs, exception handlers.
- `application`: use-case services and transaction boundaries.
- `domain`: JPA entities, domain methods, domain constants.
- `infrastructure`: repositories, persistence-specific helpers, configuration.

Do not expose JPA entities from REST endpoints. Do not put business logic in controllers.

## Java and Spring Rules

- Use constructor injection only.
- Do not use field injection.
- Prefer `final` dependencies.
- Use Java records for immutable DTOs.
- Use MapStruct for DTO/entity mapping.
- Use Bean Validation annotations on request DTOs.
- Use `@Validated` where method-level validation is needed.
- Put transactions on application service methods, not controllers.
- Use `@Transactional(readOnly = true)` for read use cases.
- Keep controllers thin and focused on HTTP concerns.
- Use `ResponseEntity` only when status/header control is needed; otherwise return DTOs directly.
- Use centralized exception handling with `@RestControllerAdvice`.
- Return consistent error responses.
- Use package-private helpers where public visibility is not required.

## Domain Model

Start with a small `Card` aggregate:

- `id`
- `title`
- `body`
- `tags`
- `createdAt`
- `updatedAt`

Rules:

- `title` is required and length-limited.
- `body` is required and length-limited.
- `tags` are optional, normalized, and length-limited.
- timestamps are maintained consistently.

## REST API

Implement versioned REST endpoints under `/api/v1`.

Required endpoints:

- `GET /api/v1/cards`
- `GET /api/v1/cards/{id}`
- `POST /api/v1/cards`
- `PUT /api/v1/cards/{id}`
- `DELETE /api/v1/cards/{id}` if deletion is included in the product flow

Operational endpoints:

- `/actuator/health`
- OpenAPI UI endpoint from Springdoc

REST standards:

- Use correct HTTP methods and status codes.
- Return `201 Created` for successful creation.
- Return `404` for missing cards.
- Return `400` for validation failures.
- Support simple pagination for list endpoints if the implementation grows beyond trivial examples.

## Persistence

- Manage all schema changes with Flyway migrations.
- Disable Hibernate DDL auto-generation for real runtime; use validation only.
- Use PostgreSQL-specific features only when they are worth the tradeoff.
- Keep migrations small and ordered.
- Seed the demo dataset used in documentation and the tutorial: at minimum a `LangChain` card and an `OpenAI` card (via a Flyway seed migration or an idempotent seed script), so the worked example is reproducible on a fresh database.
- Use repository interfaces for persistence access.
- Avoid N+1 queries; use explicit fetching if relationships are added.

## OpenAPI

- Add meaningful summaries and descriptions for public endpoints.
- Ensure DTO validation constraints are visible in the generated docs.
- Keep API examples tiny and accurate.

## Logging

- Use SLF4J logger per class.
- Log create/update/delete events at info level.
- Log validation and not-found cases sparingly.
- Never log database credentials or full request bodies containing user content unless explicitly needed for debugging.
- Include the inbound X-Request-Id (if present) in every log line for that request.

## Testing

Include:

- unit tests for application services
- mapper tests for MapStruct mappings where non-trivial
- controller tests for validation and HTTP status codes
- repository/integration tests against PostgreSQL using Testcontainers when practical
- full Spring context smoke test

Test naming should describe behavior, not implementation details.

## Build and Runtime

- Provide a Dockerfile using a multi-stage build where practical.
- Runtime config must come from environment variables.
- Application should fail clearly when database configuration is invalid.
- Gradle test lifecycle must run reliably from the service directory and from root scripts.

