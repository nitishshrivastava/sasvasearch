#!/bin/bash

echo "🦙 Fixing Ollama Connection for Onyx"
echo "===================================="
echo ""
echo "The issue: Onyx (running in Docker) can't connect to Ollama on localhost"
echo "The solution: Use 'host.docker.internal:11434' instead of 'localhost:11434'"
echo ""

# Add Ollama configuration to the environment
cd deployment/docker_compose

echo "📝 Adding Ollama configuration to environment..."
cat >> .env << 'EOF'

# Ollama Configuration (for Docker to host connection)
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_NUM_CTX=32768
EOF

echo "✅ Environment updated!"
echo ""

# Test the connection from inside a Docker container
echo "🧪 Testing Ollama connection from Docker container..."
docker run --rm --add-host=host.docker.internal:host-gateway alpine/curl:latest \
  curl -s http://host.docker.internal:11434/api/tags > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Docker can connect to Ollama!"
else
    echo "❌ Docker cannot connect to Ollama. Please check if Ollama is running."
    exit 1
fi

echo ""
echo "🔄 Restarting API server with new configuration..."
docker-compose -f docker-compose.dev.yml restart api_server

echo ""
echo "⏳ Waiting for API server to start..."
sleep 15

echo ""
echo "======================================"
echo "✅ Configuration Complete!"
echo "======================================"
echo ""
echo "📝 IMPORTANT: When configuring Ollama in the Onyx UI:"
echo ""
echo "1. Go to: http://localhost:3000"
echo "2. Navigate to: Admin → Model Configuration"
echo "3. Click: 'Add New Provider'"
echo "4. Configure as follows:"
echo ""
echo "   Provider Type: Ollama (Local)"
echo "   Provider Name: Local Ollama"
echo "   ⚠️  Ollama Base URL: http://host.docker.internal:11434"
echo "        (NOT http://localhost:11434)"
echo "   Context Window Size: 32768"
echo "   Default Model: llama3.2"
echo "   Fast Model: llama3.2:1b"
echo ""
echo "5. Click 'Save' and then 'Set as Default'"
echo ""
echo "🎯 The key is using 'host.docker.internal' instead of 'localhost'!"
echo "   This allows Docker containers to connect to services on your host machine."
echo ""

# Create a helper script for API testing
cat > test-ollama-api.sh << 'SCRIPT'
#!/bin/bash
echo "Testing Ollama through Onyx API..."
curl -X POST http://localhost:8080/chat/send-message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, are you running on Ollama?",
    "chat_session_id": "test-session",
    "parent_message_id": null,
    "prompt_id": 0,
    "search_doc_ids": [],
    "retrieval_options": {
      "run_search": "never"
    },
    "llm_override": {
      "model_provider": "ollama",
      "model_version": "llama3.2",
      "temperature": 0.7
    }
  }'
SCRIPT
chmod +x test-ollama-api.sh

echo "Created test-ollama-api.sh to test the integration directly."
echo ""
echo "If you still get connection errors:"
echo "1. Make sure Ollama is running: ollama serve"
echo "2. Check Docker network: docker network ls"
echo "3. Test from container: docker exec docker_compose-api_server-1 curl http://host.docker.internal:11434/api/tags"
