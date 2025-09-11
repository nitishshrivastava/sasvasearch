#!/bin/bash

# Script to add Ollama support to Onyx
# This will patch the necessary files to enable Ollama as an LLM provider

set -e

echo "🦙 Adding Ollama Support to Onyx"
echo "================================="
echo ""

# Navigate to backend directory
cd backend

# Create a backup of the original files
echo "📦 Creating backups..."
cp onyx/llm/llm_provider_options.py onyx/llm/llm_provider_options.py.backup
cp onyx/llm/utils.py onyx/llm/utils.py.backup

echo "✏️ Patching llm_provider_options.py..."

# Create the patch file for llm_provider_options.py
cat > ollama_provider_patch.py << 'EOF'
import sys
import re

# Read the original file
with open('onyx/llm/llm_provider_options.py', 'r') as f:
    content = f.read()

# Add Ollama provider constants after VERTEXAI definitions
ollama_constants = '''
OLLAMA_PROVIDER_NAME = "ollama"
OLLAMA_DEFAULT_MODEL = "llama3.2"
OLLAMA_DEFAULT_FAST_MODEL = "llama3.2:1b"
OLLAMA_MODEL_NAMES = [
    # Llama models
    "llama3.3:70b",
    "llama3.2:90b",
    "llama3.2:vision",
    "llama3.2",
    "llama3.2:3b",
    "llama3.2:1b",
    "llama3.1:405b",
    "llama3.1:70b",
    "llama3.1:8b",
    "llama3:70b",
    "llama3:8b",
    "llama2:70b",
    "llama2:13b",
    "llama2:7b",
    # Mistral models
    "mistral:7b",
    "mistral-large",
    "mixtral:8x7b",
    "mixtral:8x22b",
    # Google models
    "gemma2:27b",
    "gemma2:9b",
    "gemma2:2b",
    "gemma:7b",
    "gemma:2b",
    # Qwen models
    "qwen2.5:72b",
    "qwen2.5:32b",
    "qwen2.5:14b",
    "qwen2.5:7b",
    "qwen2.5:3b",
    "qwen2.5:1.5b",
    "qwen2.5:0.5b",
    "qwen2:72b",
    "qwen2:7b",
    "qwen2:1.5b",
    "qwen2:0.5b",
    # DeepSeek models
    "deepseek-v2.5",
    "deepseek-v2:16b",
    "deepseek-coder-v2",
    # Phi models
    "phi3:14b",
    "phi3:medium",
    "phi3:mini",
    # Other popular models
    "command-r-plus",
    "command-r",
    "solar:10.7b",
    "yi:34b",
    "yi:9b",
    "yi:6b",
    "vicuna:33b",
    "vicuna:13b",
    "vicuna:7b",
    "orca2:13b",
    "orca2:7b",
    "neural-chat:7b",
    "starling-lm:7b",
    "codellama:70b",
    "codellama:34b",
    "codellama:13b",
    "codellama:7b",
    "codegemma",
    "starcoder2:15b",
    "starcoder2:7b",
    "starcoder2:3b",
]
OLLAMA_VISIBLE_MODEL_NAMES = [
    "llama3.2",
    "llama3.2:1b",
    "mistral:7b",
    "gemma2:9b",
    "qwen2.5:7b",
    "phi3:mini",
]
'''

# Find the position to insert Ollama constants (after VERTEXAI_VISIBLE_MODEL_NAMES)
pattern = r'(VERTEXAI_VISIBLE_MODEL_NAMES = \[.*?\])'
match = re.search(pattern, content, re.DOTALL)
if match:
    insert_pos = match.end()
    content = content[:insert_pos] + '\n\n' + ollama_constants + content[insert_pos:]

# Update _PROVIDER_TO_MODELS_MAP
provider_map_pattern = r'(_PROVIDER_TO_MODELS_MAP = \{[^}]+)'
match = re.search(provider_map_pattern, content, re.DOTALL)
if match:
    map_content = match.group(1)
    # Add Ollama to the map
    new_map = map_content.rstrip() + ',\n    OLLAMA_PROVIDER_NAME: OLLAMA_MODEL_NAMES,'
    content = content.replace(map_content, new_map)

# Update _PROVIDER_TO_VISIBLE_MODELS_MAP
visible_map_pattern = r'(_PROVIDER_TO_VISIBLE_MODELS_MAP = \{[^}]+)'
match = re.search(visible_map_pattern, content, re.DOTALL)
if match:
    map_content = match.group(1)
    # Add Ollama to the map
    new_map = map_content.rstrip() + ',\n    OLLAMA_PROVIDER_NAME: OLLAMA_VISIBLE_MODEL_NAMES,'
    content = content.replace(map_content, new_map)

# Add Ollama to fetch_available_well_known_llms function
llm_list_pattern = r'(def fetch_available_well_known_llms\(\) -> list\[WellKnownLLMProviderDescriptor\]:.*?return \[)(.*?)(\n    \])'
match = re.search(llm_list_pattern, content, re.DOTALL)
if match:
    ollama_descriptor = '''
        WellKnownLLMProviderDescriptor(
            name=OLLAMA_PROVIDER_NAME,
            display_name="Ollama (Local)",
            api_key_required=False,
            api_base_required=False,
            api_version_required=False,
            custom_config_keys=[
                CustomConfigKey(
                    name="OLLAMA_BASE_URL",
                    display_name="Ollama Base URL",
                    description="URL where Ollama is running (e.g., http://localhost:11434)",
                    is_required=False,
                    default_value="http://localhost:11434",
                ),
                CustomConfigKey(
                    name="OLLAMA_NUM_CTX",
                    display_name="Context Window Size",
                    description="Maximum context window size (default: 32768)",
                    is_required=False,
                    default_value="32768",
                ),
            ],
            model_configurations=fetch_model_configurations_for_provider(
                OLLAMA_PROVIDER_NAME
            ),
            default_model=OLLAMA_DEFAULT_MODEL,
            default_fast_model=OLLAMA_DEFAULT_FAST_MODEL,
        ),'''
    
    # Insert before the closing bracket
    new_content = match.group(1) + match.group(2).rstrip() + ',\n' + ollama_descriptor + match.group(3)
    content = content.replace(match.group(0), new_content)

# Write the modified content
with open('onyx/llm/llm_provider_options.py', 'w') as f:
    f.write(content)

print("✅ Successfully patched llm_provider_options.py")
EOF

# Run the patch script
python ollama_provider_patch.py
rm ollama_provider_patch.py

echo ""
echo "✏️ Patching utils.py for better Ollama model support..."

# Update utils.py to add Ollama models to the token map
cat > ollama_utils_patch.py << 'EOF'
import sys
import re

# Read the original file
with open('onyx/llm/utils.py', 'r') as f:
    content = f.read()

# Find the commented Ollama section and uncomment it
pattern = r'#     # NOTE:.*?#     \]:'
replacement = '''    # Ollama models with their context windows
    for model_name in [
        "llama3.2",
        "llama3.2:1b",
        "llama3.2:3b",
        "llama3.1:8b",
        "llama3.1:70b",
        "llama3:8b",
        "llama3:70b",
        "mistral:7b",
        "mixtral:8x7b",
        "gemma2:9b",
        "gemma2:2b",
        "qwen2.5:7b",
        "phi3:mini",
    ]:'''

# Replace the commented section
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Also uncomment the actual mapping lines
content = content.replace(
    '#     starting_map[f"ollama/{model_name}"] = {',
    '    starting_map[f"ollama/{model_name}"] = {'
)
content = content.replace(
    '#         "max_tokens": 128000,',
    '        "max_tokens": 32768,'
)
content = content.replace(
    '#         "max_input_tokens": 128000,',
    '        "max_input_tokens": 32768,'
)
content = content.replace(
    '#         "max_output_tokens": 128000,',
    '        "max_output_tokens": 4096,'
)
content = content.replace(
    '#     }',
    '    }'
)

# Write the modified content
with open('onyx/llm/utils.py', 'w') as f:
    f.write(content)

print("✅ Successfully patched utils.py")
EOF

python ollama_utils_patch.py
rm ollama_utils_patch.py

echo ""
echo "✏️ Updating factory.py for better Ollama support..."

# The factory.py already has basic Ollama support, let's just ensure it's working
cat > verify_ollama_factory.py << 'EOF'
with open('onyx/llm/factory.py', 'r') as f:
    content = f.read()
    
if 'provider == "ollama"' in content:
    print("✅ factory.py already has Ollama support")
else:
    print("⚠️ factory.py may need manual review")
EOF

python verify_ollama_factory.py
rm verify_ollama_factory.py

echo ""
echo "🎉 Ollama support has been added successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Install Ollama on your system: https://ollama.ai"
echo "2. Pull a model: ollama pull llama3.2"
echo "3. Start Ollama: ollama serve"
echo "4. Restart Onyx services:"
echo "   cd ../deployment/docker_compose"
echo "   docker-compose -f docker-compose.dev.yml down"
echo "   docker-compose -f docker-compose.dev.yml up -d --build"
echo "5. Configure Ollama in the Onyx UI:"
echo "   - Go to Admin → Model Configuration"
echo "   - Add new LLM Provider"
echo "   - Select 'Ollama (Local)'"
echo "   - Set as default provider"
echo ""
echo "🦙 Ollama will now be available as an LLM provider in Onyx!"
