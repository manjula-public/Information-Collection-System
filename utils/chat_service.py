import os
import streamlit as st
from openai import OpenAI
from utils.database import execute_query

def get_openrouter_client():
    """Get OpenRouter client from secrets"""
    api_key = st.secrets.get("openrouter", {}).get("api_key") or os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        return None
    
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

def get_openai_client():
    """Get OpenAI client from secrets (fallback)"""
    api_key = st.secrets.get("openai", {}).get("api_key") or os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        return None
    
    return OpenAI(api_key=api_key)

def process_query(query):
    """Process natural language query about expenses"""
    
    # Determine SQL query based on user question
    sql = generate_sql(query)
    
    # Execute query
    try:
        results = execute_query(sql)
    except Exception as e:
        return {
            "answer": f"Sorry, I couldn't process that query. Error: {str(e)}",
            "data": [],
            "sql": sql,
            "provider": "error"
        }
    
    # Format response with LLM
    try:
        # Try OpenRouter first (free)
        client = get_openrouter_client()
        if client:
            answer = chat_with_llm(client, query, results, "meta-llama/llama-3.3-70b-instruct:free")
            provider = "openrouter"
        else:
            # Fallback to OpenAI
            client = get_openai_client()
            if client:
                answer = chat_with_llm(client, query, results, "gpt-4o-mini")
                provider = "openai"
            else:
                # No LLM available, return basic response
                answer = format_basic_response(query, results)
                provider = "basic"
        
        return {
            "answer": answer,
            "data": results,
            "sql": sql,
            "provider": provider
        }
    
    except Exception as e:
        # Fallback to basic formatting
        return {
            "answer": format_basic_response(query, results),
            "data": results,
            "sql": sql,
            "provider": "basic"
        }

def generate_sql(query):
    """Generate SQL query based on natural language question"""
    query_lower = query.lower()
    
    if "total" in query_lower and "amount" in query_lower:
        return "SELECT SUM(amount) as total FROM transactions"
    
    elif "count" in query_lower or "how many" in query_lower:
        return "SELECT COUNT(*) as count FROM transactions"
    
    elif "category" in query_lower or "categories" in query_lower:
        return "SELECT category, SUM(amount) as total FROM transactions WHERE category IS NOT NULL GROUP BY category ORDER BY total DESC"
    
    elif "vendor" in query_lower:
        return "SELECT vendor_name, SUM(amount) as total FROM transactions WHERE vendor_name IS NOT NULL GROUP BY vendor_name ORDER BY total DESC LIMIT 10"
    
    elif "recent" in query_lower or "latest" in query_lower:
        return "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10"
    
    elif "this month" in query_lower or "monthly" in query_lower:
        return """
            SELECT SUM(amount) as total, COUNT(*) as count 
            FROM transactions 
            WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
        """
    
    else:
        # Default: recent transactions
        return "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10"

def chat_with_llm(client, query, results, model):
    """Use LLM to format response"""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant for expense tracking. Provide concise, clear answers based on the data provided. Format numbers with proper currency symbols and commas."
            },
            {
                "role": "user",
                "content": f"User asked: {query}\n\nDatabase results: {results}\n\nProvide a natural language answer."
            }
        ],
        temperature=0.7,
        max_tokens=300
    )
    
    return response.choices[0].message.content

def format_basic_response(query, results):
    """Format basic response without LLM"""
    if not results:
        return "I couldn't find any data matching your query."
    
    if len(results) == 1 and 'total' in results[0]:
        return f"The total amount is ${results[0]['total']:,.2f}"
    
    elif len(results) == 1 and 'count' in results[0]:
        return f"There are {results[0]['count']} transactions."
    
    elif 'category' in results[0]:
        response = "Here's the breakdown by category:\n"
        for row in results[:5]:
            response += f"- {row['category']}: ${row['total']:,.2f}\n"
        return response
    
    elif 'vendor_name' in results[0]:
        response = "Here are the top vendors:\n"
        for row in results[:5]:
            response += f"- {row['vendor_name']}: ${row['total']:,.2f}\n"
        return response
    
    else:
        return f"I found {len(results)} results. Please check the data table below for details."
