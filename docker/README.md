# Zuno Docker Guide

This directory contains the Docker Compose setup for running the full Zuno stack.

## What Starts

- `frontend`: Vue production build served by nginx on `8090`
- `backend`: FastAPI backend on `7860`
- `postgres`: main application database
- `redis`: cache
- `neo4j`: graph database used by GraphRAG features
- `minio`: S3-compatible object storage

## Requirements

- Docker Desktop or Docker Engine with Compose v2
- At least 6 GB free memory for the full stack
- A local config file at `docker/docker_config.local.yaml`

## Quick Start

From the repository root:

```bash
copy docker\docker_config.example.yaml docker\docker_config.local.yaml
docker compose -f docker/docker-compose.yml up --build -d
```

On macOS/Linux:

```bash
cp docker/docker_config.example.yaml docker/docker_config.local.yaml
docker compose -f docker/docker-compose.yml up --build -d
```

Then open:

- Web UI: <http://127.0.0.1:8090>
- Backend health: <http://127.0.0.1:7860/health>
- API docs: <http://127.0.0.1:7860/docs>
- MinIO console: <http://127.0.0.1:9001>
- Neo4j browser: <http://127.0.0.1:7474>

Default infrastructure credentials:

- PostgreSQL: `postgres` / `postgres`, database `agentchat`
- Neo4j: `neo4j` / `neo4j12345`
- MinIO: `minioadmin` / `minioadmin`

## Configure Models and Keys

`docker_config.local.yaml` is intentionally ignored by git. Put real API keys and model endpoints there.

The example config can boot the stack, but chat and agent features need model settings before they can answer normally. Configure at least:

- `multi_models.conversation_model`
- `multi_models.tool_call_model`
- `multi_models.embedding` if you want knowledge-base retrieval
- tool keys such as Tavily, weather, Bocha, or delivery only if you need those tools

The backend reads this file through:

```yaml
AGENTCHAT_CONFIG: /app/agentchat/config.yaml
```

and Compose mounts your local file into that path.

## Production-Like Image Mode

The default Compose file does not mount frontend or backend source code into the containers. It builds images from the repository:

```bash
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml up -d
```

Useful checks:

```bash
docker compose -f docker/docker-compose.yml ps
curl http://127.0.0.1:7860/health
curl http://127.0.0.1:8090
```

## Development Mode

Use the dev override when editing locally and wanting hot reload:

```bash
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up --build -d
```

The dev override mounts:

- `src/backend` to `/app`
- `src/frontend` to `/app`
- `cli_tools` to `/app/cli_tools`
- `scripts` to `/app/scripts`

## Stop and Reset

Stop services but keep data:

```bash
docker compose -f docker/docker-compose.yml down
```

Remove containers and local Docker volumes:

```bash
docker compose -f docker/docker-compose.yml down -v
```

Use `down -v` when old local database records cause startup/runtime surprises, for example stale MCP rows pointing to files that no longer exist.

## Build Mirrors

If Docker Hub, npm, Debian, or PyPI access is slow in your network, pass mirrors:

```bash
docker compose -f docker/docker-compose.yml build \
  --build-arg NPM_REGISTRY=https://registry.npmmirror.com \
  --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
  --build-arg DEBIAN_MIRROR=mirrors.tuna.tsinghua.edu.cn
```

PowerShell example:

```powershell
docker compose -f docker/docker-compose.yml build `
  --build-arg NPM_REGISTRY=https://registry.npmmirror.com `
  --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple `
  --build-arg DEBIAN_MIRROR=mirrors.tuna.tsinghua.edu.cn
```

## Troubleshooting

If `docker compose config` fails, check that you are using Compose v2:

```bash
docker compose version
```

If frontend is up but login/chat fails, check backend health and logs:

```bash
curl http://127.0.0.1:7860/health
docker logs --tail 200 agentchat-backend
```

If the backend cannot answer, verify model settings in `docker_config.local.yaml`.

If old MCP/tool records break startup or chat, remove them in the UI or reset volumes with `down -v`.
