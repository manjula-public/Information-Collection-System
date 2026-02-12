import streamlit as st
from utils.database import init_database, get_metrics

st.set_page_config(
    page_title="Info Collection POC",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_database()

# Header
st.title("📄 Information Collection System")
st.markdown("### POC Demo - Privacy-Focused Document Processing")

# Demo mode notice
st.info("""
**🌐 Demo Mode**: This is running on Streamlit Cloud for demonstration purposes.
- ✅ PaddleOCR for document processing (runs on cloud VM)
- ✅ OpenRouter free models for AI chat (Llama 3.3 70B)
- ✅ SQLite for data storage
- ⚠️ Data is stored on cloud VM (not recommended for sensitive production data)

**For production**: Use local Docker Compose deployment for 100% privacy and full automation features.
""")

st.markdown("---")

# Metrics
metrics = get_metrics()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Documents Processed", metrics["total_documents"])
with col2:
    st.metric("Total Amount", f"${metrics['total_amount']:,.2f}")
with col3:
    st.metric("This Month", metrics["month_documents"])
with col4:
    st.metric("Categories", metrics["total_categories"])

st.markdown("---")

# Quick stats
if metrics["total_documents"] > 0:
    st.subheader("📊 Quick Stats")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Recent Activity**")
        st.write(f"- Last upload: {metrics.get('last_upload', 'N/A')}")
        st.write(f"- Average amount: ${metrics.get('avg_amount', 0):,.2f}")
        st.write(f"- Processing accuracy: {metrics.get('avg_confidence', 0)*100:.1f}%")
    
    with col2:
        st.markdown("**Top Categories**")
        for cat, amount in metrics.get('top_categories', [])[:5]:
            st.write(f"- {cat}: ${amount:,.2f}")
else:
    st.info("👈 **Get started by uploading a document using the sidebar!**")

st.markdown("---")

# Features
st.subheader("✨ Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📤 Upload Documents**")
    st.write("Upload invoices, receipts, and bills in PDF or image format")

with col2:
    st.markdown("**🔍 Smart Extraction**")
    st.write("Automatically extract vendor, amount, date, and other key information")

with col3:
    st.markdown("**💬 AI Chat**")
    st.write("Ask questions about your expenses in natural language")

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>POC Information Collection System | Privacy-Focused Document Processing</p>
    <p>Powered by PaddleOCR, OpenRouter (Llama 3.3), and Streamlit</p>
</div>
""", unsafe_allow_html=True)
