# 📚 How Onyx Works - Understanding the System

## What Onyx IS vs What it ISN'T

### ✅ What Onyx IS:
- **Enterprise Document Search System**: Searches your organization's internal documents
- **Knowledge Base Connector**: Connects to 40+ data sources (Google Drive, Slack, Confluence, etc.)
- **RAG System**: Retrieval-Augmented Generation - finds relevant documents then generates answers
- **Private AI Assistant**: Works with your private company data, maintaining security

### ❌ What Onyx ISN'T (by default):
- **NOT a general web search engine** (like Google)
- **NOT a general knowledge AI** (like ChatGPT without documents)
- **NOT a live internet searcher** (unless configured with Bing/Exa APIs)

## The Core Problem

When you ask "What is www.persistent.com?", Onyx:
1. Searches its indexed documents for information about persistent.com
2. Finds nothing (because you haven't indexed any documents about it)
3. Fails to provide an answer

This is **by design** - Onyx is meant to search YOUR data, not the internet.

## Solutions for General Queries

### Option 1: Add Web Connectors (Document-Based)
You can add specific websites as data sources:
1. Go to Admin Panel → Connectors
2. Add "Web" connector
3. Enter URL: https://www.persistent.com
4. Onyx will crawl and index that website
5. Now queries about persistent.com will work

### Option 2: Enable Web Search APIs (Live Search)
Add these to your `.env` file:
```bash
# For live web search
BING_API_KEY=your-bing-key-here  # Get from Azure
EXA_API_KEY=your-exa-key-here    # Get from Exa.ai

# For general AI knowledge
GEN_AI_API_KEY=sk-your-openai-key  # OpenAI API key
```

### Option 3: Index Relevant Documents
Upload documents about topics you need:
- Company wikis
- Product documentation
- Industry reports
- Internal knowledge bases

## Use Case Examples

### ✅ Good Queries for Default Onyx:
- "What's our vacation policy?" (if you've connected HR docs)
- "Show me last quarter's sales report" (if you've connected Drive/SharePoint)
- "What did John say about the project in Slack?" (if Slack is connected)

### ❌ Bad Queries for Default Onyx:
- "What is www.persistent.com?" (no indexed data about it)
- "Who won the 2024 election?" (no indexed news sources)
- "Explain quantum computing" (no general knowledge without LLM API)

## Setting Up for Your Use Case

### For Company Internal Search:
1. Keep default configuration
2. Connect your data sources (Google Drive, Slack, etc.)
3. Let it index your documents
4. Search your company knowledge

### For General Q&A + Company Data:
1. Add OpenAI API key for general knowledge
2. Add Bing/Exa API keys for web search
3. Connect your internal data sources
4. Now handles both general and specific queries

### For Public Website Analysis:
1. Use Web connector to index specific sites
2. Add sites you frequently need info about
3. Set up regular re-indexing for updates

## Configuration Examples

### Minimal Setup (Document Search Only):
```bash
AUTH_TYPE=disabled
# No API keys needed
# Only searches indexed documents
```

### Enhanced Setup (General AI + Web):
```bash
AUTH_TYPE=disabled
GEN_AI_API_KEY=sk-xxx  # OpenAI for general knowledge
BING_API_KEY=xxx        # Live web search
DISABLE_LLM_DOC_RELEVANCE=true  # Allow answers without documents
```

### Production Setup (Company Deployment):
```bash
AUTH_TYPE=google_oauth  # Secure authentication
GEN_AI_API_KEY=sk-xxx   # AI capabilities
# Connect company data sources
# Set access controls per user
```

## Quick Test Commands

Test if document search works:
```bash
curl -X POST http://localhost:8080/query/stream-query-validation \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "collection": "default"}'
```

Test if API is healthy:
```bash
curl http://localhost:8080/health
```

## Troubleshooting

### "No documents found" errors:
- You haven't connected any data sources
- Documents aren't indexed yet (check Admin → Connectors)
- Query doesn't match any indexed content

### Want general knowledge answers:
- Add `GEN_AI_API_KEY` to enable LLM responses
- Set `DISABLE_LLM_DOC_RELEVANCE=true` to allow non-document answers

### Want live web search:
- Add `BING_API_KEY` or `EXA_API_KEY`
- These enable real-time internet searches

## Summary

Onyx is powerful for searching YOUR data, but needs configuration for general queries. Choose your setup based on your needs:
- **Internal only**: Default setup, no API keys
- **Internal + General**: Add OpenAI API key
- **Everything**: Add OpenAI + Bing/Exa keys

The system is working correctly when it says "no documents found" for general queries - it's just not configured for that use case by default!
