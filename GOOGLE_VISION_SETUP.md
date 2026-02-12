# Google Cloud Vision API Setup Guide

This guide will help you set up Google Cloud Vision API to get **1,000 free OCR requests per month**.

## Step 1: Create Google Cloud Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Accept terms and conditions
4. **No credit card required** for free tier!

## Step 2: Create a New Project

1. Click on the project dropdown (top left)
2. Click **"New Project"**
3. Enter project name: `information-collection-ocr`
4. Click **"Create"**

## Step 3: Enable Vision API

1. Go to [Vision API Page](https://console.cloud.google.com/apis/library/vision.googleapis.com)
2. Make sure your project is selected
3. Click **"Enable"**
4. Wait for activation (takes ~30 seconds)

## Step 4: Create Service Account & Get Credentials

1. Go to [Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Click **"Create Service Account"**
3. Enter details:
   - **Name**: `ocr-service`
   - **Description**: `OCR service for receipt processing`
4. Click **"Create and Continue"**
5. **Grant Role**: Select `Cloud Vision AI Service Agent`
6. Click **"Continue"** then **"Done"**

## Step 5: Generate JSON Key

1. Click on the service account you just created
2. Go to **"Keys"** tab
3. Click **"Add Key"** → **"Create new key"**
4. Select **"JSON"**
5. Click **"Create"**
6. A JSON file will download automatically
7. **Save this file securely!** (e.g., `google-vision-key.json`)

## Step 6: Configure the Application

### Option A: For Local Development

1. Save the JSON key file to your project folder:
   ```
   d:\AI-TEAM\PROJECTS\POC-info-collect\google-vision-key.json
   ```

2. Add to `.gitignore` (already done):
   ```
   google-vision-key.json
   ```

3. Update `.streamlit/secrets.toml`:
   ```toml
   # Google Cloud Vision API
   GOOGLE_APPLICATION_CREDENTIALS = "google-vision-key.json"
   USE_GOOGLE_VISION = true
   ```

### Option B: For Streamlit Cloud

1. Open the JSON key file
2. Copy the entire contents
3. Go to Streamlit Cloud → Your App → Settings → Secrets
4. Add:
   ```toml
   # Google Cloud Vision API
   [gcp_service_account]
   type = "service_account"
   project_id = "your-project-id"
   private_key_id = "your-private-key-id"
   private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   client_email = "your-service-account@project.iam.gserviceaccount.com"
   client_id = "your-client-id"
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "your-cert-url"
   
   USE_GOOGLE_VISION = true
   ```

## Step 7: Verify Free Tier

1. Go to [Billing](https://console.cloud.google.com/billing)
2. Check **"Free tier usage"**
3. Vision API shows: **1,000 units/month free**

## Free Tier Limits

- ✅ **1,000 images/month** - FREE
- ✅ **Text detection** - FREE (within limit)
- ✅ **Document text detection** - FREE (within limit)
- 💰 After 1,000: $1.50 per 1,000 images

## Usage Tracking

Monitor your usage:
1. Go to [APIs & Services → Dashboard](https://console.cloud.google.com/apis/dashboard)
2. Click on **"Cloud Vision API"**
3. View **"Metrics"** tab
4. See requests per day/month

## Security Best Practices

1. ✅ **Never commit** `google-vision-key.json` to Git
2. ✅ **Restrict API key** to Vision API only
3. ✅ **Set up billing alerts** (optional)
4. ✅ **Rotate keys** every 90 days

## Troubleshooting

### Error: "API not enabled"
- Go to Vision API page and click "Enable"

### Error: "Permission denied"
- Check service account has "Cloud Vision AI Service Agent" role

### Error: "Quota exceeded"
- You've used 1,000 free images this month
- Wait for next month or enable billing

## Cost Monitoring

Set up billing alert (optional):
1. Go to [Billing → Budgets & Alerts](https://console.cloud.google.com/billing/budgets)
2. Create budget: $0.00
3. Get email when approaching limit

---

**Next Steps:**
1. Complete setup above
2. Restart Streamlit app
3. Upload a receipt
4. See improved accuracy! (95-99% vs 85-92%)
