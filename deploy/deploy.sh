#!/bin/bash
set -e

PROJECT_NAME="意图解析"
IMAGE_NAME="idn-frontend"
CONTAINER_NAME="idn-frontend"

echo "=== Building Docker image for ${PROJECT_NAME} ==="

# Build the Docker image
docker build -t ${IMAGE_NAME} -f deploy/Dockerfile .

echo "=== Stopping and removing existing container (if any) ==="
docker stop ${CONTAINER_NAME} 2>/dev/null || true
docker rm ${CONTAINER_NAME} 2>/dev/null || true

echo "=== Running new container ==="
docker run -d \
    --name ${CONTAINER_NAME} \
    -p 8080:80 \
    --restart unless-stopped \
    ${IMAGE_NAME}

echo "=== Deployment complete ==="
echo "Frontend available at: http://localhost:8080"
