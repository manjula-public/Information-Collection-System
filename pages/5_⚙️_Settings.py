import streamlit as st
from utils.database import init_database
import json
import os

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

# Initialize database
init_database()

st.title("⚙️ Settings")

st.markdown("Configure your LLM provider and API keys")

# Initialize session state for settings
if 'llm_provider' not in st.session_state:
    st.session_state.llm_provider = st.secrets.get("llm", {}).get("provider", "OpenAI")
if 'llm_model' not in st.session_state:
    st.session_state.llm_model = st.secrets.get("llm", {}).get("model", "gpt-4o")

# LLM Provider Configuration
LLM_PROVIDERS = {
    "OpenAI": {
        "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        "api_key_required": True,
        "api_key_label": "OpenAI API Key",
        "base_url": None
    },
    "OpenRouter": {
        "models": [
            "google/gemini-flash-1.5",
            "meta-llama/llama-3.2-3b-instruct:free",
            "qwen/qwen-2-7b-instruct:free",
            "microsoft/phi-3-mini-128k-instruct:free"
        ],
        "api_key_required": True,
        "api_key_label": "OpenRouter API Key",
        "base_url": "https://openrouter.ai/api/v1"
    },
    "Google Gemini": {
        "models": ["gemini-pro", "gemini-1.5-pro", "gemini-1.5-flash"],
        "api_key_required": True,
        "api_key_label": "Google AI API Key",
        "base_url": None
    },
    "Local (Ollama)": {
        "models": ["llama3.2", "mistral", "codellama", "phi3"],
        "api_key_required": False,
        "api_key_label": None,
        "base_url": "http://localhost:11434"
    }
}

st.markdown("---")

# LLM Configuration Section
st.subheader("🤖 LLM Configuration")

col1, col2 = st.columns(2)

with col1:
    provider = st.selectbox(
        "Provider",
        options=list(LLM_PROVIDERS.keys()),
        index=list(LLM_PROVIDERS.keys()).index(st.session_state.llm_provider) if st.session_state.llm_provider in LLM_PROVIDERS else 0
    )

with col2:
    models = LLM_PROVIDERS[provider]["models"]
    current_model = st.session_state.llm_model if st.session_state.llm_model in models else models[0]
    model = st.selectbox(
        "Model",
        options=models,
        index=models.index(current_model) if current_model in models else 0
    )

# API Key Input
if LLM_PROVIDERS[provider]["api_key_required"]:
    st.markdown("---")
    
    # Get current API key from secrets
    provider_key_map = {
        "OpenAI": "openai",
        "OpenRouter": "openrouter",
        "Google Gemini": "google_gemini"
    }
    
    secret_key = provider_key_map.get(provider, "openai")
    current_api_key = st.secrets.get(secret_key, {}).get("api_key", "")
    
    api_key = st.text_input(
        LLM_PROVIDERS[provider]["api_key_label"],
        value=current_api_key,
        type="password",
        help="Your API key will be saved securely in secrets.toml"
    )
    
    # Show masked version if key exists
    if current_api_key and not api_key:
        st.info(f"✅ API key configured: {current_api_key[:8]}...{current_api_key[-4:]}")

# Ollama Base URL
if provider == "Local (Ollama)":
    st.markdown("---")
    base_url = st.text_input(
        "Ollama Base URL",
        value=st.secrets.get("ollama", {}).get("base_url", "http://localhost:11434"),
        help="URL where Ollama is running (default: http://localhost:11434)"
    )

st.markdown("---")

# Save Button
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    if st.button("💾 Save Configuration", type="primary"):
        # Update session state
        st.session_state.llm_provider = provider
        st.session_state.llm_model = model
        
        # Update secrets.toml
        secrets_path = ".streamlit/secrets.toml"
        
        try:
            # Read existing secrets
            if os.path.exists(secrets_path):
                with open(secrets_path, 'r') as f:
                    content = f.read()
            else:
                content = ""
            
            # Update LLM section
            llm_config = f'\n[llm]\nprovider = "{provider}"\nmodel = "{model}"\n'
            
            # Update provider-specific API key
            if LLM_PROVIDERS[provider]["api_key_required"] and api_key:
                provider_config = f'\n[{secret_key}]\napi_key = "{api_key}"\n'
                
                # Simple replacement (for demo - in production use proper TOML parser)
                if f'[{secret_key}]' in content:
                    # Replace existing section
                    import re
                    content = re.sub(
                        rf'\[{secret_key}\].*?(?=\n\[|\Z)',
                        provider_config.strip() + '\n',
                        content,
                        flags=re.DOTALL
                    )
                else:
                    content += provider_config
            
            # Update Ollama base URL
            if provider == "Local (Ollama)":
                ollama_config = f'\n[ollama]\nbase_url = "{base_url}"\n'
                if '[ollama]' in content:
                    import re
                    content = re.sub(
                        r'\[ollama\].*?(?=\n\[|\Z)',
                        ollama_config.strip() + '\n',
                        content,
                        flags=re.DOTALL
                    )
                else:
                    content += ollama_config
            
            # Update LLM section
            if '[llm]' in content:
                import re
                content = re.sub(
                    r'\[llm\].*?(?=\n\[|\Z)',
                    llm_config.strip() + '\n',
                    content,
                    flags=re.DOTALL
                )
            else:
                content += llm_config
            
            # Write back
            with open(secrets_path, 'w') as f:
                f.write(content)
            
            st.success("✅ Configuration saved successfully!")
            st.info("🔄 Please refresh the page for changes to take effect.")
            
        except Exception as e:
            st.error(f"❌ Error saving configuration: {str(e)}")

with col2:
    if st.button("🧪 Test Connection"):
        with st.spinner("Testing connection..."):
            try:
                if provider == "OpenAI":
                    from openai import OpenAI
                    test_key = api_key if api_key else current_api_key
                    if not test_key:
                        st.error("❌ Please enter an API key first")
                    else:
                        try:
                            client = OpenAI(api_key=test_key)
                            response = client.chat.completions.create(
                                model=model,
                                messages=[{"role": "user", "content": "Hello"}],
                                max_tokens=5
                            )
                            st.success("✅ Connection successful!")
                        except Exception as e:
                            st.error(f"❌ Connection failed: {str(e)}")
                
                elif provider == "OpenRouter":
                    from openai import OpenAI
                    test_key = api_key if api_key else current_api_key
                    if not test_key:
                        st.error("❌ Please enter an API key first")
                    else:
                        try:
                            client = OpenAI(
                                base_url="https://openrouter.ai/api/v1",
                                api_key=test_key
                            )
                            response = client.chat.completions.create(
                                model=model,
                                messages=[{"role": "user", "content": "Hello"}],
                                max_tokens=5
                            )
                            st.success("✅ Connection successful!")
                        except Exception as e:
                            st.error(f"❌ Connection failed: {str(e)}")
                
                elif provider == "Google Gemini":
                    test_key = api_key if api_key else current_api_key
                    if not test_key:
                        st.error("❌ Please enter an API key first")
                    else:
                        try:
                            import google.generativeai as genai
                            genai.configure(api_key=test_key)
                            model_obj = genai.GenerativeModel(model)
                            response = model_obj.generate_content("Hello")
                            st.success("✅ Connection successful!")
                        except Exception as e:
                            st.error(f"❌ Connection failed: {str(e)}")
                
                elif provider == "Local (Ollama)":
                    try:
                        from openai import OpenAI
                        client = OpenAI(
                            base_url=base_url + "/v1",
                            api_key="ollama"  # Ollama doesn't need real API key
                        )
                        response = client.chat.completions.create(
                            model=model,
                            messages=[{"role": "user", "content": "Hello"}],
                            max_tokens=5
                        )
                        st.success("✅ Connection successful!")
                    except Exception as e:
                        st.error(f"❌ Connection failed: {str(e)}")
                        st.info("💡 Make sure Ollama is running: `ollama serve`")
                    
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")

st.markdown("---")

# Current Configuration
st.subheader("📋 Current Configuration")

col1, col2 = st.columns(2)

with col1:
    st.metric("Provider", st.session_state.llm_provider)
    
with col2:
    st.metric("Model", st.session_state.llm_model)

# Instructions
st.markdown("---")
st.subheader("📖 Instructions")

st.markdown("""
### How to get API keys:

**OpenAI:**
1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Navigate to API Keys section
4. Create new secret key

**OpenRouter:**
1. Go to [openrouter.ai](https://openrouter.ai)
2. Sign up or log in
3. Go to Keys section
4. Create new API key
5. Free models available: Llama, DeepSeek, Gemma

**Google Gemini:**
1. Go to [ai.google.dev](https://ai.google.dev)
2. Get API key from Google AI Studio
3. Free tier available

**Local Ollama:**
1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Run `ollama serve` to start server
3. Pull models: `ollama pull llama3.2`
4. No API key required
""")
