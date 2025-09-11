# 🦙 Ollama Connection Fix - Complete Solution

## ✅ What We Fixed

1. **Ollama Binding**: Changed from `localhost:11434` to `0.0.0.0:11434` (all interfaces)
2. **Docker Environment**: Added `OLLAMA_API_BASE=http://host.docker.internal:11434` to docker-compose.yml
3. **API Server**: Now has the correct environment variable set

## 📝 Configuration in Onyx UI

### Option 1: Using Ollama Provider (Recommended)

1. Go to **http://localhost:3000**
2. Navigate to **Admin** → **Model Configuration**
3. Click **Add New Provider**
4. Configure as follows:

   - **Provider Type**: `Ollama (Local)`
   - **Provider Name**: `ollama` (lowercase, no spaces)
   
   In the **Custom Configuration** section (if it appears):
   - Click **Add Custom Config**
   - **Key**: `OLLAMA_BASE_URL`
   - **Value**: `http://host.docker.internal:11434`
   
   - **Default Model**: `llama3.2`
   - **Fast Default Model**: `llama3.2:1b`
   
   ⚠️ **IMPORTANT**: Leave "API Key", "API Base URL", and "API Version" fields EMPTY

5. Click **Save**
6. Click **Set as Default**

### Option 2: Using Custom Provider

If Option 1 doesn't work, try this:

1. **Provider Type**: `Custom`
2. **Provider Name**: `ollama_custom`
3. **API Base URL**: `http://host.docker.internal:11434`
4. **Default Model**: `ollama/llama3.2` (note the "ollama/" prefix)
5. **Fast Default Model**: `ollama/llama3.2:1b`
6. Leave API Key empty

## 🧪 Testing the Connection

Once configured, test in the Chat interface:
1. Create a new chat
2. Type: "Hello, are you running on Ollama?"
3. You should get a response from llama3.2

## 🐛 Troubleshooting

### If you still get connection errors:

1. **Verify Ollama is running on all interfaces**:
   ```bash
   lsof -i :11434 | grep LISTEN
   # Should show: *:11434 (LISTEN)
   ```

2. **Test from Docker container**:
   ```bash
   docker exec docker_compose-api_server-1 curl http://host.docker.internal:11434/api/tags
   ```

3. **Check environment variable**:
   ```bash
   docker exec docker_compose-api_server-1 sh -c "echo \$OLLAMA_API_BASE"
   # Should show: http://host.docker.internal:11434
   ```

4. **Try with explicit model prefix**:
   When configuring in UI, use model names like:
   - `ollama/llama3.2` instead of just `llama3.2`
   - `ollama/llama3.2:1b` instead of just `llama3.2:1b`

## 🔑 Key Points

- **host.docker.internal** is required for Docker containers to reach your host machine
- **0.0.0.0** binding is required for Ollama to accept connections from Docker
- The environment variable `OLLAMA_API_BASE` helps LiteLLM find Ollama
- Model names might need the `ollama/` prefix depending on configuration

## 🚀 For Future Starts

Always start Ollama with:
```bash
OLLAMA_HOST=0.0.0.0 ollama serve
```

Or use the provided script:
```bash
./start-ollama-for-docker.sh
```

This ensures Ollama is accessible from Docker containers.
