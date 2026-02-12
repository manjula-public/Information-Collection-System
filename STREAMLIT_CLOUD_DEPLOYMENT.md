# 🌐 Streamlit Cloud Deployment Guide

Complete step-by-step guide to deploy the POC Information Collection System to Streamlit Cloud.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Prepare Your Repository](#prepare-your-repository)
3. [Deploy to Streamlit Cloud](#deploy-to-streamlit-cloud)
4. [Configure Secrets](#configure-secrets)
5. [Troubleshooting](#troubleshooting)
6. [Post-Deployment](#post-deployment)

---

## Prerequisites

### Required

1. **GitHub Account**
   - Sign up at https://github.com if you don't have one

2. **Streamlit Cloud Account**
   - Sign up at https://streamlit.io/cloud
   - Use your GitHub account to sign in

3. **API Keys**
   - OpenAI API key (required for chat)
   - Optional: OpenRouter, Google Gemini, Google Cloud Vision

### Optional but Recommended

- Git installed locally
- GitHub Desktop (easier than command line)

---

## Prepare Your Repository

### Step 1: Create .gitignore

Create or update `.gitignore` in your project root:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Streamlit
.streamlit/secrets.toml

# Data
data/database.db
data/*.db

# Google Cloud
google-vision-key.json
*.json

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Uploads
uploads/
temp/
```

**⚠️ CRITICAL:** Make sure `secrets.toml` is in `.gitignore` to avoid exposing API keys!

### Step 2: Verify requirements.txt

Ensure `requirements.txt` has all dependencies:

```txt
streamlit==1.31.0
easyocr==1.7.0
torch==2.2.0
torchvision==0.17.0
Pillow==9.5.0
openai>=2.0.0
requests==2.31.0
pandas==2.2.0
plotly==5.18.0
python-dotenv==1.0.1
opencv-python-headless==4.9.0.80
google-cloud-vision==3.7.0
google-generativeai
```

### Step 3: Create README.md

Create a `README.md` for your repository:

```markdown
# POC Information Collection System

AI-powered document processing and expense tracking system.

## Features

- 📤 Document upload with OCR
- 📄 Document management (CRUD)
- 💬 AI chat assistant
- 📊 Category-based analytics
- ⚙️ Multi-provider LLM support

## Live Demo

[View on Streamlit Cloud](https://your-app-url.streamlit.app)

## Local Setup

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## Configuration

Requires API keys for:
- OpenAI (required)
- OpenRouter (optional)
- Google Gemini (optional)
- Google Cloud Vision (optional)
```

### Step 4: Push to GitHub

**Option A: Using Git Command Line**

```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - POC Info Collection System"

# Create repository on GitHub first, then:
git remote add origin https://github.com/YOUR-USERNAME/POC-info-collect.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Option B: Using GitHub Desktop**

1. Open GitHub Desktop
2. Click "Add" → "Add Existing Repository"
3. Select your project folder
4. Click "Publish repository"
5. Choose repository name
6. Uncheck "Keep this code private" if you want it public
7. Click "Publish Repository"

---

## Deploy to Streamlit Cloud

### Step 1: Sign in to Streamlit Cloud

1. Go to https://share.streamlit.io
2. Click "Sign in with GitHub"
3. Authorize Streamlit to access your GitHub

### Step 2: Create New App

1. Click **"New app"** button
2. Fill in the deployment form:

   **Repository:**
   - Select your GitHub repository: `YOUR-USERNAME/POC-info-collect`

   **Branch:**
   - `main` (or your default branch)

   **Main file path:**
   - `streamlit_app.py`

   **App URL (optional):**
   - Choose a custom subdomain: `your-app-name.streamlit.app`

3. Click **"Advanced settings"** (IMPORTANT!)

### Step 3: Configure Advanced Settings

**Python version:**
- Select `3.9` or higher

**Secrets:**
Click "Secrets" and paste your configuration:

```toml
# OpenAI Configuration (Required)
[openai]
api_key = "sk-your-openai-api-key-here"

# LLM Configuration
[llm]
provider = "OpenAI"
model = "gpt-4o"

# Optional: OpenRouter
[openrouter]
api_key = "sk-or-your-openrouter-key"

# Optional: Google Gemini
[google_gemini]
api_key = "AIza-your-gemini-key"

# Optional: Google Cloud Vision
[google_vision]
enabled = false

# Settings
[settings]
ocr_engine = "easyocr"
```

**⚠️ IMPORTANT:** 
- Do NOT include `google-vision-key.json` content here
- Use EasyOCR for Streamlit Cloud (Google Vision requires file upload)
- Keep API keys secure - never commit to Git

4. Click **"Save"**

### Step 4: Deploy

1. Click **"Deploy!"**
2. Wait for deployment (usually 2-5 minutes)
3. Watch the deployment logs for any errors

---

## Configure Secrets

### Managing Secrets After Deployment

1. Go to your app dashboard: https://share.streamlit.io
2. Click on your app
3. Click **"Settings"** (⚙️ icon)
4. Click **"Secrets"**
5. Edit secrets as needed
6. Click **"Save"**
7. App will automatically restart

### Secrets Format

```toml
# Minimal configuration (OpenAI only)
[openai]
api_key = "sk-..."

[llm]
provider = "OpenAI"
model = "gpt-4o"

# Full configuration (all providers)
[openai]
api_key = "sk-..."

[openrouter]
api_key = "sk-or-..."

[google_gemini]
api_key = "AIza..."

[llm]
provider = "OpenAI"
model = "gpt-4o"

[settings]
ocr_engine = "easyocr"
```

---

## Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError"

**Problem:** Missing dependencies

**Solution:**
- Check `requirements.txt` has all packages
- Ensure versions are compatible
- Push updated `requirements.txt` to GitHub

#### 2. "Secrets not found"

**Problem:** Secrets not configured

**Solution:**
- Go to app Settings → Secrets
- Add required secrets (at minimum: `[openai]` section)
- Save and restart app

#### 3. "App is sleeping"

**Problem:** Streamlit Cloud free tier sleeps after inactivity

**Solution:**
- Just visit the URL - it will wake up automatically
- Consider upgrading for always-on apps

#### 4. Database errors

**Problem:** SQLite database not persisting

**Solution:**
- This is expected on Streamlit Cloud (ephemeral storage)
- Database resets on each deployment
- For persistent storage, use external database (PostgreSQL, MongoDB)

#### 5. Large file uploads failing

**Problem:** Streamlit Cloud has file size limits

**Solution:**
- Limit file uploads to < 200MB
- Add file size validation in upload page

#### 6. Torch/EasyOCR installation timeout

**Problem:** Large dependencies timing out

**Solution:**
- Use lighter OCR alternatives
- Or use Google Cloud Vision API (requires setup)

### Viewing Logs

1. Go to app dashboard
2. Click "Manage app"
3. View deployment logs
4. Check for errors during startup

---

## Post-Deployment

### Step 1: Test Your App

1. Visit your app URL: `https://your-app-name.streamlit.app`
2. Test all features:
   - ✅ Upload a document
   - ✅ View documents page
   - ✅ Test chat assistant
   - ✅ Check reports page
   - ✅ Configure settings

### Step 2: Configure Settings

1. Go to Settings page (⚙️)
2. Verify LLM configuration
3. Test connection to your chosen provider
4. Save configuration

### Step 3: Share Your App

Your app is now live! Share the URL:
- `https://your-app-name.streamlit.app`

### Step 4: Monitor Usage

**Streamlit Cloud Dashboard:**
- View app analytics
- Monitor resource usage
- Check deployment history

**Free Tier Limits:**
- 1 GB RAM
- 1 CPU
- Unlimited viewers
- Apps sleep after inactivity

---

## Updating Your App

### Method 1: Push to GitHub

```bash
# Make changes locally
git add .
git commit -m "Update feature X"
git push

# Streamlit Cloud auto-deploys on push
```

### Method 2: Reboot App

1. Go to app dashboard
2. Click "⋮" menu
3. Click "Reboot app"

### Method 3: Manual Redeploy

1. Go to app dashboard
2. Click "⋮" menu
3. Click "Delete app"
4. Redeploy from scratch

---

## Security Best Practices

### ✅ DO

- Use `.gitignore` for secrets
- Store API keys in Streamlit Cloud Secrets
- Use environment variables
- Regularly rotate API keys
- Monitor API usage
- Enable 2FA on GitHub

### ❌ DON'T

- Commit `secrets.toml` to Git
- Hardcode API keys in code
- Share your app URL with API keys visible
- Use production API keys for testing
- Expose sensitive data in logs

---

## Upgrading to Paid Plan

**Streamlit Cloud Plans:**

**Free:**
- 1 private app
- Unlimited public apps
- Community support

**Team ($20/month per editor):**
- Unlimited private apps
- Always-on apps
- Priority support
- Custom domains

**Enterprise:**
- SSO
- Advanced security
- Dedicated support
- Custom SLA

**Upgrade at:** https://streamlit.io/cloud

---

## Alternative Deployment Options

### 1. Docker + Cloud Run

- More control
- Better for production
- Requires Docker knowledge

### 2. Heroku

- Easy deployment
- Paid plans required
- Good for small apps

### 3. AWS/Azure/GCP

- Full control
- More complex setup
- Best for enterprise

### 4. Self-hosted

- Complete control
- Requires server management
- See `DEPLOYMENT_GUIDE.md` for local setup

---

## Quick Reference

### Deployment Checklist

- [ ] Create `.gitignore` (exclude secrets)
- [ ] Verify `requirements.txt`
- [ ] Create `README.md`
- [ ] Push to GitHub
- [ ] Sign in to Streamlit Cloud
- [ ] Create new app
- [ ] Configure secrets
- [ ] Deploy
- [ ] Test all features
- [ ] Share URL

### Important URLs

- **Streamlit Cloud:** https://share.streamlit.io
- **Your App:** https://your-app-name.streamlit.app
- **GitHub Repo:** https://github.com/YOUR-USERNAME/POC-info-collect
- **Documentation:** https://docs.streamlit.io/streamlit-community-cloud

---

## Support

**Streamlit Community:**
- Forum: https://discuss.streamlit.io
- Documentation: https://docs.streamlit.io
- GitHub: https://github.com/streamlit/streamlit

**Common Questions:**

**Q: How do I add a custom domain?**
A: Available on Team/Enterprise plans. Configure in app settings.

**Q: Can I use a database?**
A: Yes, but use external DB (PostgreSQL, MongoDB). SQLite is ephemeral.

**Q: How do I increase memory?**
A: Upgrade to paid plan or optimize your app.

**Q: Can I password-protect my app?**
A: Use Streamlit's built-in authentication or implement custom auth.

---

**You're ready to deploy! 🚀**

Follow these steps and your app will be live on Streamlit Cloud in minutes!
