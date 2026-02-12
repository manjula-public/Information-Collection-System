import sqlite3
import os
from datetime import datetime

DB_PATH = "data/database.db"

def init_database():
    """Initialize SQLite database with schema"""
    os.makedirs("data", exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL DEFAULT 'upload',
            document_type TEXT,
            status TEXT DEFAULT 'processed',
            confidence_score REAL,
            file_path TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP,
            metadata TEXT
        )
    """)
    
    # Transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER REFERENCES documents(id),
            vendor_name TEXT,
            invoice_number TEXT,
            transaction_date DATE,
            amount REAL,
            currency TEXT DEFAULT 'USD',
            tax_amount REAL,
            category TEXT,
            department TEXT,
            status TEXT DEFAULT 'processed',
            notes TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Categories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            parent_id INTEGER REFERENCES categories(id),
            department TEXT
        )
    """)
    
    # Insert sample categories if empty
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        categories = [
            ('IT & Software', 'IT'),
            ('Cloud Services', 'IT'),
            ('Hardware & Equipment', 'IT'),
            ('Marketing & Advertising', 'Marketing'),
            ('Digital Advertising', 'Marketing'),
            ('Content Creation', 'Marketing'),
            ('Office Supplies', 'Operations'),
            ('Utilities', 'Operations'),
            ('Office Rent', 'Operations'),
            ('Travel & Entertainment', 'Operations'),
            ('Professional Services', 'Finance'),
            ('Legal Fees', 'Finance'),
            ('Accounting Services', 'Finance'),
            ('HR & Recruitment', 'HR'),
            ('Training & Development', 'HR'),
        ]
        cursor.executemany("INSERT OR IGNORE INTO categories (name, department) VALUES (?, ?)", categories)
    
    conn.commit()
    conn.close()

def save_document(data):
    """Save extracted document data to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Insert document
    cursor.execute("""
        INSERT INTO documents (source, document_type, status, confidence_score, processed_at)
        VALUES (?, ?, ?, ?, ?)
    """, ('upload', 'invoice', 'processed', data.get('confidence', 0), datetime.now()))
    
    document_id = cursor.lastrowid
    
    # Auto-categorize
    category = auto_categorize(data.get('vendor_name', ''), data.get('raw_text', ''))
    
    # Insert transaction
    cursor.execute("""
        INSERT INTO transactions (
            document_id, vendor_name, invoice_number, transaction_date,
            amount, tax_amount, category, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        document_id,
        data.get('vendor_name'),
        data.get('invoice_number'),
        data.get('transaction_date'),
        data.get('amount', 0),
        data.get('tax_amount', 0),
        category,
        'processed'
    ))
    
    conn.commit()
    conn.close()
    
    return document_id

def auto_categorize(vendor, text):
    """Auto-categorize based on vendor and text"""
    vendor_lower = (vendor or '').lower()
    text_lower = (text or '').lower()
    
    # IT & Software
    if any(kw in vendor_lower or kw in text_lower for kw in ['aws', 'azure', 'google cloud', 'microsoft', 'adobe', 'software', 'saas']):
        return 'IT & Software'
    
    # Marketing
    if any(kw in vendor_lower or kw in text_lower for kw in ['facebook', 'google ads', 'linkedin', 'marketing', 'advertising']):
        return 'Marketing & Advertising'
    
    # Utilities
    if any(kw in vendor_lower or kw in text_lower for kw in ['electric', 'water', 'internet', 'telecom', 'utility']):
        return 'Utilities'
    
    # Travel
    if any(kw in vendor_lower or kw in text_lower for kw in ['hotel', 'airline', 'uber', 'taxi', 'travel']):
        return 'Travel & Entertainment'
    
    # Office Supplies
    if any(kw in vendor_lower or kw in text_lower for kw in ['office', 'supplies', 'stationery', 'paper']):
        return 'Office Supplies'
    
    return 'Other'

def get_metrics():
    """Get dashboard metrics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total documents
    cursor.execute("SELECT COUNT(*) FROM documents")
    total_documents = cursor.fetchone()[0]
    
    # Total amount
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions")
    total_amount = cursor.fetchone()[0]
    
    # This month documents
    cursor.execute("""
        SELECT COUNT(*) FROM documents 
        WHERE strftime('%Y-%m', uploaded_at) = strftime('%Y-%m', 'now')
    """)
    month_documents = cursor.fetchone()[0]
    
    # Total categories
    cursor.execute("SELECT COUNT(*) FROM categories")
    total_categories = cursor.fetchone()[0]
    
    # Last upload
    cursor.execute("SELECT MAX(uploaded_at) FROM documents")
    last_upload = cursor.fetchone()[0] or 'Never'
    
    # Average amount
    cursor.execute("SELECT AVG(amount) FROM transactions WHERE amount > 0")
    avg_amount = cursor.fetchone()[0] or 0
    
    # Average confidence
    cursor.execute("SELECT AVG(confidence_score) FROM documents WHERE confidence_score > 0")
    avg_confidence = cursor.fetchone()[0] or 0
    
    # Top categories
    cursor.execute("""
        SELECT category, SUM(amount) as total 
        FROM transactions 
        WHERE category IS NOT NULL
        GROUP BY category 
        ORDER BY total DESC 
        LIMIT 5
    """)
    top_categories = cursor.fetchall()
    
    conn.close()
    
    return {
        'total_documents': total_documents,
        'total_amount': total_amount,
        'month_documents': month_documents,
        'total_categories': total_categories,
        'last_upload': last_upload,
        'avg_amount': avg_amount,
        'avg_confidence': avg_confidence,
        'top_categories': top_categories
    }

def get_all_documents():
    """Get all documents with transaction data"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            d.id,
            d.uploaded_at,
            t.vendor_name,
            t.invoice_number,
            t.transaction_date,
            t.amount,
            t.category,
            d.confidence_score,
            d.status
        FROM documents d
        LEFT JOIN transactions t ON d.id = t.document_id
        ORDER BY d.uploaded_at DESC
    """)
    
    documents = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return documents

def execute_query(sql):
    """Execute SQL query and return results"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(sql)
    results = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return results
