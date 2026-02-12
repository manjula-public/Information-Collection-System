import os
import re
from paddleocr import PaddleOCR
from PIL import Image
import streamlit as st

# Initialize PaddleOCR (cached to avoid reloading)
@st.cache_resource
def get_ocr_engine():
    """Get cached PaddleOCR engine"""
    return PaddleOCR(
        use_angle_cls=True,
        lang='en',
        use_gpu=False,
        show_log=False
    )

def process_document(image_path):
    """Process document with PaddleOCR and extract invoice data"""
    try:
        ocr = get_ocr_engine()
        result = ocr.ocr(image_path, cls=True)
        
        if not result or not result[0]:
            return {
                "status": "error",
                "message": "No text detected in image"
            }
        
        # Extract all text
        all_text = []
        total_confidence = 0
        
        for line in result[0]:
            text = line[1][0]
            confidence = line[1][1]
            all_text.append(text)
            total_confidence += confidence
        
        full_text = " ".join(all_text)
        avg_confidence = total_confidence / len(result[0]) if result[0] else 0
        
        # Parse invoice fields
        extracted_data = {
            "vendor_name": extract_vendor(full_text),
            "invoice_number": extract_invoice_number(full_text),
            "transaction_date": extract_date(full_text),
            "amount": extract_amount(full_text),
            "tax_amount": extract_tax(full_text),
            "confidence": avg_confidence,
            "raw_text": full_text
        }
        
        return {
            "status": "success",
            "engine": "paddleocr",
            "data": extracted_data
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

def extract_vendor(text):
    """Extract vendor name using patterns"""
    patterns = [
        r"(?:from|vendor|supplier|company)[\s:]+([A-Z][A-Za-z\s&.,]+?)(?:\n|invoice|bill)",
        r"^([A-Z][A-Za-z\s&.,]{3,30})",  # First capitalized line
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
    return None

def extract_invoice_number(text):
    """Extract invoice number"""
    patterns = [
        r"invoice[\s#:]+([A-Z0-9-]+)",
        r"inv[\s#:]+([A-Z0-9-]+)",
        r"#\s*([A-Z0-9-]{5,})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

def extract_date(text):
    """Extract transaction date"""
    patterns = [
        r"date[\s:]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"(\d{4}-\d{2}-\d{2})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

def extract_amount(text):
    """Extract total amount"""
    patterns = [
        r"total[\s:]+\$?(\d+[,.]?\d*\.?\d{2})",
        r"amount[\s:]+\$?(\d+[,.]?\d*\.?\d{2})",
        r"\$(\d+[,.]?\d*\.?\d{2})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                return float(amount_str)
            except:
                continue
    return None

def extract_tax(text):
    """Extract tax amount"""
    patterns = [
        r"tax[\s:]+\$?(\d+[,.]?\d*\.?\d{2})",
        r"vat[\s:]+\$?(\d+[,.]?\d*\.?\d{2})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            tax_str = match.group(1).replace(',', '')
            try:
                return float(tax_str)
            except:
                continue
    return None
