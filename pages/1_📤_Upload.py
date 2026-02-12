import streamlit as st
from utils.ocr_service import process_document
from utils.database import save_document
import tempfile
import os

st.set_page_config(page_title="Upload Document", page_icon="📤", layout="wide")

st.title("📤 Upload Document")

st.markdown("""
Upload invoices, receipts, or bills in **PDF** or **image** format (JPG, PNG).
The system will automatically extract key information using PaddleOCR.
""")

# File uploader
uploaded_file = st.file_uploader(
    "Choose a file",
    type=["pdf", "jpg", "jpeg", "png"],
    help="Supported formats: PDF, JPG, PNG"
)

if uploaded_file:
    # Display preview
    st.subheader("Preview")
    
    if uploaded_file.type.startswith("image"):
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    else:
        st.info(f"📄 File: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
    
    st.markdown("---")
    
    # Process button
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Process Document", type="primary", use_container_width=True):
            with st.spinner("Processing with PaddleOCR... This may take a few seconds."):
                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                    tmp.write(uploaded_file.getbuffer())
                    tmp_path = tmp.name
                
                try:
                    # Process with OCR
                    result = process_document(tmp_path)
                    
                    if result["status"] == "success":
                        st.success("✅ Document processed successfully!")
                        
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
                            st.write(f"🎯 **Confidence:** {confidence*100:.1f}%")
                        
                        # Save to database
                        try:
                            doc_id = save_document(result["data"])
                            st.success(f"💾 Saved to database (Document ID: {doc_id})")
                        except Exception as e:
                            st.warning(f"⚠️ Saved locally but database error: {str(e)}")
                        
                        # Show raw text
                        with st.expander("🔍 View Raw Extracted Text"):
                            st.text(result["data"].get("raw_text", "No text extracted"))
                        
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
