#!/bin/bash

set -e

echo "Starting Zuno Docker services..."

echo "Creating required directories..."
mkdir -p ./mysql/init

if [ ! -f "./docker_config.local.yaml" ]; then
  echo "Creating local Docker config from template..."
  cp ./docker_config.example.yaml ./docker_config.local.yaml
  echo "Please edit docker_config.local.yaml before running Docker again."
  exit 1
fi

echo "Building and starting services..."
docker-compose up --build -d

echo "Waiting for services to start..."
sleep 10

echo "Checking service status..."
docker-compose ps

echo ""
echo "Zuno started successfully!"
echo ""
echo "Access URLs:"
echo "  Frontend:  http://localhost:8090"
echo "  Backend:   http://localhost:7860"
echo "  API Docs:  http://localhost:7860/docs"
echo ""
echo "Logs:"
echo "  All services: docker-compose logs -f"
echo "  Backend:      docker-compose logs -f backend"
echo "  Frontend:     docker-compose logs -f frontend"
echo ""
echo "Stop services:"
echo "  docker-compose down"
echo ""
