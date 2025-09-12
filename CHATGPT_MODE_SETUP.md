# 🤖 ChatGPT Mode for Onyx - Complete Setup Guide

## Overview
This guide will configure Onyx to behave like ChatGPT - answering general questions, doing web searches, and providing helpful responses without requiring document retrieval.

## Current Status

✅ **What's Working:**
- Ollama integration (local LLM)
- Document search capabilities
- Basic chat interface

❌ **What's Missing for ChatGPT Mode:**
- Web search API key (Exa or custom implementation)
- ChatGPT-like persona configuration

## Step 1: Configure for General Questions (No Web Search)

Even without web search, you can make Onyx answer general questions using Ollama:

### 1.1 Update Environment Configuration

Add to `deployment/docker_compose/.env`:

```bash
# Enable general AI responses
DISABLE_LLM_DOC_RELEVANCE=true
DISABLE_GENERATIVE_AI=false
DISABLE_LLM_CHOOSE_SEARCH=false
DISABLE_LLM_QUERY_REPHRASE=false

# Increase timeouts for complex questions
QA_TIMEOUT=60
MAX_CHUNKS_FED_TO_CHAT=5
```

### 1.2 Restart Services

```bash
cd deployment/docker_compose
docker-compose -f docker-compose.dev.yml restart api_server background
```

## Step 2: Create ChatGPT-like Assistant

### Via UI (Recommended):

1. Go to **http://localhost:3000**
2. Navigate to **Admin** → **Assistants**
3. Click **"Create New Assistant"**
4. Configure:
   - **Name**: "ChatGPT Assistant"
   - **Description**: "General purpose AI assistant"
   
   - **System Prompt**:
   ```
   You are a helpful AI assistant. Answer questions directly using your knowledge.
   When you don't know something, say so honestly.
   Be conversational, detailed, and helpful.
   ```
   
   - **Tools**: Enable "Search" (even without documents, it allows fallback to LLM)
   - **Advanced Settings**:
     - Document Relevance Filter: OFF
     - LLM Filter Extraction: OFF
     - Allow Empty Retrievals: ON

5. **Save** and **Set as Default**

## Step 3: Add Web Search (Optional but Recommended)

Currently, Onyx supports **Exa** for web search. Here's how to set it up:

### Option A: Get Exa API Key (Free Tier Available)

1. **Sign up at Exa**: https://exa.ai/
2. **Get your API key** from the dashboard
3. **Add to environment**:
   ```bash
   echo "EXA_API_KEY=your-exa-api-key-here" >> deployment/docker_compose/.env
   ```
4. **Restart services**:
   ```bash
   docker-compose -f docker-compose.dev.yml restart api_server
   ```

### Option B: Use Without Web Search

Without web search, Onyx will:
- Answer based on Ollama's training data
- Search any documents you've indexed
- Provide helpful responses for general questions

## Step 4: Test Your ChatGPT Mode

### Test Questions to Try:

1. **General Knowledge** (works with Ollama alone):
   - "Explain quantum computing in simple terms"
   - "Write a Python function to sort a list"
   - "What are the benefits of meditation?"

2. **Current Events** (requires web search):
   - "What's happening in tech news today?"
   - "Latest developments in AI"
   - "Current weather in San Francisco"

## Advanced Configuration

### Custom Web Search Provider

If you want to add Bing or Google search support, you'll need to modify the codebase:

1. Create a new provider in `backend/onyx/agents/agent_search/dr/sub_agents/web_search/clients/`
2. Implement the `InternetSearchProvider` interface
3. Update `providers.py` to use your provider

Example structure for Bing provider:
```python
# bing_client.py
from onyx.agents.agent_search.dr.sub_agents.web_search.interfaces import (
    InternetSearchProvider,
    InternetSearchResult,
)

class BingClient(InternetSearchProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def search(self, query: str) -> list[InternetSearchResult]:
        # Implement Bing search API call
        pass
```

## Limitations & Workarounds

### Current Limitations:
1. **Web Search**: Only Exa is natively supported
2. **Real-time Data**: Without web search, can't access current information
3. **Rate Limits**: Depends on your Ollama model and system resources

### Workarounds:
1. **For Current Information**: Manually add web connectors to index specific sites
2. **For Better Responses**: Use larger Ollama models (llama3.2:70b if you have resources)
3. **For Specific Domains**: Index relevant documentation as documents

## Quick Start Script

Run this to configure everything automatically:

```bash
#!/bin/bash
# Save as setup-chatgpt.sh

# Add configuration
cat >> deployment/docker_compose/.env << 'EOF'
DISABLE_LLM_DOC_RELEVANCE=true
DISABLE_GENERATIVE_AI=false
DISABLE_LLM_CHOOSE_SEARCH=false
QA_TIMEOUT=60
EOF

# Restart services
cd deployment/docker_compose
docker-compose -f docker-compose.dev.yml restart api_server background

echo "✅ ChatGPT mode configured!"
echo "Add EXA_API_KEY to .env for web search"
echo "Go to http://localhost:3000 to create your assistant"
```

## Summary

To make Onyx work like ChatGPT:

1. ✅ **Enable general AI responses** (environment variables)
2. ✅ **Create ChatGPT-like assistant** (UI configuration)
3. ⚡ **Optional: Add Exa API for web search**
4. 🎯 **Use Ollama for local, private ChatGPT experience**

Without web search, you get:
- General knowledge answers
- Code generation
- Creative writing
- Analysis and reasoning
- All running locally with Ollama!

With Exa web search, you also get:
- Current events
- Real-time information
- Web-based fact checking
- Latest developments in any field
