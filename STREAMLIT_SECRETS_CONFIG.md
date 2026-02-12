# 🔐 Streamlit Cloud Secrets Configuration

## For: https://information-collection-system-dgh.streamlit.app/

---

## Step-by-Step Deployment Instructions

### 1. Access Streamlit Cloud Dashboard

1. Go to https://share.streamlit.io
2. Sign in with your GitHub account
3. Find your app: **information-collection-system-dgh**
4. Click on the app name

### 2. Configure Secrets

1. Click the **"Settings"** button (⚙️ icon)
2. Click **"Secrets"** in the left sidebar
3. Paste the configuration below
4. Click **"Save"**

---

## Secrets Configuration

Copy and paste this into the Streamlit Cloud Secrets editor:

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
# OPTIONAL: OpenRouter (Free Models)
# ============================================
[openrouter]
api_key = "YOUR_OPENROUTER_API_KEY_HERE"

# ============================================
# OPTIONAL: Google Gemini
# ============================================
[google_gemini]
api_key = "YOUR_GOOGLE_GEMINI_API_KEY_HERE"

# ============================================
# Settings
# ============================================
[settings]
ocr_engine = "easyocr"
```

---

## How to Get API Keys

### OpenAI (REQUIRED)

1. Go to https://platform.openai.com
2. Sign up or log in
3. Click on **"API Keys"** in the left sidebar
4. Click **"Create new secret key"**
5. Copy the key (starts with `sk-`)
6. Replace `YOUR_OPENAI_API_KEY_HERE` above

**Cost:** Pay-as-you-go (gpt-4o: ~$2.50 per 1M input tokens)

### OpenRouter (OPTIONAL - Free Models Available)

1. Go to https://openrouter.ai
2. Sign up or log in
3. Click on **"Keys"** in the top menu
4. Click **"Create Key"**
5. Copy the key (starts with `sk-or-`)
6. Replace `YOUR_OPENROUTER_API_KEY_HERE` above

**Free Models:**
- google/gemini-flash-1.5
- meta-llama/llama-3.2-3b-instruct:free
- qwen/qwen-2-7b-instruct:free
- microsoft/phi-3-mini-128k-instruct:free

### Google Gemini (OPTIONAL)

1. Go to https://ai.google.dev
2. Click **"Get API key"**
3. Sign in with Google account
4. Click **"Create API key"**
5. Copy the key (starts with `AIza`)
6. Replace `YOUR_GOOGLE_GEMINI_API_KEY_HERE` above

**Free Tier:** 60 requests per minute

---

## Minimal Configuration (OpenAI Only)

If you only want to use OpenAI, use this minimal configuration:

```toml
[openai]
api_key = "sk-your-actual-key-here"

[llm]
provider = "OpenAI"
model = "gpt-4o"

[settings]
ocr_engine = "easyocr"
```

---

## After Saving Secrets

### 3. Reboot the App

1. Go back to the app dashboard
2. Click the **"⋮"** menu (three dots)
3. Click **"Reboot app"**
4. Wait for the app to restart (~30 seconds)

### 4. Test the Deployment

1. Visit https://information-collection-system-dgh.streamlit.app/
2. Go to **Settings** page (⚙️ in sidebar)
3. Verify your provider is shown
4. Click **"Test Connection"**
5. Should show "✅ Connection successful!"

### 5. Test All Features

- **Upload Page:** Upload a test receipt
- **Documents Page:** View and manage documents
- **Chat Page:** Ask a question about expenses
- **Reports Page:** View analytics (after uploading documents)
- **Settings Page:** Verify LLM configuration

---

## Troubleshooting

### "Secrets not found" Error

**Solution:**
1. Make sure you saved the secrets
2. Reboot the app
3. Wait for full restart

### "Invalid API key" Error

**Solution:**
1. Verify API key is correct (no extra spaces)
2. Check key hasn't expired
3. Verify you have credits in your account

### App Won't Start

**Solution:**
1. Check deployment logs in Streamlit Cloud dashboard
2. Look for errors in the logs
3. Verify `requirements.txt` is correct

### Database Resets on Each Deployment

**Expected Behavior:**
- Streamlit Cloud uses ephemeral storage
- Database resets on each deployment
- This is normal for the free tier
- For persistent storage, use external database

---

## Security Notes

✅ **DO:**
- Keep API keys private
- Rotate keys regularly
- Monitor API usage
- Use separate keys for dev/prod

❌ **DON'T:**
- Share your secrets configuration
- Commit secrets to Git
- Use production keys for testing
- Share app URL with sensitive data

---

## Monitoring

### Check App Status

1. Go to https://share.streamlit.io
2. View app dashboard
3. Check deployment status
4. View logs for errors

### Monitor API Usage

**OpenAI:**
- Dashboard: https://platform.openai.com/usage
- Set usage limits to avoid surprises

**OpenRouter:**
- Dashboard: https://openrouter.ai/activity
- Monitor free tier usage

**Google Gemini:**
- Console: https://console.cloud.google.com
- Check quota usage

---

## Updating the App

### Auto-Deploy on Git Push

Streamlit Cloud automatically redeploys when you push to GitHub:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

App will redeploy automatically in ~2-3 minutes.

### Manual Reboot

1. Go to app dashboard
2. Click "⋮" menu
3. Click "Reboot app"

---

## Support

**Issues?**
- Check deployment logs in Streamlit Cloud
- Review `STREAMLIT_CLOUD_DEPLOYMENT.md` for detailed guide
- Open issue on GitHub: https://github.com/manjula-public/Information-Collection-System/issues

---

**Your app is ready to deploy! 🚀**

Just configure the secrets and reboot the app!
