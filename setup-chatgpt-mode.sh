#!/bin/bash

echo "🤖 Setting up ChatGPT-like Mode for Onyx"
echo "========================================="
echo ""
echo "This will configure Onyx to:"
echo "✅ Answer general questions (like ChatGPT)"
echo "✅ Search the web in real-time"
echo "✅ Use LLM for all responses"
echo ""

cd deployment/docker_compose

# Backup current .env
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

echo "📝 Adding ChatGPT-mode configuration to .env..."

# Add configuration for ChatGPT-like behavior
cat >> .env << 'EOF'

# ===== CHATGPT MODE CONFIGURATION =====
# Enable general AI responses without documents
DISABLE_LLM_DOC_RELEVANCE=true
DISABLE_GENERATIVE_AI=false

# Allow LLM to choose whether to search
DISABLE_LLM_CHOOSE_SEARCH=false

# Enable query rephrasing for better understanding
DISABLE_LLM_QUERY_REPHRASE=false

# Allow answers without document retrieval
QA_TIMEOUT=60
MAX_CHUNKS_FED_TO_CHAT=10

# Enable web search capabilities
ENABLE_WEB_SEARCH=true

# For Bing Search (get free key from Azure Cognitive Services)
# BING_API_KEY=your-bing-api-key-here

# For Exa Search (advanced semantic search)
# EXA_API_KEY=your-exa-api-key-here

# For Brave Search (privacy-focused)
# BRAVE_API_KEY=your-brave-api-key-here

# For SerpAPI (Google search results)
# SERPAPI_API_KEY=your-serpapi-key-here
EOF

echo "✅ Configuration added!"
echo ""
echo "🔄 Restarting services with new configuration..."
docker-compose -f docker-compose.dev.yml restart api_server background

echo ""
echo "⏳ Waiting for services to restart..."
sleep 20

echo ""
echo "======================================"
echo "✅ ChatGPT Mode Configuration Complete!"
echo "======================================"
echo ""
echo "📝 NEXT STEPS:"
echo ""
echo "1. GET A WEB SEARCH API KEY (Choose one):"
echo "   "
echo "   Option A: Bing Search (Recommended - Free tier available)"
echo "   ➜ https://azure.microsoft.com/en-us/services/cognitive-services/bing-web-search-api/"
echo "   - Sign up for Azure (free tier)"
echo "   - Create a Bing Search resource"
echo "   - Get your API key"
echo "   "
echo "   Option B: Brave Search (Privacy-focused)"
echo "   ➜ https://brave.com/search/api/"
echo "   - Sign up for free API access"
echo "   - Get your API key"
echo "   "
echo "   Option C: SerpAPI (Google results)"
echo "   ➜ https://serpapi.com/"
echo "   - Sign up for free tier (100 searches/month)"
echo "   - Get your API key"
echo ""
echo "2. ADD YOUR API KEY:"
echo "   Edit deployment/docker_compose/.env"
echo "   Uncomment and add your key:"
echo "   BING_API_KEY=your-actual-key-here"
echo ""
echo "3. RESTART SERVICES:"
echo "   docker-compose -f docker-compose.dev.yml restart api_server"
echo ""
echo "4. CONFIGURE IN UI:"
echo "   - Go to http://localhost:3000"
echo "   - Create a new 'Assistant' or 'Persona'"
echo "   - Enable 'Web Search' tool"
echo "   - Set prompt to allow general questions"
echo ""
echo "======================================"
