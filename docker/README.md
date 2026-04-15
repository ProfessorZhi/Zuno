# Zuno Docker Guide

This directory contains the Docker-based local deployment setup for Zuno.

## Services

- `backend` - FastAPI backend
- `frontend` - frontend container
- `mysql` - application database
- `redis` - cache
- `minio` - object storage

## Quick Start

1. Copy the example config:

```bash
cp docker_config.example.yaml docker_config.local.yaml
```

2. Edit `docker_config.local.yaml`.

3. Start all services:

```bash
docker compose up --build -d
```

4. Open:

- Frontend: <http://localhost:8090>
- Backend API: <http://localhost:7860>
- API Docs: <http://localhost:7860/docs>

## Helper Scripts

- Windows: `start_win.bat`
- Linux: `start_linux.sh`
