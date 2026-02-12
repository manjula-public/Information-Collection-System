# 🔐 Updated Streamlit Cloud Secrets Configuration

## For: https://information-collection-system-dgh.streamlit.app/

---

## IMPORTANT: Google Cloud Vision Setup

To use Google Cloud Vision OCR on Streamlit Cloud, you need to add your Google Cloud service account credentials to the secrets.

### Step 1: Get Google Cloud Credentials

1. Follow the guide in `GOOGLE_VISION_SETUP.md` to create a service account
2. Download the JSON key file
3. Open the JSON file and copy its entire contents

### Step 2: Configure Streamlit Cloud Secrets

1. Go to https://share.streamlit.io
2. Click your app: **information-collection-system-dgh**
3. Click **"Settings"** (⚙️ icon)
4. Click **"Secrets"**
5. Paste the configuration below
6. Click **"Save"**

---

## Complete Secrets Configuration

```toml
# ============================================
# REQUIRED: OpenAI Configuration
# ============================================
[openai]
api_key = "YOUR_OPENAI_API_KEY_HERE"

# ============================================
# LLM Configuration (Default Provider)
# ============================================
[llm]
provider = "OpenAI"
model = "gpt-4o"

# ============================================
# REQUIRED: Google Cloud Vision (for OCR)
# ============================================
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"

# ============================================
# Settings (Use Google Vision by default)
# ============================================
[settings]
ocr_engine = "google_vision"

# ============================================
# OPTIONAL: OpenRouter (Free Models)
# ============================================
[openrouter]
api_key = "YOUR_OPENROUTER_API_KEY_HERE"

# ============================================
# OPTIONAL: Google Gemini
# ============================================
[google_gemini]
api_key = "YOUR_GOOGLE_GEMINI_API_KEY_HERE"
```

---

## How to Add Google Cloud Credentials

### Option 1: Copy from JSON file (Recommended)

1. Open your downloaded `google-vision-key.json` file
2. Copy the ENTIRE contents
3. In the secrets configuration above, replace the `[gcp_service_account]` section with your actual values

**Example JSON structure:**
```json
{
  "type": "service_account",
  "project_id": "your-project-123456",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "vision-ocr@your-project.iam.gserviceaccount.com",
  ...
}
```

Convert each JSON field to TOML format in the `[gcp_service_account]` section.

### Option 2: Use Streamlit's JSON format

Alternatively, you can paste the entire JSON as a string:

```toml
[gcp_service_account]
# Paste your entire google-vision-key.json contents here as TOML
```

---

## Minimal Configuration (If you don't have Google Vision yet)

If you haven't set up Google Cloud Vision yet, use this minimal config with pytesseract:

```toml
[openai]
api_key = "sk-your-actual-key-here"

[llm]
provider = "OpenAI"
model = "gpt-4o"

[settings]
ocr_engine = "tesseract"
```

**Note:** Tesseract OCR is less accurate than Google Vision but doesn't require additional setup.

---

## Setting Up Google Cloud Vision (Free Tier)

### Quick Setup Steps:

1. **Create Google Cloud Account**
   - Go to https://console.cloud.google.com
   - Sign up (free $300 credit for new users)

2. **Create Project**
   - Click "Select a project" → "New Project"
   - Name it (e.g., "bill-ocr")

3. **Enable Vision API**
   - Go to "APIs & Services" → "Library"
   - Search "Cloud Vision API"
   - Click "Enable"

4. **Create Service Account**
   - Go to "IAM & Admin" → "Service Accounts"
   - Click "Create Service Account"
   - Name: "vision-ocr"
   - Role: "Cloud Vision API User"

5. **Download Key**
   - Click on the service account
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key"
   - Choose JSON
   - Download the file

6. **Add to Streamlit Secrets**
   - Copy the JSON contents
   - Paste into `[gcp_service_account]` section above

**Free Tier:** 1,000 OCR requests per month (plenty for testing!)

---

## After Saving Secrets

### Reboot the App

1. Go to app dashboard
2. Click **"⋮"** menu
3. Click **"Reboot app"**
4. Wait ~30 seconds

### Test OCR

1. Go to https://information-collection-system-dgh.streamlit.app/
2. Navigate to **Upload** page
3. Upload a test receipt
4. Should see "OCR Engine: google_vision" in the results
5. Check extracted data quality

---

## Troubleshooting

### "No OCR engine available" error

**Solution:**
- Make sure `[gcp_service_account]` is configured in secrets
- Verify Google Cloud Vision API is enabled
- Check service account has correct permissions

### "Invalid credentials" error

**Solution:**
- Verify JSON format is correct in secrets
- Check private key has proper line breaks (`\n`)
- Ensure no extra spaces in the configuration

### OCR still not working

**Solution:**
- Fall back to tesseract temporarily:
  ```toml
  [settings]
  ocr_engine = "tesseract"
  ```
- Check deployment logs for errors
- Verify image format (JPG/PNG only)

---

## Cost Monitoring

**Google Cloud Vision Pricing:**
- First 1,000 requests/month: **FREE**
- 1,001 - 5,000,000: $1.50 per 1,000 images
- Set budget alerts in Google Cloud Console

**OpenAI Pricing:**
- gpt-4o: ~$2.50 per 1M input tokens
- Monitor at https://platform.openai.com/usage

---

## Security Notes

⚠️ **IMPORTANT:**
- Never commit service account JSON to Git
- Keep API keys private
- Rotate keys regularly
- Monitor usage for unexpected spikes
- Set spending limits in cloud consoles

---

**Your app will have accurate OCR with Google Cloud Vision! 🎯**

Complete the Google Cloud setup and configure the secrets to get started.
