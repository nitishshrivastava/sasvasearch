#!/bin/bash

echo "🐳 Starting Docker Desktop and waiting for it to be ready..."
echo ""

# Start Docker Desktop if not running
open -a Docker 2>/dev/null || true

# Wait for Docker to be ready
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker info >/dev/null 2>&1; then
        echo "✅ Docker is ready!"
        echo ""
        echo "🚀 Starting Onyx build..."
        ./build-and-run.sh
        exit 0
    else
        echo "⏳ Waiting for Docker to start... (attempt $((attempt+1))/$max_attempts)"
        sleep 2
        ((attempt++))
    fi
done

echo "❌ Docker failed to start after $max_attempts attempts"
echo "Please start Docker Desktop manually and then run ./build-and-run.sh"
exit 1
