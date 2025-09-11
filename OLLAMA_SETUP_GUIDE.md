# 🦙 Ollama Integration Guide for Onyx

## ✅ What We've Done

We've successfully added Ollama support to Onyx! Here's what was modified:

### 1. **Backend Changes**
- **`llm_provider_options.py`**: Added Ollama as a well-known LLM provider with 50+ model configurations
- **`utils.py`**: Added token mapping for Ollama models
- **`factory.py`**: Already had basic Ollama support (via LiteLLM)

### 2. **Supported Models**
We've pre-configured support for these popular Ollama models:
- **Llama Family**: llama3.2, llama3.1, llama3, llama2 (various sizes)
- **Mistral/Mixtral**: mistral:7b, mixtral:8x7b, mixtral:8x22b
- **Google Gemma**: gemma2:27b, gemma2:9b, gemma2:2b
- **Qwen**: qwen2.5 series (72b down to 0.5b)
- **Code Models**: codellama, codegemma, starcoder2
- **And many more!**

## 🚀 How to Use Ollama with Onyx

### Step 1: Ensure Ollama is Running
```bash
# Check if Ollama is running
ollama list

# If not running, start it
ollama serve

# Pull recommended models (if not already done)
ollama pull llama3.2
ollama pull llama3.2:1b  # Lightweight fast model
```

### Step 2: Access Onyx Admin Panel
1. Open your browser and go to: http://localhost:3000
2. Navigate to **Admin** → **Model Configuration**

### Step 3: Add Ollama as LLM Provider
1. Click **"Add New Provider"**
2. Fill in the configuration:
   - **Provider Type**: Select `Ollama (Local)`
   - **Provider Name**: Give it a name (e.g., "Local Ollama")
   - **Ollama Base URL**: `http://host.docker.internal:11434` (for Docker) or `http://localhost:11434` (for direct access)
   - **Context Window Size**: `32768` (or adjust as needed)
   - **Default Model**: `llama3.2`
   - **Fast Model**: `llama3.2:1b`

### Step 4: Set as Default Provider
1. After creating the provider, click the **"Set as Default"** button
2. This will make Ollama the primary LLM for all queries

### Step 5: Test the Integration
1. Go to the Chat interface
2. Ask a question like "Hello, are you running on Ollama?"
3. The response should come from your local Ollama model

## 🔧 Configuration Options

### Environment Variables (Optional)
You can also configure Ollama via environment variables in `.env`:

```bash
# Add to deployment/docker_compose/.env
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_NUM_CTX=32768
```

### Model-Specific Settings
Different models have different capabilities:

| Model | Context Window | Best For | Memory Usage |
|-------|---------------|----------|--------------|
| llama3.2:1b | 32k | Fast responses | ~2GB |
| llama3.2 | 128k | General use | ~5GB |
| llama3.1:8b | 128k | Better quality | ~8GB |
| mistral:7b | 32k | Balanced | ~5GB |
| gemma2:9b | 8k | Google's model | ~9GB |
| qwen2.5:7b | 32k | Multilingual | ~7GB |

## 🐛 Troubleshooting

### Issue: "Cannot connect to Ollama"
**Solution**: 
- Ensure Ollama is running: `ollama serve`
- For Docker, use `http://host.docker.internal:11434` instead of `localhost`
- Check firewall settings

### Issue: "Model not found"
**Solution**:
- Pull the model first: `ollama pull <model-name>`
- Verify it's listed: `ollama list`

### Issue: "Slow responses"
**Solution**:
- Use a smaller model (e.g., llama3.2:1b)
- Increase Docker memory allocation
- Reduce context window size

### Issue: "Out of memory"
**Solution**:
- Use quantized models (e.g., models with :1b, :3b suffixes)
- Close other applications
- Increase system swap space

## 📊 Performance Tips

1. **Model Selection**:
   - For fast responses: Use `llama3.2:1b` or `phi3:mini`
   - For quality: Use `llama3.2` or `mistral:7b`
   - For code: Use `codellama:7b` or `codegemma`

2. **Context Window**:
   - Smaller context = faster responses
   - Default 32768 is good for most use cases
   - Reduce to 8192 for faster processing

3. **Resource Management**:
   - Monitor with: `docker stats`
   - Ollama uses GPU if available (much faster)
   - CPU-only works but is slower

## 🎯 Use Cases

### 1. **Private Company Assistant**
- No data leaves your infrastructure
- Complete control over the model
- No API costs

### 2. **Document Q&A**
- Index your documents with Onyx
- Use Ollama for generating answers
- Completely offline capable

### 3. **Code Assistant**
- Use `codellama` or `starcoder2` models
- Great for code review and generation
- Integrated with your codebase

## 🔄 Switching Between Providers

You can easily switch between Ollama and cloud providers:

1. Go to Admin → Model Configuration
2. Click "Set as Default" on your preferred provider
3. All new chats will use the selected provider

## 📈 Monitoring

Check Ollama status:
```bash
# View running models
curl http://localhost:11434/api/ps

# Check model details
ollama show llama3.2

# Monitor resource usage
ollama ps
```

## 🎉 Success!

You now have a fully functional local LLM integration with Onyx! Benefits:
- ✅ No API costs
- ✅ Complete data privacy
- ✅ Works offline
- ✅ Customizable models
- ✅ No rate limits

## 📚 Additional Resources

- [Ollama Documentation](https://ollama.ai/docs)
- [Ollama Model Library](https://ollama.ai/library)
- [LiteLLM Ollama Support](https://docs.litellm.ai/docs/providers/ollama)
- [Onyx Documentation](https://docs.onyx.app/)

## 🆘 Getting Help

If you encounter issues:
1. Check Ollama logs: `journalctl -u ollama` or check terminal where `ollama serve` is running
2. Check Onyx logs: `docker-compose -f docker-compose.dev.yml logs api_server`
3. Verify connectivity: `curl http://localhost:11434/api/generate -d '{"model": "llama3.2", "prompt": "test"}'`

---

**Note**: Ollama models are stored in `~/.ollama/models/` and can take significant disk space. Manage with `ollama rm <model>` to remove unused models.
