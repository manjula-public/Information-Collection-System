import streamlit as st
import pandas as pd
from utils.database import get_all_documents

st.set_page_config(page_title="Documents", page_icon="📄", layout="wide")

st.title("📄 Documents")

st.markdown("View and manage all processed documents")

# Get all documents
documents = get_all_documents()

if documents:
    # Convert to DataFrame
    df = pd.DataFrame(documents)
    
    # Format columns
    if 'amount' in df.columns:
        df['amount'] = df['amount'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
    
    if 'confidence_score' in df.columns:
        df['confidence_score'] = df['confidence_score'].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "N/A")
    
    # Rename columns for display
    display_df = df.rename(columns={
        'id': 'ID',
        'uploaded_at': 'Upload Date',
        'vendor_name': 'Vendor',
        'invoice_number': 'Invoice #',
        'transaction_date': 'Date',
        'amount': 'Amount',
        'category': 'Category',
        'confidence_score': 'Confidence',
        'status': 'Status'
    })
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Documents", len(documents))
    
    with col2:
        processed = sum(1 for d in documents if d.get('status') == 'processed')
        st.metric("Processed", processed)
    
    with col3:
        total_amount = sum(float(d.get('amount', 0) or 0) for d in documents)
        st.metric("Total Amount", f"${total_amount:,.2f}")
    
    with col4:
        avg_confidence = sum(float(d.get('confidence_score', 0) or 0) for d in documents) / len(documents) if documents else 0
        st.metric("Avg Confidence", f"{avg_confidence*100:.1f}%")
    
    st.markdown("---")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = ['All'] + sorted(list(set(d.get('category') for d in documents if d.get('category'))))
        selected_category = st.selectbox("Filter by Category", categories)
    
    with col2:
        vendors = ['All'] + sorted(list(set(d.get('vendor_name') for d in documents if d.get('vendor_name'))))
        selected_vendor = st.selectbox("Filter by Vendor", vendors)
    
    with col3:
        statuses = ['All'] + sorted(list(set(d.get('status') for d in documents if d.get('status'))))
        selected_status = st.selectbox("Filter by Status", statuses)
    
    # Apply filters
    filtered_df = display_df.copy()
    
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['Category'] == selected_category]
    
    if selected_vendor != 'All':
        filtered_df = filtered_df[filtered_df['Vendor'] == selected_vendor]
    
    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['Status'] == selected_status]
    
    # Display table
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn("ID", width="small"),
            "Upload Date": st.column_config.DatetimeColumn("Upload Date", format="YYYY-MM-DD HH:mm"),
            "Amount": st.column_config.TextColumn("Amount", width="medium"),
            "Confidence": st.column_config.TextColumn("Confidence", width="small"),
        }
    )
    
    # Export option
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        # Download as CSV
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="documents.csv",
            mime="text/csv"
        )
    
    with col2:
        st.write(f"Showing {len(filtered_df)} of {len(documents)} documents")

else:
    st.info("📭 No documents yet. Upload your first document to get started!")
    
    if st.button("📤 Go to Upload Page"):
        st.switch_page("pages/1_📤_Upload.py")
