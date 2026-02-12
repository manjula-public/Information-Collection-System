import streamlit as st
import pandas as pd
from utils.database import get_all_documents, delete_document, update_transaction, get_line_items, init_database
from datetime import datetime

st.set_page_config(page_title="Documents", page_icon="📄", layout="wide")

# Initialize database
init_database()

st.title("📄 Documents")

st.markdown("View and manage all processed documents")

# Initialize session state for editing
if 'editing_id' not in st.session_state:
    st.session_state.editing_id = None
if 'show_delete_confirm' not in st.session_state:
    st.session_state.show_delete_confirm = None

# Get all documents
documents = get_all_documents()

if documents:
    # Convert to DataFrame
    df = pd.DataFrame(documents)
    
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
    filtered_docs = documents.copy()
    
    if selected_category != 'All':
        filtered_docs = [d for d in filtered_docs if d.get('category') == selected_category]
    
    if selected_vendor != 'All':
        filtered_docs = [d for d in filtered_docs if d.get('vendor_name') == selected_vendor]
    
    if selected_status != 'All':
        filtered_docs = [d for d in filtered_docs if d.get('status') == selected_status]
    
    st.markdown("---")
    
    # Display documents with edit/delete buttons
    for doc in filtered_docs:
        with st.container():
            col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 1, 1])
            
            with col1:
                st.write(f"**ID:** {doc['id']}")
                st.write(f"**Vendor:** {doc.get('vendor_name', 'N/A')}")
            
            with col2:
                st.write(f"**Invoice #:** {doc.get('invoice_number', 'N/A')}")
                st.write(f"**Date:** {doc.get('transaction_date', 'N/A')}")
            
            with col3:
                amount = doc.get('amount', 0) or 0
                st.write(f"**Amount:** ${amount:,.2f}")
                st.write(f"**Category:** {doc.get('category', 'N/A')}")
            
            with col4:
                conf = doc.get('confidence_score', 0) or 0
                st.write(f"**Confidence:** {conf*100:.1f}%")
                st.write(f"**Uploaded:** {doc.get('uploaded_at', 'N/A')[:10]}")
            
            with col5:
                if st.button("✏️ Edit", key=f"edit_{doc['id']}"):
                    st.session_state.editing_id = doc['id']
                    st.rerun()
            
            with col6:
                if st.button("🗑️", key=f"delete_{doc['id']}"):
                    st.session_state.show_delete_confirm = doc['id']
                    st.rerun()
            
            # Show line items if available
            line_items = get_line_items(doc['id'])
            if line_items:
                with st.expander(f"🛒 View {len(line_items)} Line Items"):
                    items_df = pd.DataFrame(line_items)
                    items_df = items_df[['description', 'quantity', 'unit_price', 'total', 'category']]
                    items_df['unit_price'] = items_df['unit_price'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
                    items_df['total'] = items_df['total'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
                    items_df = items_df.rename(columns={
                        'description': 'Item',
                        'quantity': 'Qty',
                        'unit_price': 'Unit Price',
                        'total': 'Total',
                        'category': 'Category'
                    })
                    st.dataframe(items_df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
    
    # Edit Modal
    if st.session_state.editing_id:
        doc_to_edit = next((d for d in documents if d['id'] == st.session_state.editing_id), None)
        if doc_to_edit:
            with st.form(f"edit_form_{st.session_state.editing_id}"):
                st.subheader(f"✏️ Edit Document #{st.session_state.editing_id}")
                
                vendor = st.text_input("Vendor Name", value=doc_to_edit.get('vendor_name', ''))
                invoice = st.text_input("Invoice Number", value=doc_to_edit.get('invoice_number', ''))
                
                # Parse date with multiple format support
                date_value = datetime.now()
                if doc_to_edit.get('transaction_date'):
                    try:
                        # Try YYYY-MM-DD format first
                        date_value = datetime.strptime(doc_to_edit.get('transaction_date'), '%Y-%m-%d')
                    except ValueError:
                        try:
                            # Try MM/DD/YYYY format
                            date_value = datetime.strptime(doc_to_edit.get('transaction_date'), '%m/%d/%Y')
                        except ValueError:
                            # Default to today if parsing fails
                            date_value = datetime.now()
                
                date = st.date_input("Transaction Date", value=date_value)
                amount = st.number_input("Amount", value=float(doc_to_edit.get('amount', 0) or 0), min_value=0.0, step=0.01)
                category = st.selectbox("Category", categories[1:], index=categories[1:].index(doc_to_edit.get('category')) if doc_to_edit.get('category') in categories else 0)
                
                col1, col2 = st.columns(2)
                with col1:
                    save_clicked = st.form_submit_button("💾 Save Changes", type="primary")
                with col2:
                    cancel_clicked = st.form_submit_button("❌ Cancel")
                
                # Handle form submission outside the columns
                if save_clicked:
                    # Get transaction ID
                    from utils.database import execute_query
                    trans = execute_query(f"SELECT id FROM transactions WHERE document_id = {st.session_state.editing_id}")
                    if trans:
                        update_transaction(trans[0]['id'], {
                            'vendor_name': vendor,
                            'invoice_number': invoice,
                            'transaction_date': date.strftime('%Y-%m-%d'),
                            'amount': amount,
                            'category': category
                        })
                        st.success("✅ Document updated successfully!")
                        st.session_state.editing_id = None
                        st.rerun()
                
                if cancel_clicked:
                    st.session_state.editing_id = None
                    st.rerun()
    
    # Delete Confirmation
    if st.session_state.show_delete_confirm:
        st.warning(f"⚠️ Are you sure you want to delete Document #{st.session_state.show_delete_confirm}? This will also delete all associated line items.")
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("✅ Yes, Delete", type="primary"):
                delete_document(st.session_state.show_delete_confirm)
                st.success("🗑️ Document deleted successfully!")
                st.session_state.show_delete_confirm = None
                st.rerun()
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.show_delete_confirm = None
                st.rerun()
    
    # Export option
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        # Download as CSV
        export_df = pd.DataFrame(filtered_docs)
        if 'amount' in export_df.columns:
            export_df['amount'] = export_df['amount'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
        if 'confidence_score' in export_df.columns:
            export_df['confidence_score'] = export_df['confidence_score'].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "N/A")
        
        csv = export_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="documents.csv",
            mime="text/csv"
        )
    
    with col2:
        st.write(f"Showing {len(filtered_docs)} of {len(documents)} documents")

else:
    st.info("📭 No documents yet. Upload your first document to get started!")
    
    if st.button("📤 Go to Upload Page"):
        st.switch_page("pages/1_📤_Upload.py")
