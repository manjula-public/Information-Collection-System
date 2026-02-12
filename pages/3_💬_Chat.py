import streamlit as st
from utils.chat_service import process_query

st.set_page_config(page_title="Chat Assistant", page_icon="💬", layout="wide")

st.title("💬 AI Chat Assistant")

st.markdown("""
Ask questions about your expenses in natural language. Powered by **OpenRouter** (Llama 3.3 70B) or **OpenAI GPT-4o-mini**.
""")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show data if available
        if message.get("data") and message["role"] == "assistant":
            with st.expander("📊 View Data"):
                st.json(message["data"])

# Chat input
if prompt := st.chat_input("Ask a question about your expenses..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = process_query(prompt)
                answer = result["answer"]
                
                st.markdown(answer)
                
                # Show data
                if result.get("data"):
                    with st.expander("📊 View Data"):
                        st.json(result["data"])
                
                # Show provider info
                provider = result.get("provider", "unknown")
                if provider == "openrouter":
                    st.caption("🤖 Powered by OpenRouter (Llama 3.3 70B) - Free")
                elif provider == "openai":
                    st.caption("🤖 Powered by OpenAI GPT-4o-mini")
                elif provider == "basic":
                    st.caption("📊 Basic response (no LLM)")
                
                # Save to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "data": result.get("data"),
                    "provider": provider
                })
            
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# Sidebar with suggestions
with st.sidebar:
    st.subheader("💡 Suggested Queries")
    
    suggestions = [
        "What's the total amount spent?",
        "Show me expenses by category",
        "Who are the top 5 vendors?",
        "How many documents this month?",
        "What's the average transaction amount?",
        "Show me recent transactions"
    ]
    
    for suggestion in suggestions:
        if st.button(suggestion, key=f"btn_{suggestion}", use_container_width=True):
            # Add to chat
            st.session_state.messages.append({"role": "user", "content": suggestion})
            st.rerun()
    
    st.markdown("---")
    
    # Clear chat
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    
    st.markdown("""
    ### How it works:
    
    1. **Ask** a question in natural language
    2. **AI analyzes** your query
    3. **Database** is queried for relevant data
    4. **LLM formats** the response naturally
    
    ### Powered by:
    - 🦙 OpenRouter (Llama 3.3 70B) - Free
    - 🤖 OpenAI GPT-4o-mini - Fallback
    - 🗄️ SQLite database
    """)

# Show example if no messages
if not st.session_state.messages:
    st.info("""
    👋 **Welcome to the AI Chat Assistant!**
    
    Try asking questions like:
    - "What's my total spending?"
    - "Show me expenses by category"
    - "Who are my top vendors?"
    - "How many invoices did I process this month?"
    
    Click on the suggestions in the sidebar or type your own question below! 👇
    """)
