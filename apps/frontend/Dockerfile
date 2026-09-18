# syntax=docker/dockerfile:1
FROM node:22-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# NEXT_PUBLIC_* values are inlined into the client bundle at build time, not
# read at runtime, so the agent URL must be supplied as a build arg.
ARG NEXT_PUBLIC_AGENT_URL
ENV NEXT_PUBLIC_AGENT_URL=${NEXT_PUBLIC_AGENT_URL}
RUN npm run build

FROM node:22-slim AS runtime
WORKDIR /app
# node:22-slim already ships a "node" user at uid 1000; reuse it instead of
# creating a new one (useradd --uid 1000 fails since that uid is taken).
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
USER node
EXPOSE 3000
ENV PORT=3000
# Docker sets HOSTNAME to the container id by default, and Next's standalone
# server binds to $HOSTNAME if set - without this override it binds to the
# container's own IP instead of all interfaces, making it unreachable from
# localhost/127.0.0.1 inside the container (e.g. from a healthcheck).
ENV HOSTNAME=0.0.0.0
CMD ["node", "server.js"]
