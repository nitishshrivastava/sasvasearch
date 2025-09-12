#!/usr/bin/env python3
"""
Script to create a ChatGPT-like persona in Onyx
This will configure Onyx to behave like ChatGPT with web search
"""

import requests
import json
import sys

# Configuration
API_BASE = "http://localhost:8080"
PERSONA_NAME = "ChatGPT Assistant"

# ChatGPT-like system prompt
SYSTEM_PROMPT = """You are a helpful AI assistant similar to ChatGPT. You can:
1. Answer general knowledge questions
2. Search the web for current information when needed
3. Provide thoughtful, detailed responses
4. Help with various tasks like writing, analysis, coding, etc.

When answering questions:
- If the question is about current events or needs up-to-date information, search the web
- For general knowledge, use your training data
- Be conversational and helpful
- Provide detailed but concise answers

You don't need to always search documents. You can answer directly when appropriate."""

def create_persona():
    """Create a ChatGPT-like persona via API"""
    
    # Check if API is accessible
    try:
        health = requests.get(f"{API_BASE}/health")
        if health.status_code != 200:
            print("❌ API server is not accessible. Make sure Onyx is running.")
            return False
    except:
        print("❌ Cannot connect to API server at http://localhost:8080")
        return False
    
    # Create persona payload
    persona_data = {
        "name": PERSONA_NAME,
        "description": "A ChatGPT-like assistant that can answer questions and search the web",
        "system_prompt": SYSTEM_PROMPT,
        "task_prompt": "",
        "is_public": True,
        "default_persona": False,
        "is_visible": True,
        "display_priority": 1,
        "starter_messages": [
            "What's happening in the world today?",
            "Can you help me understand quantum computing?",
            "Search for the latest AI developments",
            "Write a Python script to analyze data"
        ],
        # Enable tools
        "tools": [
            {"name": "WebSearchTool", "enabled": True},
            {"name": "SearchTool", "enabled": True}
        ],
        # Search settings
        "num_chunks": 10,
        "llm_relevance_filter": False,
        "llm_filter_extraction": False,
        "recency_bias": "base_decay",
        "search_type": "hybrid",
        # Allow answering without documents
        "llm_model_provider_override": "ollama",  # Use Ollama if configured
        "llm_model_version_override": "llama3.2",
        "prompt_override": None,
        # Important settings for ChatGPT-like behavior
        "document_sets": [],  # Don't restrict to specific document sets
        "enable_web_search": True,
        "require_documents": False,  # Don't require documents to answer
    }
    
    # Try to create persona
    try:
        response = requests.post(
            f"{API_BASE}/persona",
            json=persona_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Created '{PERSONA_NAME}' persona successfully!")
            return True
        else:
            print(f"❌ Failed to create persona: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating persona: {e}")
        return False

def configure_search_settings():
    """Configure search settings for ChatGPT-like behavior"""
    
    settings = {
        "disable_llm_doc_relevance": True,  # Allow answers without documents
        "disable_llm_choose_search": False,  # Let LLM choose when to search
        "disable_llm_query_rephrase": False,  # Enable query rephrasing
        "max_chunks_fed_to_chat": 10,
        "hybrid_alpha": 0.5,  # Balance between keyword and semantic search
    }
    
    try:
        response = requests.put(
            f"{API_BASE}/admin/search-settings",
            json=settings,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Search settings configured for ChatGPT mode")
            return True
        else:
            print(f"⚠️ Could not update search settings: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️ Error updating search settings: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Creating ChatGPT-like Persona in Onyx")
    print("=" * 40)
    print()
    
    # Create persona
    if create_persona():
        print()
        print("📝 Next steps:")
        print("1. Go to http://localhost:3000")
        print(f"2. Select '{PERSONA_NAME}' from the assistants list")
        print("3. Start chatting like you would with ChatGPT!")
        print()
        print("💡 For web search to work, you need to add a search API key:")
        print("   - Edit deployment/docker_compose/.env")
        print("   - Add: BING_API_KEY=your-key-here")
        print("   - Restart: docker-compose -f docker-compose.dev.yml restart api_server")
    else:
        print()
        print("💡 Tip: Make sure Onyx is running and accessible at http://localhost:8080")
