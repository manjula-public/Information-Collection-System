import streamlit as st
from utils.ocr_service import process_document
from utils.database import save_document, save_line_items, init_database
import tempfile
import os

st.set_page_config(page_title="Upload Document", page_icon="📤", layout="wide")

# Initialize database
init_database()

st.title("📤 Upload Document")

st.markdown("""
Upload invoices, receipts, or bills in **PDF** or **image** format (JPG, PNG).
The system will automatically extract key information using **EasyOCR** with image preprocessing for 95%+ accuracy.
""")

# File uploader
uploaded_file = st.file_uploader(
    "Choose a file",
    type=["pdf", "jpg", "jpeg", "png"],
    help="Supported formats: PDF, JPG, PNG"
)

if uploaded_file:
    # Display preview
    with st.expander("📷 View Uploaded Image", expanded=False):
        if uploaded_file.type.startswith("image"):
            st.image(uploaded_file, caption="Uploaded Image", width=300)
        else:
            st.info(f"📄 File: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
    
    st.markdown("---")
    
    # Process button
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Process Document", type="primary", use_container_width=True):
            with st.spinner("Processing with EasyOCR... This may take a few seconds."):
                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                    tmp.write(uploaded_file.getbuffer())
                    tmp_path = tmp.name
                
                try:
                    # Process with OCR
                    result = process_document(tmp_path)
                    
                    if result["status"] == "success":
                        engine_name = "Google Cloud Vision API" if result["engine"] == "google_vision" else "EasyOCR"
                        st.success(f"✅ Document processed successfully with {engine_name}!")
                        
                        # Display extracted data
                        st.subheader("📋 Extracted Information")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Vendor Information**")
                            vendor = result["data"].get("vendor_name") or "Not detected"
                            st.write(f"🏢 **Vendor:** {vendor}")
                            
                            invoice_num = result["data"].get("invoice_number") or "Not detected"
                            st.write(f"📄 **Invoice #:** {invoice_num}")
                            
                            date = result["data"].get("transaction_date") or "Not detected"
                            st.write(f"📅 **Date:** {date}")
                        
                        with col2:
                            st.markdown("**Financial Information**")
                            amount = result["data"].get("amount")
                            if amount:
                                st.write(f"💰 **Amount:** ${amount:,.2f}")
                            else:
                                st.write(f"💰 **Amount:** Not detected")
                            
                            tax = result["data"].get("tax_amount")
                            if tax:
                                st.write(f"📊 **Tax:** ${tax:,.2f}")
                            else:
                                st.write(f"📊 **Tax:** Not detected")
                            
                            confidence = result["data"].get("confidence", 0)
                            
                            # Color code confidence
                            if confidence >= 0.95:
                                conf_color = "🟢"
                            elif confidence >= 0.80:
                                conf_color = "🟡"
                            else:
                                conf_color = "🔴"
                            
                            st.write(f"🎯 **Confidence:** {conf_color} {confidence*100:.1f}%")
                        
                        # Display line items if available
                        line_items = result["data"].get("line_items", [])
                        if line_items:
                            st.markdown("---")
                            st.subheader(f"🛒 Purchased Items ({len(line_items)} items)")
                            
                            # Create a table
                            import pandas as pd
                            df = pd.DataFrame(line_items)
                            
                            # Format columns
                            if 'unit_price' in df.columns:
                                df['unit_price'] = df['unit_price'].apply(lambda x: f"${x:.2f}")
                            if 'total' in df.columns:
                                df['total'] = df['total'].apply(lambda x: f"${x:.2f}")
                            
                            # Rename columns
                            df = df.rename(columns={
                                'description': 'Item',
                                'quantity': 'Qty',
                                'unit_price': 'Unit Price',
                                'total': 'Total'
                            })
                            
                            st.dataframe(df, use_container_width=True, hide_index=True)
                            
                            # Calculate total from line items
                            total_from_items = sum(item['total'] for item in line_items)
                            st.info(f"📊 **Sum of line items:** ${total_from_items:.2f}")
                        else:
                            st.info("ℹ️ No line items detected. This might be a simple receipt or the items section couldn't be parsed.")
                        
                        # Save to database
                        try:
                            doc_id = save_document(result["data"])
                            
                            # Save line items if available
                            if line_items:
                                # Get transaction_id from the saved document
                                from utils.database import execute_query
                                trans = execute_query(f"SELECT id FROM transactions WHERE document_id = {doc_id}")
                                if trans:
                                    transaction_id = trans[0]['id']
                                    save_line_items(doc_id, transaction_id, line_items)
                                    st.success(f"💾 Saved to database with {len(line_items)} line items (Document ID: {doc_id})")
                                else:
                                    st.success(f"💾 Saved to database (Document ID: {doc_id})")
                            else:
                                st.success(f"💾 Saved to database (Document ID: {doc_id})")
                        except Exception as e:
                            st.warning(f"⚠️ Saved locally but database error: {str(e)}")
                        
                        # Show raw text for debugging
                        with st.expander("🔍 View Raw Extracted Text (for debugging)"):
                            st.text(result["data"].get("raw_text", "No text extracted"))
                            
                            # Show confidence per line
                            st.markdown("**Text with Confidence:**")
                            if result.get("debug_text"):
                                for item in result["debug_text"][:20]:
                                    conf_pct = item['confidence'] * 100
                                    st.text(f"{conf_pct:5.1f}% | {item['text']}")
                        
                        # Tips
                        st.info("""
                        **💡 Tips for better results:**
                        - Use clear, high-resolution images
                        - Ensure text is not blurry or skewed
                        - Avoid shadows and glare
                        - For best results, scan documents at 300 DPI or higher
                        """)
                    
                    else:
                        st.error(f"❌ Processing failed: {result.get('message', 'Unknown error')}")
                        st.info("Try uploading a clearer image or a different file format.")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                
                finally:
                    # Clean up temp file
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass

else:
    st.info("👆 Please upload a document to get started")
    
    # Sample instructions
    with st.expander("📖 How to use"):
        st.markdown("""
        ### Step-by-step guide:
        
        1. **Upload** a document using the file uploader above
        2. **Preview** the uploaded file
        3. **Click** the "Process Document" button
        4. **Review** the extracted information
        5. **Check** the Documents page to see all processed files
        
        ### Supported information:
        - Vendor/Company name
        - Invoice number
        - Transaction date
        - Total amount
        - Tax amount
        - Raw text content
        
        ### Auto-categorization:
        Documents are automatically categorized based on vendor and content:
        - IT & Software
        - Marketing & Advertising
        - Utilities
        - Travel & Entertainment
        - Office Supplies
        - And more...
        """)
