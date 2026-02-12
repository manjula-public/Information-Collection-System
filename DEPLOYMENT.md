# Streamlit Cloud Deployment Guide

## 🚀 Quick Deployment Steps

### 1. Prepare Repository

Your code is ready! The following files are configured for Streamlit Cloud:

✅ `streamlit_app.py` - Main entry point  
✅ `requirements.txt` - Python dependencies  
✅ `packages.txt` - System dependencies  
✅ `.streamlit/config.toml` - Streamlit configuration  
✅ `pages/` - Multi-page app structure  
✅ `utils/` - Backend services  

### 2. Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Streamlit Cloud POC"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/POC-info-collect.git

# Push
git push -u origin main
```

### 3. Deploy on Streamlit Cloud

1. **Go to**: [share.streamlit.io](https://share.streamlit.io)

2. **Sign in** with GitHub

3. **Click**: "New app"

4. **Configure**:
   - Repository: `YOUR_USERNAME/POC-info-collect`
   - Branch: `main`
   - Main file path: `streamlit_app.py`

5. **Click**: "Deploy!"

### 4. Configure Secrets

Once deployed, go to your app dashboard:

1. Click **"⚙️ Settings"** (bottom right)
2. Click **"Secrets"**
3. Add the following:

```toml
[openrouter]
api_key = "sk-or-v1-YOUR-KEY-HERE"

[openai]
api_key = "sk-YOUR-KEY-HERE"  # Optional fallback
```

4. Click **"Save"**

### 5. Get API Keys

**OpenRouter (FREE tier):**
1. Go to [openrouter.ai](https://openrouter.ai)
2. Sign up / Log in
3. Go to "Keys" section
4. Create new API key
5. Copy key (starts with `sk-or-v1-`)

**OpenAI (Optional fallback):**
1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up / Log in
3. Go to "API Keys"
4. Create new secret key
5. Copy key (starts with `sk-`)

### 6. Access Your App

Your app will be available at:
```
https://YOUR-APP-NAME.streamlit.app
```

---

## 🎯 What You Get

### Features Available on Streamlit Cloud:

✅ **Document Upload** - Upload and process invoices/receipts  
✅ **PaddleOCR** - Extract text and data (runs on cloud VM)  
✅ **AI Chat** - Ask questions using OpenRouter (Llama 3.3 70B - FREE)  
✅ **Dashboard** - View metrics and insights  
✅ **Documents List** - Browse and filter processed documents  
✅ **Auto-categorization** - Automatic expense categorization  
✅ **CSV Export** - Download data as CSV  

### Limitations (vs Local Deployment):

❌ **No N8N workflows** - No email/WhatsApp automation  
❌ **No background processing** - Manual upload only  
❌ **Cloud storage** - Data stored on Streamlit's servers  
⚠️ **Not for production** - Use for demos only  

---

## 💰 Cost

| Service | Cost |
|---------|------|
| Streamlit Cloud Hosting | **FREE** |
| PaddleOCR | **FREE** |
| OpenRouter (Llama 3.3 70B) | **FREE** (20 RPM) |
| OpenAI GPT-4o-mini (optional) | ~$10-20/month |
| **Total** | **$0-20/month** |

---

## 🧪 Testing Your Deployment

### 1. Test Upload

1. Go to **📤 Upload** page
2. Upload a sample invoice (PDF or image)
3. Click "Process Document"
4. Verify extracted data appears

### 2. Test Chat

1. Go to **💬 Chat** page
2. Ask: "What's the total amount?"
3. Verify AI responds correctly

### 3. Test Documents

1. Go to **📄 Documents** page
2. Verify uploaded document appears
3. Test filters and CSV export

---

## 🔧 Troubleshooting

### App Won't Start

**Check logs**:
1. Go to app dashboard
2. Click "Manage app"
3. View logs for errors

**Common issues**:
- Missing dependencies in `requirements.txt`
- Syntax errors in Python files
- Missing secrets

### OCR Not Working

**Symptoms**: "No text detected" or errors during processing

**Solutions**:
- Ensure `packages.txt` includes system dependencies
- Try different image format
- Check image quality (should be clear, high-res)

### Chat Not Responding

**Symptoms**: Error messages or no response

**Solutions**:
- Verify API keys in Secrets
- Check OpenRouter account has credits
- Try OpenAI fallback

### Database Errors

**Symptoms**: "Database locked" or similar

**Solutions**:
- Restart app (Streamlit Cloud auto-restarts)
- Clear browser cache
- Redeploy app

---

## 📊 Monitoring

### View Logs

```
App Dashboard > Manage app > Logs
```

### Check Usage

- **Streamlit Cloud**: View in dashboard
- **OpenRouter**: Check [openrouter.ai/activity](https://openrouter.ai/activity)
- **OpenAI**: Check [platform.openai.com/usage](https://platform.openai.com/usage)

---

## 🔄 Updating Your App

### Method 1: Git Push (Automatic)

```bash
# Make changes to code
git add .
git commit -m "Update: description"
git push

# Streamlit Cloud auto-deploys!
```

### Method 2: Manual Redeploy

1. Go to app dashboard
2. Click "⋮" menu
3. Click "Reboot app"

---

## 🎨 Customization

### Change Theme

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FF6B6B"  # Change this
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

### Add Custom Domain

Streamlit Cloud supports custom domains:
1. Go to app settings
2. Click "Custom domain"
3. Follow instructions

---

## 🔒 Security Best Practices

### For Demo/Testing:
- ✅ Use OpenRouter free tier
- ✅ Set rate limits
- ✅ Don't upload sensitive data
- ✅ Use test/sample invoices only

### For Production:
- ❌ Don't use Streamlit Cloud
- ✅ Deploy locally with Docker
- ✅ Use 100% local OCR + LLM
- ✅ Implement authentication

---

## 📱 Sharing Your Demo

### Public Link

Share your app URL:
```
https://your-app-name.streamlit.app
```

### Embed in Website

```html
<iframe src="https://your-app-name.streamlit.app" 
        width="100%" height="800px">
</iframe>
```

### QR Code

Generate QR code for your app URL for easy mobile access.

---

## 🎓 Next Steps

### After Successful Deployment:

1. ✅ **Test thoroughly** with sample documents
2. ✅ **Share with customers** for feedback
3. ✅ **Gather requirements** for production
4. ✅ **Plan local deployment** for real data

### Moving to Production:

See `05-deployment-options.md` for local Docker Compose setup with:
- N8N workflow automation
- Email/WhatsApp ingestion
- 100% privacy mode
- Custom API integration

---

## 📞 Support

### Streamlit Cloud Issues:
- [Streamlit Community Forum](https://discuss.streamlit.io)
- [Streamlit Docs](https://docs.streamlit.io)

### OpenRouter Issues:
- [OpenRouter Discord](https://discord.gg/openrouter)
- [OpenRouter Docs](https://openrouter.ai/docs)

### Code Issues:
- Check GitHub Issues
- Review logs in Streamlit dashboard

---

**🎉 Congratulations! Your POC is now live on Streamlit Cloud!**
