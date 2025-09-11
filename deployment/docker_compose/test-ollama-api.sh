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
