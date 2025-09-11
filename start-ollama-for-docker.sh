#!/bin/bash

# Script to start Ollama with the correct configuration for Docker access

echo "🦙 Starting Ollama for Docker Access"
echo "===================================="
echo ""

# Kill any existing Ollama process
pkill ollama 2>/dev/null && sleep 2

# Start Ollama listening on all interfaces
echo "Starting Ollama on 0.0.0.0:11434 (accessible from Docker)..."
OLLAMA_HOST=0.0.0.0 ollama serve &

sleep 3

# Verify it's running
if lsof -i :11434 | grep -q LISTEN; then
    echo "✅ Ollama is running and accessible from Docker!"
    echo ""
    echo "Binding info:"
    lsof -i :11434 | grep LISTEN
else
    echo "❌ Failed to start Ollama"
    exit 1
fi

echo ""
echo "📝 Note: Always start Ollama with this script when using with Onyx/Docker"
echo "   The default 'ollama serve' only listens on localhost"
echo "   This script makes it listen on all interfaces (0.0.0.0)"
echo ""
echo "🎯 Now you can use in Onyx:"
echo "   Ollama Base URL: http://host.docker.internal:11434"
