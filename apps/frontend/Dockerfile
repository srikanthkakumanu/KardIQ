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
RUN useradd --uid 1000 --create-home appuser
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
USER appuser
EXPOSE 3000
ENV PORT=3000
CMD ["node", "server.js"]
