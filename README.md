# POC Information Collection System

**Privacy-Focused Document Processing with AI** 🔒

A proof-of-concept system for automated document processing, data extraction, and AI-powered chat assistance. Designed with privacy and cost-effectiveness in mind.

---

## 🌟 Features

- **📤 Document Upload** - Upload invoices, receipts, and bills (PDF, JPG, PNG)
- **🔍 Smart OCR** - Extract vendor, amount, date, and other key information using PaddleOCR
- **🤖 AI Chat** - Ask questions about your expenses in natural language
- **📊 Dashboard** - View metrics, charts, and insights
- **💰 Auto-Categorization** - Automatically categorize expenses by type
- **🔒 Privacy-Focused** - Option for 100% local processing

---

## 🚀 Quick Start (Streamlit Cloud)

### 1. Deploy to Streamlit Cloud

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

1. **Fork** this repository to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"**
4. Select your forked repository
5. Set **Main file path**: `streamlit_app.py`
6. Click **"Deploy"**

### 2. Configure Secrets

In Streamlit Cloud dashboard, go to **Settings > Secrets** and add:

```toml
[openrouter]
api_key = "your-openrouter-api-key"

[openai]
api_key = "your-openai-api-key"  # Optional fallback
```

**Get API Keys:**
- OpenRouter: [openrouter.ai](https://openrouter.ai) (FREE tier available)
- OpenAI: [platform.openai.com](https://platform.openai.com) (Optional)

### 3. Access Your App

Your app will be available at: `https://your-app-name.streamlit.app`

---

## 💻 Local Development

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd POC-info-collect

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create secrets file
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your API keys

# Run locally
streamlit run streamlit_app.py
```

Access at: `http://localhost:8501`

---

## 📁 Project Structure

```
POC-info-collect/
├── streamlit_app.py          # Main application
├── requirements.txt           # Python dependencies
├── packages.txt              # System dependencies
├── .streamlit/
│   ├── config.toml           # Streamlit configuration
│   └── secrets.toml          # API keys (not in git)
├── pages/
│   ├── 1_📤_Upload.py        # Document upload page
│   ├── 2_📄_Documents.py     # Documents list page
│   └── 3_💬_Chat.py          # AI chat page
├── utils/
│   ├── database.py           # SQLite utilities
│   ├── ocr_service.py        # PaddleOCR integration
│   └── chat_service.py       # OpenRouter/OpenAI chat
└── data/
    └── database.db           # SQLite database (auto-created)
```

---

## 🔧 Technology Stack

### Core
- **Streamlit** - Web UI framework
- **SQLite** - Local database
- **Python 3.11** - Backend

### AI/ML Services
- **PaddleOCR** - Document OCR (100% local)
- **OpenRouter** - LLM API (Llama 3.3 70B - FREE)
- **OpenAI GPT-4o-mini** - Fallback LLM (optional)

### Libraries
- `paddleocr` - OCR engine
- `openai` - LLM client (works with OpenRouter)
- `pandas` - Data manipulation
- `plotly` - Charts and visualizations

---

## 💰 Cost Breakdown

### Streamlit Cloud Deployment
| Service | Cost |
|---------|------|
| Streamlit Cloud Hosting | **FREE** |
| PaddleOCR (runs on cloud VM) | **FREE** |
| OpenRouter (Llama 3.3 70B) | **FREE** (20 RPM limit) |
| OpenAI GPT-4o-mini (fallback) | ~$10-20/month (optional) |
| **Total** | **$0-20/month** |

### Local Docker Deployment
See `05-deployment-options.md` for full local setup with N8N workflows.

---

## 📖 Usage Guide

### 1. Upload Documents

1. Go to **📤 Upload** page
2. Select a PDF or image file
3. Click **"Process Document"**
4. Review extracted information
5. Data is automatically saved

### 2. View Documents

1. Go to **📄 Documents** page
2. View all processed documents
3. Filter by category, vendor, or status
4. Export to CSV

### 3. Chat with AI

1. Go to **💬 Chat** page
2. Ask questions like:
   - "What's my total spending?"
   - "Show me expenses by category"
   - "Who are my top vendors?"
3. Get natural language responses

---

## 🔒 Privacy & Security

### Streamlit Cloud (Demo Mode)
- ⚠️ Data stored on Streamlit's cloud servers
- ⚠️ OCR processing happens on cloud VM
- ✅ Uses OpenRouter (minimal data sharing)
- **Recommendation**: Use for demos only, not production

### Local Docker (Production Mode)
- ✅ 100% data stays on your infrastructure
- ✅ OCR processing completely local
- ✅ Can use Ollama for 100% local LLM
- **Recommendation**: Use for sensitive customer data

See `05-deployment-options.md` for local deployment guide.

---

## 🛠️ Configuration

### Environment Variables (Local)

Create `.streamlit/secrets.toml`:

```toml
[openrouter]
api_key = "sk-or-v1-..."

[openai]
api_key = "sk-..."  # Optional

[settings]
ocr_engine = "paddleocr"
llm_provider = "openrouter"
```

### Streamlit Cloud Secrets

Add in dashboard: **Settings > Secrets**

---

## 📊 Features Roadmap

### ✅ Current (MVP)
- Document upload and OCR
- Basic data extraction
- AI chat assistant
- Auto-categorization
- SQLite database

### 🚧 Coming Soon (Local Deployment)
- N8N workflow automation
- Email ingestion
- WhatsApp ingestion
- Custom API integration
- Advanced analytics

---

## 🤝 Contributing

This is a POC project. For production use, consider:
- Implementing user authentication
- Adding data encryption
- Setting up proper backup systems
- Deploying locally for sensitive data

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🆘 Support

### Common Issues

**OCR not working?**
- Ensure image is clear and high-resolution
- Try different file format (PDF vs JPG)
- Check PaddleOCR installation

**Chat not responding?**
- Verify API keys in secrets
- Check OpenRouter/OpenAI account status
- Review Streamlit logs

**Database errors?**
- Delete `data/database.db` and restart
- Check file permissions

### Documentation

- [Streamlit Docs](https://docs.streamlit.io)
- [PaddleOCR Docs](https://github.com/PaddlePaddle/PaddleOCR)
- [OpenRouter Docs](https://openrouter.ai/docs)

---

## 🎯 Project Goals

1. **Privacy-First** - Keep sensitive data local
2. **Cost-Effective** - Minimize operational costs
3. **Easy to Deploy** - 5-minute setup on Streamlit Cloud
4. **Scalable** - Clear path from demo to production

---

**Built with ❤️ using Streamlit, PaddleOCR, and OpenRouter**
