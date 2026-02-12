import os
import re
import easyocr
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import streamlit as st

# Try to import Google Cloud Vision
try:
    from google.cloud import vision
    from google.oauth2 import service_account
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False

# Initialize EasyOCR (cached to avoid reloading)
@st.cache_resource
def get_ocr_engine():
    """Get cached EasyOCR engine"""
    return easyocr.Reader(['en'], gpu=False)

# Initialize Google Vision client (cached)
@st.cache_resource
def get_google_vision_client():
    """Get cached Google Vision client"""
    if not GOOGLE_VISION_AVAILABLE:
        return None
    
    try:
        # Try to get credentials from Streamlit secrets
        if "gcp_service_account" in st.secrets:
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"]
            )
            return vision.ImageAnnotatorClient(credentials=credentials)
        
        # Try to use credentials file
        elif "google_vision" in st.secrets and st.secrets["google_vision"].get("credentials_path"):
            creds_path = st.secrets["google_vision"]["credentials_path"]
            if os.path.exists(creds_path):
                return vision.ImageAnnotatorClient.from_service_account_file(creds_path)
        
        # Try default credentials
        return vision.ImageAnnotatorClient()
    
    except Exception as e:
        st.warning(f"Google Vision not available: {str(e)}. Falling back to EasyOCR.")
        return None

def preprocess_image(image_path):
    """Preprocess image to improve OCR accuracy to 95%+"""
    # Read image with OpenCV
    img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply denoising
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    
    # Increase contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast = clahe.apply(denoised)
    
    # Apply adaptive thresholding for better text detection
    thresh = cv2.adaptiveThreshold(
        contrast, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # Remove noise with morphological operations
    kernel = np.ones((1, 1), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    # Save preprocessed image
    preprocessed_path = image_path.replace('.', '_preprocessed.')
    cv2.imwrite(preprocessed_path, cleaned)
    
    return preprocessed_path


def process_with_google_vision(image_path):
    """Process document with Google Cloud Vision API"""
    client = get_google_vision_client()
    
    if not client:
        # Fallback to EasyOCR
        return None
    
    try:
        # Read image file
        with open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        
        # Perform text detection
        response = client.document_text_detection(image=image)
        
        if response.error.message:
            raise Exception(response.error.message)
        
        # Extract text with positions
        text_with_positions = []
        full_text_annotation = response.full_text_annotation
        
        if not full_text_annotation.text:
            return None
        
        # Get individual words with positions and confidence
        for page in full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        word_text = ''.join([symbol.text for symbol in word.symbols])
                        
                        # Get bounding box
                        vertices = word.bounding_box.vertices
                        y_pos = (vertices[0].y + vertices[2].y) / 2
                        
                        # Get confidence
                        confidence = word.confidence if hasattr(word, 'confidence') else 0.95
                        
                        text_with_positions.append({
                            'text': word_text,
                            'y_pos': y_pos,
                            'confidence': confidence
                        })
        
        # Get full text
        full_text = full_text_annotation.text
        
        # Calculate average confidence
        avg_confidence = sum(item['confidence'] for item in text_with_positions) / len(text_with_positions) if text_with_positions else 0
        
        return {
            'text_with_positions': text_with_positions,
            'full_text': full_text,
            'avg_confidence': avg_confidence
        }
    
    except Exception as e:
        st.warning(f"Google Vision error: {str(e)}. Falling back to EasyOCR.")
        return None

def process_document(image_path):
    """Process document with OCR and extract invoice data including line items"""
    try:
        # Check which OCR engine to use
        use_google_vision = False
        if "settings" in st.secrets:
            ocr_engine = st.secrets["settings"].get("ocr_engine", "easyocr")
            use_google_vision = ocr_engine == "google_vision"
        elif "google_vision" in st.secrets:
            use_google_vision = st.secrets["google_vision"].get("enabled", False)
        
        # Try Google Vision first if enabled
        ocr_result = None
        engine_used = "easyocr"
        
        if use_google_vision and GOOGLE_VISION_AVAILABLE:
            ocr_result = process_with_google_vision(image_path)
            if ocr_result:
                engine_used = "google_vision"
        
        # Fallback to EasyOCR if Google Vision not available or failed
        if not ocr_result:
            # Preprocess image for better accuracy
            preprocessed_path = preprocess_image(image_path)
            
            ocr = get_ocr_engine()
            
            # Process both original and preprocessed for best results
            result_original = ocr.readtext(image_path)
            result_preprocessed = ocr.readtext(preprocessed_path)
            
            # Use preprocessed if it has better confidence
            avg_conf_original = sum(r[2] for r in result_original) / len(result_original) if result_original else 0
            avg_conf_preprocessed = sum(r[2] for r in result_preprocessed) / len(result_preprocessed) if result_preprocessed else 0
            
            result = result_preprocessed if avg_conf_preprocessed > avg_conf_original else result_original
            
            if not result:
                return {
                    "status": "error",
                    "message": "No text detected in image"
                }
            
            # Extract all text with positions
            all_text = []
            text_with_positions = []
            total_confidence = 0
            
            for detection in result:
                bbox = detection[0]  # Bounding box coordinates
                text = detection[1]
                confidence = detection[2]
                
                # Calculate y-position (for line item grouping)
                y_pos = (bbox[0][1] + bbox[2][1]) / 2
                
                all_text.append(text)
                text_with_positions.append({
                    'text': text,
                    'y_pos': y_pos,
                    'confidence': confidence
                })
                total_confidence += confidence
            
            full_text = " ".join(all_text)
            avg_confidence = total_confidence / len(result) if result else 0
            
            # Clean up preprocessed image
            try:
                os.unlink(preprocessed_path)
            except:
                pass
        else:
            # Use Google Vision results
            text_with_positions = ocr_result['text_with_positions']
            full_text = ocr_result['full_text']
            avg_confidence = ocr_result['avg_confidence']
        
        # Parse invoice fields
        extracted_data = {
            "vendor_name": extract_vendor(full_text),
            "invoice_number": extract_invoice_number(full_text),
            "transaction_date": extract_date(full_text),
            "amount": extract_amount(full_text),
            "tax_amount": extract_tax(full_text),
            "line_items": extract_line_items(text_with_positions, full_text),
            "confidence": avg_confidence,
            "raw_text": full_text
        }
        
        return {
            "status": "success",
            "engine": engine_used,
            "data": extracted_data,
            "debug_text": text_with_positions  # For debugging
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def extract_line_items(text_with_positions, full_text):
    """Extract line items (purchased items) from receipt - robust to OCR errors"""
    line_items = []
    
    # Sort by y-position to get items in order
    sorted_text = sorted(text_with_positions, key=lambda x: x['y_pos'])
    
    # Strategy: Look for prices (amounts in the rightmost column) and work backwards to find item names
    # Collect ALL words on the same line to get full product names
    
    for i, item in enumerate(sorted_text):
        text = item['text'].strip()
        
        # Check if this looks like a price/amount (flexible format)
        # Matches: 118.80, 380.00, 1200.00, etc.
        price_match = re.match(r'^[\$]?([\d,]+[\.\-]?\d{1,2})$', text)
        if not price_match:
            continue
        
        # Try to parse as float
        price_str = price_match.group(1).replace(',', '').replace('-', '.')
        try:
            price = float(price_str)
        except:
            continue
        
        # Skip if price is too high (likely total) or too low
        if price < 1.0 or price > 10000:
            continue
        
        # Skip common totals/headers
        if any(keyword in text.lower() for keyword in ['total', 'balance', 'card', 'cash']):
            continue
        
        # Skip if this price appears multiple times (likely a total amount)
        # Count how many times this exact price appears
        price_count = sum(1 for t in sorted_text if t['text'].strip().replace(',', '').replace('.', '') == text.replace(',', '').replace('.', ''))
        if price_count > 2:  # If same price appears more than twice, it's likely a total
            continue
        
        # Look backwards for ALL words on the same line to build full item description
        description_words = []
        quantity = 1.0
        item_number = None
        
        # Check previous items on same line (within 50 pixels vertically = same line)
        for j in range(max(0, i-15), i):
            candidate = sorted_text[j]
            y_diff = abs(candidate['y_pos'] - item['y_pos'])
            
            # Must be on same line (within 50 pixels)
            if y_diff > 50:
                continue
            
            candidate_text = candidate['text'].strip()
            
            # Skip empty or very short text
            if len(candidate_text) < 2:
                continue
            
            # Check if this is an item number (like "1", "2", "3", "4")
            if re.match(r'^\d{1,2}$', candidate_text) and int(candidate_text) < 50:
                item_number = candidate_text
                continue
            
            # Check if this is an item code (skip it)
            if re.match(r'^[A-Z]{2}\d+', candidate_text):
                continue
            
            # Check if this looks like a quantity
            qty_match = re.match(r'^\d+\.?\d{0,3}$', candidate_text)
            if qty_match:
                try:
                    qty_val = float(candidate_text)
                    if 0.01 < qty_val < 100:
                        quantity = qty_val
                        continue
                except:
                    pass
            
            # Check if this is a valid word for item description
            if is_valid_description_word(candidate_text):
                description_words.append(candidate_text)
        
        # Build full description from collected words
        if description_words:
            # Reverse to get correct order (we collected backwards)
            description_words.reverse()
            full_description = ' '.join(description_words)
            
            # Additional validation for full description
            # Reject if it contains too many common/filler words
            common_words = ['as', 'at', 'on', 'this', 'the', 'and', 'or', 'to', 'of', 'in', 'a', 'for']
            common_word_count = sum(1 for word in description_words if word.lower() in common_words)
            
            # If more than 40% are common words, it's likely footer text
            if len(description_words) > 0 and (common_word_count / len(description_words)) > 0.4:
                continue
            
            # Reject if description contains footer-specific keywords
            footer_keywords = ['star', 'points', 'earned', 'loyalty', 'hotline', 'please', 'call']
            if any(keyword in full_description.lower() for keyword in footer_keywords):
                continue
            
            # Validate the full description
            if is_valid_line_item(full_description, price):
                # Add item number prefix if found
                if item_number:
                    final_description = f"{item_number}. {full_description}"
                else:
                    final_description = full_description
                
                line_items.append({
                    'description': final_description,
                    'quantity': quantity,
                    'unit_price': price / quantity if quantity > 0 else price,
                    'total': price
                })
    
    # Remove duplicates - keep the one with lowest price (likely correct)
    # This handles cases where OCR misreads prices
    seen_descriptions = {}
    filtered_items = []
    
    for item in line_items:
        # Create a key for deduplication (ignore item number prefix)
        desc_clean = re.sub(r'^\d+\.\s*', '', item['description']).lower().strip()
        
        # If we've seen this description before
        if desc_clean in seen_descriptions:
            # Keep the one with the lower total (more likely to be correct)
            existing_item = seen_descriptions[desc_clean]
            if item['total'] < existing_item['total']:
                # Replace with lower price
                seen_descriptions[desc_clean] = item
        else:
            seen_descriptions[desc_clean] = item
    
    # Convert back to list
    filtered_items = list(seen_descriptions.values())
    
    # Sort by description for consistent ordering
    filtered_items.sort(key=lambda x: x['description'])
    
    return filtered_items[:20]  # Limit to 20 items

def is_valid_description_word(text):
    """Check if a word is valid for item description (less strict than full description)"""
    # Must be at least 2 characters
    if len(text) < 2:
        return False
    
    # Must start with a letter
    if not text[0].isalpha():
        return False
    
    # Should not be an item code
    if re.match(r'^[A-Z]{2}\d+', text):
        return False
    
    # Should not be common excluded words (expanded list for footer text)
    excluded_words = [
        'qty', 'price', 'amount', 'total', 'subtotal', 'tax', 'vat', 'gst',
        'net', 'grand', 'balance', 'card', 'cash', 'paid', 'change',
        'invoice', 'receipt', 'no', 'nd', 'item', 'iteh', 'oty', 'oti',
        # Footer/loyalty program words
        'star', 'points', 'earned', 'loyalty', 'customer', 'name', 'as',
        'bill', 'this', 'on', 'at', 'please', 'call', 'our', 'hotline',
        'for', 'your', 'valued', 'suggestions', 'comments', 'notice',
        'important', 'case', 'return', 'refund', 'difference', 'days',
        'within', 'the', 'and', 'or', 'to', 'of', 'in', 'a'
    ]
    
    if text.lower() in excluded_words:
        return False
    
    # Should have at least 2 letters
    letter_count = sum(1 for c in text if c.isalpha())
    if letter_count < 2:
        return False
    
    return True


def is_valid_description(text):
    """Check if text is a valid item description"""
    # Must be at least 5 characters for a real item name
    if len(text) < 5:
        return False
    
    # Must start with a letter
    if not text[0].isalpha():
        return False
    
    # Should not be mostly uppercase single letters (like item codes)
    # Item codes look like: VG20301, DY40953, DY95311
    if re.match(r'^[A-Z]{2}\d+', text):
        return False
    
    # Should not be mixed case gibberish (like "TDr", "sulosana")
    # Real items are usually all caps or proper case
    # Reject if it has random capitalization pattern
    if len(text) < 10:  # Only check short text
        upper_count = sum(1 for c in text if c.isupper())
        lower_count = sum(1 for c in text if c.islower())
        # If it has both upper and lower but is short, likely OCR error
        if upper_count > 0 and lower_count > 0 and upper_count < 3:
            return False
    
    # Should not be a common header/footer word
    excluded_words = [
        'total', 'subtotal', 'tax', 'vat', 'gst', 'amount', 'paid', 'change',
        'cash', 'card', 'credit', 'debit', 'invoice', 'receipt', 'date',
        'time', 'thank', 'you', 'welcome', 'visit', 'again', 'store', 'no',
        'number', 'qty', 'price', 'item', 'description', 'discount', 'balance',
        'net', 'grand', 'end', 'npi', 'iconic', 'express', 'city', 'food',
        'sulosana', 'amqunt', 'btty', 'notice', 'important', 'case', 'refund',
        'please', 'call', 'hotline', 'valued', 'suggestions', 'comments'
    ]
    
    text_lower = text.lower().strip()
    if text_lower in excluded_words:
        return False
    
    # Check if it starts with excluded words
    for word in ['net', 'total', 'balance', 'card', 'cash', 'time', 'please', 'thank']:
        if text_lower.startswith(word):
            return False
    
    # Should not be just numbers or symbols
    if re.match(r'^[\d\s\-\.\$]+$', text):
        return False
    
    # Should have at least 3 letters (not just one or two letters + numbers)
    letter_count = sum(1 for c in text if c.isalpha())
    if letter_count < 3:
        return False
    
    # Should not be all uppercase with very few characters (likely abbreviation)
    if text.isupper() and len(text) < 5:
        return False
    
    # Should contain at least one space or be all uppercase (real product names)
    # This filters out random short words like "TDr"
    if ' ' not in text and not text.isupper() and len(text) < 10:
        return False
    
    return True

def is_valid_line_item(description, price):
    """Validate if this is a real line item"""
    # Description must be valid
    if not is_valid_description(description):
        return False
    
    # Price must be reasonable (between $0.10 and $10,000 for supermarkets)
    if price < 0.10 or price > 10000:
        return False
    
    # Description should not be too long
    if len(description) > 60:
        return False
    
    # Description should not contain certain keywords
    excluded_keywords = [
        'total', 'subtotal', 'tax', 'amount', 'balance', 'paid',
        'change', 'tender', 'cash', 'card', 'invoice', 'receipt',
        'net total', 'grand total'
    ]
    
    desc_lower = description.lower()
    for keyword in excluded_keywords:
        if keyword in desc_lower:
            return False
    
    return True

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
    
    # Try to get first line with capital letters
    lines = text.split('\n')
    for line in lines[:5]:
        if len(line) > 3 and any(c.isupper() for c in line):
            return line.strip()
    
    return None

def extract_invoice_number(text):
    """Extract invoice number"""
    patterns = [
        r"invoice[\s#:]+([A-Z0-9-]+)",
        r"inv[\s#:]+([A-Z0-9-]+)",
        r"receipt[\s#:]+([A-Z0-9-]+)",
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
        r"(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

def extract_amount(text):
    """Extract total amount - prioritize Net Total and Grand Total"""
    # Check for Net Total or Grand Total first
    # Handle both same-line and next-line formats
    net_total_patterns = [
        r"net\s+total[\s:]*\s*([\d,]+\.?\d*)",  # Same line
        r"net\s+total[\s:]*\s*\n?\s*([\d,]+\.?\d*)",  # Next line
    ]
    
    for pattern in net_total_patterns:
        net_total_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if net_total_match:
            try:
                amount = float(net_total_match.group(1).replace(',', ''))
                if amount > 10:  # Valid total
                    return amount
            except:
                pass
    
    patterns = [
        r"total[\s:]+\$?(\d+[,.]?\d*\.?\d{2})",
        r"amount[\s:]+\$?(\d+[,.]?\d*\.?\d{2})",
        r"grand\s+total[\s:]+\$?(\d+[,.]?\d*\.?\d{2})",
        r"\$(\d+[,.]?\d*\.?\d{2})",
    ]
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            # Skip Star Points Total
            context = text[max(0, match.start()-20):match.start()].lower()
            if any(word in context for word in ['star', 'points', 'loyalty', 'earned']):
                continue
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
        r"gst[\s:]+\$?(\d+[,.]?\d*\.?\d{2})",
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
