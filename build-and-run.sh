#!/bin/bash

# Onyx Build and Run Script
# This script builds and runs the Onyx application using Docker Compose

set -e

echo "🚀 Building and starting Onyx..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f "deployment/docker_compose/.env" ]; then
    echo -e "${YELLOW}📝 Creating .env file with default configuration...${NC}"
    cat > deployment/docker_compose/.env << 'ENVFILE'
# Local Development Environment Configuration
WEB_DOMAIN=http://localhost:3000
AUTH_TYPE=disabled
SESSION_EXPIRE_TIME_SECONDS=604800
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=onyx
DB_READONLY_USER=db_readonly_user
DB_READONLY_PASSWORD=password
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
S3_ENDPOINT_URL=http://minio:9000
S3_AWS_ACCESS_KEY_ID=minioadmin
S3_AWS_SECRET_ACCESS_KEY=minioadmin
S3_FILE_STORE_BUCKET_NAME=onyx-file-store-bucket
MODEL_SERVER_HOST=inference_model_server
INDEXING_MODEL_SERVER_HOST=indexing_model_server
LOG_LEVEL=info
DISABLE_TELEMETRY=false
SHOW_EXTRA_CONNECTORS=true
ENABLE_PAID_ENTERPRISE_EDITION_FEATURES=false
IMAGE_TAG=latest
ENVFILE
fi

# Navigate to the docker compose directory
cd deployment/docker_compose

# Build the images
echo -e "${GREEN}🔨 Building Docker images...${NC}"
docker-compose -f docker-compose.dev.yml build

# Start the services
echo -e "${GREEN}🚀 Starting services...${NC}"
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 10

# Check if services are running
if docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Onyx is now running!${NC}"
    echo ""
    echo "🌐 Access the application at:"
    echo "   Web UI: http://localhost:3000"
    echo "   API: http://localhost:8080"
    echo ""
    echo "📊 Additional services:"
    echo "   PostgreSQL: localhost:5432"
    echo "   Vespa (Search Engine): localhost:8081"
    echo "   Redis: localhost:6379"
    echo "   MinIO (S3): localhost:9004 (Console: localhost:9005)"
    echo ""
    echo "📝 To view logs: docker-compose -f docker-compose.dev.yml logs -f"
    echo "🛑 To stop: docker-compose -f docker-compose.dev.yml down"
else
    echo -e "${RED}❌ Some services failed to start. Check logs with:${NC}"
    echo "docker-compose -f docker-compose.dev.yml logs"
    exit 1
fi
