import streamlit as st
import pandas as pd
from utils.database import execute_query, init_database
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Reports", page_icon="📊", layout="wide")

# Initialize database
init_database()

st.title("📊 Reports & Analytics")

st.markdown("View spending by category and analyze line items")

# Date range filter
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
with col2:
    end_date = st.date_input("End Date", value=datetime.now())

st.markdown("---")

# Category Summary
st.subheader("📈 Spending by Category")

# Get category totals from line items
category_query = f"""
    SELECT category, SUM(total) as total_amount, COUNT(*) as item_count
    FROM line_items
    WHERE category IS NOT NULL
    GROUP BY category
    ORDER BY total_amount DESC
"""

category_data = execute_query(category_query)

if category_data:
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    total_spending = sum(item['total_amount'] for item in category_data)
    total_items = sum(item['item_count'] for item in category_data)
    
    with col1:
        st.metric("Total Spending", f"${total_spending:,.2f}")
    with col2:
        st.metric("Total Items", total_items)
    with col3:
        st.metric("Categories", len(category_data))
    
    st.markdown("---")
    
    # Create visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart
        df_cat = pd.DataFrame(category_data)
        fig_bar = px.bar(
            df_cat,
            x='category',
            y='total_amount',
            title='Spending by Category',
            labels={'category': 'Category', 'total_amount': 'Amount ($)'},
            color='total_amount',
            color_continuous_scale='Blues'
        )
        fig_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # Pie chart
        fig_pie = px.pie(
            df_cat,
            values='total_amount',
            names='category',
            title='Category Distribution',
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Category breakdown table
    st.subheader("📋 Category Breakdown")
    
    display_df = df_cat.copy()
    display_df['total_amount'] = display_df['total_amount'].apply(lambda x: f"${x:,.2f}")
    display_df = display_df.rename(columns={
        'category': 'Category',
        'total_amount': 'Total Amount',
        'item_count': 'Items'
    })
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Line Items by Document
    st.subheader("🛒 Line Items by Document")
    
    # Get all documents with line items
    docs_query = """
        SELECT DISTINCT d.id, d.uploaded_at, t.vendor_name, t.transaction_date, t.amount
        FROM documents d
        JOIN transactions t ON d.id = t.document_id
        JOIN line_items li ON d.id = li.document_id
        ORDER BY d.uploaded_at DESC
    """
    
    docs_with_items = execute_query(docs_query)
    
    if docs_with_items:
        for doc in docs_with_items:
            with st.expander(f"📄 Document #{doc['id']} - {doc.get('vendor_name', 'Unknown')} - ${doc.get('amount', 0):,.2f}"):
                # Get line items for this document
                items_query = f"""
                    SELECT description, quantity, unit_price, total, category
                    FROM line_items
                    WHERE document_id = {doc['id']}
                    ORDER BY category, description
                """
                
                items = execute_query(items_query)
                
                if items:
                    items_df = pd.DataFrame(items)
                    
                    # Format currency
                    items_df['unit_price'] = items_df['unit_price'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
                    items_df['total'] = items_df['total'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
                    
                    # Rename columns
                    items_df = items_df.rename(columns={
                        'description': 'Item',
                        'quantity': 'Qty',
                        'unit_price': 'Unit Price',
                        'total': 'Total',
                        'category': 'Category'
                    })
                    
                    st.dataframe(items_df, use_container_width=True, hide_index=True)
                    
                    # Category totals for this document
                    st.markdown("**Category Totals:**")
                    cat_totals_query = f"""
                        SELECT category, SUM(total) as cat_total
                        FROM line_items
                        WHERE document_id = {doc['id']}
                        GROUP BY category
                        ORDER BY cat_total DESC
                    """
                    
                    cat_totals = execute_query(cat_totals_query)
                    
                    cols = st.columns(len(cat_totals) if len(cat_totals) <= 4 else 4)
                    for idx, cat in enumerate(cat_totals):
                        with cols[idx % 4]:
                            st.metric(cat['category'], f"${cat['cat_total']:,.2f}")
    
    st.markdown("---")
    
    # Top Items
    st.subheader("🏆 Top Items by Spending")
    
    top_items_query = """
        SELECT description, SUM(total) as total_spent, COUNT(*) as purchase_count, category
        FROM line_items
        GROUP BY description
        ORDER BY total_spent DESC
        LIMIT 10
    """
    
    top_items = execute_query(top_items_query)
    
    if top_items:
        top_df = pd.DataFrame(top_items)
        top_df['total_spent'] = top_df['total_spent'].apply(lambda x: f"${x:.2f}")
        top_df = top_df.rename(columns={
            'description': 'Item',
            'total_spent': 'Total Spent',
            'purchase_count': 'Times Purchased',
            'category': 'Category'
        })
        
        st.dataframe(top_df, use_container_width=True, hide_index=True)

else:
    st.info("📭 No line items data yet. Upload receipts with itemized purchases to see category analytics!")
    
    if st.button("📤 Go to Upload Page"):
        st.switch_page("pages/1_📤_Upload.py")
