# syntax=docker/dockerfile:1
FROM eclipse-temurin:26-jdk AS build
WORKDIR /workspace
COPY gradlew ./
COPY gradle ./gradle
COPY build.gradle settings.gradle ./
RUN chmod +x gradlew
COPY src ./src
RUN ./gradlew clean bootJar --no-daemon -x test

FROM eclipse-temurin:26-jre AS runtime
# curl is needed for the docker-compose healthcheck; the base JRE image
# doesn't include it.
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
# No --uid pinned: eclipse-temurin's Ubuntu base already has a uid-1000
# user, and useradd would fail on that collision.
RUN useradd --create-home appuser
WORKDIR /app
COPY --from=build /workspace/build/libs/*.jar app.jar
USER appuser
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
