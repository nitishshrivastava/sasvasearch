#!/bin/bash

echo "🌐 Configuring Onyx for Web Search & General Queries"
echo ""
echo "This will enable Onyx to handle general web queries, not just document retrieval."
echo ""

# Create enhanced .env file
cat > .env.enhanced << 'ENVFILE'
# Local Development Environment Configuration
WEB_DOMAIN=http://localhost:3000
AUTH_TYPE=disabled
SESSION_EXPIRE_TIME_SECONDS=604800

# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=onyx
DB_READONLY_USER=db_readonly_user
DB_READONLY_PASSWORD=password

# Storage Configuration
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
S3_ENDPOINT_URL=http://minio:9000
S3_AWS_ACCESS_KEY_ID=minioadmin
S3_AWS_SECRET_ACCESS_KEY=minioadmin
S3_FILE_STORE_BUCKET_NAME=onyx-file-store-bucket

# Model Configuration
MODEL_SERVER_HOST=inference_model_server
INDEXING_MODEL_SERVER_HOST=indexing_model_server

# System Configuration
LOG_LEVEL=info
DISABLE_TELEMETRY=false
SHOW_EXTRA_CONNECTORS=true
ENABLE_PAID_ENTERPRISE_EDITION_FEATURES=false
IMAGE_TAG=latest

# ===== ENHANCED FEATURES FOR GENERAL QUERIES =====

# Enable LLM for general knowledge (add your API key)
# Uncomment and add your OpenAI API key to enable general AI responses
# GEN_AI_API_KEY=sk-your-openai-api-key-here

# Web Search Integration (add API keys for live web search)
# Bing Search API - Get from Azure Cognitive Services
# BING_API_KEY=your-bing-api-key-here

# Exa Search API - Advanced semantic search
# EXA_API_KEY=your-exa-api-key-here

# Disable document-only mode to allow general queries
DISABLE_GENERATIVE_AI=false

# Allow LLM to answer without documents
DISABLE_LLM_DOC_RELEVANCE=true

# Enable query rephrasing for better understanding
DISABLE_LLM_QUERY_REPHRASE=false

# Allow LLM to choose whether to search documents
DISABLE_LLM_CHOOSE_SEARCH=false
ENVFILE

echo "✅ Enhanced configuration created!"
echo ""
echo "To enable web search and general queries, you need to:"
echo ""
echo "1. Add API Keys (edit .env.enhanced):"
echo "   - OpenAI API Key: for general AI responses"
echo "   - Bing API Key: for live web search"
echo "   - Exa API Key: for semantic web search"
echo ""
echo "2. Apply the configuration:"
echo "   cp .env.enhanced .env"
echo "   docker-compose -f docker-compose.dev.yml down"
echo "   docker-compose -f docker-compose.dev.yml up -d"
echo ""
echo "Without API keys, Onyx will only search indexed documents."
echo "With API keys, it can answer general questions and search the web."
