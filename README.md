# POC Information Collection System

AI-powered document processing and expense tracking system with OCR, multi-provider LLM support, and analytics.

## 🌐 Live Demo

**Streamlit Cloud:** https://information-collection-system-dgh.streamlit.app/

## ✨ Features

- 📤 **Document Upload** - OCR-powered receipt/invoice processing
- 📄 **Document Management** - Full CRUD operations with edit/delete
- 💬 **AI Chat Assistant** - Natural language queries about expenses
- 📊 **Analytics & Reports** - Category-based spending analysis with charts
- ⚙️ **Settings** - Multi-provider LLM configuration

### LLM Providers Supported

- **OpenAI** (gpt-4o, gpt-4-turbo, gpt-3.5-turbo)
- **OpenRouter** (Free models: Gemini Flash, Llama, Qwen, Phi-3)
- **Google Gemini** (gemini-pro, gemini-1.5-pro, gemini-1.5-flash)
- **Local Ollama** (llama3.2, mistral, codellama, phi3)

## 🚀 Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/manjula-public/Information-Collection-System.git
cd Information-Collection-System

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure secrets
# Edit .streamlit/secrets.toml and add your API keys

# Run application
streamlit run streamlit_app.py
```

Access at: http://localhost:8501

### Configuration

Create `.streamlit/secrets.toml`:

```toml
[openai]
api_key = "sk-your-key"

[llm]
provider = "OpenAI"
model = "gpt-4o"
```

## 📖 Documentation

- [Local Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Streamlit Cloud Deployment](STREAMLIT_CLOUD_DEPLOYMENT.md)
- [Google Vision Setup](GOOGLE_VISION_SETUP.md)

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **OCR:** EasyOCR, Google Cloud Vision
- **LLM:** OpenAI, OpenRouter, Google Gemini, Ollama
- **Database:** SQLite
- **Charts:** Plotly
- **Image Processing:** OpenCV, Pillow

## 📁 Project Structure

```
Information-Collection-System/
├── pages/
│   ├── 1_📤_Upload.py       # Document upload & OCR
│   ├── 2_📄_Documents.py    # Document management
│   ├── 3_💬_Chat.py         # AI chat assistant
│   ├── 4_📊_Reports.py      # Analytics & charts
│   └── 5_⚙️_Settings.py     # LLM configuration
├── utils/
│   ├── database.py          # Database operations
│   ├── ocr_service.py       # OCR processing
│   └── chat_service.py      # LLM integration
├── streamlit_app.py         # Main application
└── requirements.txt         # Dependencies
```

## 🔧 Features in Detail

### Document Processing
- Upload receipts/invoices (JPG, PNG)
- OCR extraction (vendor, date, amount, line items)
- Auto-categorization (8 grocery categories)
- Line item tracking with quantities and prices

### Analytics
- Category-based spending analysis
- Bar and pie charts
- Top items ranking
- Line item details per document

### AI Chat
- Natural language queries
- SQL generation from questions
- Multi-provider LLM support
- Fallback to basic responses

## 🔐 Security

- API keys stored in Streamlit secrets (not in Git)
- `.gitignore` configured for sensitive files
- Masked password inputs
- No hardcoded credentials

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using Streamlit**
