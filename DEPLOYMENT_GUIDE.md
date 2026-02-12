# 🚀 Local Deployment Guide - POC Information Collection System

Complete step-by-step guide to run this application on your local machine.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Application](#running-the-application)
5. [Troubleshooting](#troubleshooting)
6. [Optional Features](#optional-features)

---

## Prerequisites

### Required Software

1. **Python 3.8 or higher**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"
   - Verify installation:
     ```bash
     python --version
     ```

2. **Git** (if cloning from repository)
   - Download from: https://git-scm.com/downloads
   - Verify installation:
     ```bash
     git --version
     ```

### Optional Software

- **Google Cloud Vision API** (for better OCR)
- **Ollama** (for local LLM)

---

## Installation

### Step 1: Get the Code

**Option A: If you already have the code**
```bash
cd D:\AI-TEAM\PROJECTS\POC-info-collect
```

**Option B: Clone from Git**
```bash
git clone <your-repo-url>
cd POC-info-collect
```

### Step 2: Create Virtual Environment

**Windows (PowerShell):**
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
.\venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

**Expected packages:**
- streamlit
- easyocr
- torch & torchvision
- openai
- google-cloud-vision
- google-generativeai
- plotly
- pandas
- opencv-python-headless
- Pillow

**Installation time:** ~5-10 minutes (depending on internet speed)

---

## Configuration

### Step 1: Configure Secrets

Create or edit `.streamlit/secrets.toml`:

```toml
# General Settings
[settings]
ocr_engine = "easyocr"  # or "google_vision"

# OpenAI Configuration (Default)
[openai]
api_key = "sk-your-openai-api-key-here"

# LLM Configuration
[llm]
provider = "OpenAI"
model = "gpt-4o"

# Optional: OpenRouter (Free models)
[openrouter]
api_key = "sk-or-your-openrouter-key"

# Optional: Google Gemini
[google_gemini]
api_key = "AIza-your-gemini-key"

# Optional: Google Cloud Vision
[google_vision]
enabled = false
credentials_path = "google-vision-key.json"

# Optional: Ollama (Local)
[ollama]
base_url = "http://localhost:11434"
```

### Step 2: Get API Keys

#### OpenAI (Required for Chat)

1. Go to https://platform.openai.com
2. Sign up or log in
3. Navigate to **API Keys** section
4. Click **Create new secret key**
5. Copy the key (starts with `sk-`)
6. Paste into `secrets.toml` under `[openai]`

#### OpenRouter (Optional - Free Models)

1. Go to https://openrouter.ai
2. Sign up or log in
3. Navigate to **Keys** section
4. Create new API key
5. Copy and paste into `secrets.toml` under `[openrouter]`

#### Google Gemini (Optional)

1. Go to https://ai.google.dev
2. Get API key from Google AI Studio
3. Copy and paste into `secrets.toml` under `[google_gemini]`

### Step 3: Create Data Directory

```bash
# Create data directory if it doesn't exist
mkdir -p data
```

---

## Running the Application

### Step 1: Start the Application

**Windows (PowerShell):**
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Run Streamlit
streamlit run streamlit_app.py
```

**macOS/Linux:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run Streamlit
streamlit run streamlit_app.py
```

### Step 2: Access the Application

The application will automatically open in your browser at:
- **Local URL:** http://localhost:8501
- **Network URL:** http://192.168.x.x:8501 (accessible from other devices on your network)

If it doesn't open automatically, manually navigate to http://localhost:8501

### Step 3: First-Time Setup

1. **Go to Settings Page** (⚙️ Settings in sidebar)
2. **Configure LLM Provider:**
   - Select provider (OpenAI recommended)
   - Select model (gpt-4o recommended)
   - Enter API key
   - Click "Test Connection"
   - Click "Save Configuration"

3. **Upload a Test Document:**
   - Go to Upload page (📤 Upload)
   - Upload a receipt or invoice image
   - Wait for processing
   - Check extracted data

4. **View Results:**
   - Go to Documents page (📄 Documents) to see uploaded files
   - Go to Reports page (📊 Reports) to see analytics
   - Go to Chat page (💬 Chat) to ask questions

---

## Troubleshooting

### Common Issues

#### 1. "streamlit: command not found"

**Solution:**
```bash
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # macOS/Linux

# Or run with full path
.\venv\Scripts\streamlit run streamlit_app.py
```

#### 2. "No module named 'streamlit'"

**Solution:**
```bash
# Reinstall requirements
pip install -r requirements.txt
```

#### 3. Port 8501 already in use

**Solution:**
```bash
# Kill existing Streamlit process
Get-Process | Where-Object {$_.ProcessName -eq "streamlit"} | Stop-Process -Force

# Or use different port
streamlit run streamlit_app.py --server.port 8502
```

#### 4. Database errors

**Solution:**
```bash
# Delete and recreate database
Remove-Item data\database.db
# Restart Streamlit - database will be recreated
```

#### 5. OpenAI API errors

**Solution:**
- Check API key is correct in `.streamlit/secrets.toml`
- Verify you have credits in your OpenAI account
- Test connection in Settings page

#### 6. OCR not working

**Solution:**
- Make sure image is clear and well-lit
- Try different OCR engine in Settings
- Check image format (JPG, PNG supported)

---

## Optional Features

### Google Cloud Vision API (Better OCR)

1. **Follow setup guide:** See `GOOGLE_VISION_SETUP.md`
2. **Enable in secrets.toml:**
   ```toml
   [settings]
   ocr_engine = "google_vision"
   
   [google_vision]
   enabled = true
   credentials_path = "google-vision-key.json"
   ```

### Local LLM with Ollama

1. **Install Ollama:**
   - Download from https://ollama.ai
   - Install on your system

2. **Pull a model:**
   ```bash
   ollama pull llama3.2
   ```

3. **Start Ollama server:**
   ```bash
   ollama serve
   ```

4. **Configure in Settings page:**
   - Provider: Local (Ollama)
   - Model: llama3.2
   - Base URL: http://localhost:11434

---

## Stopping the Application

**To stop Streamlit:**
- Press `Ctrl + C` in the terminal
- Or close the terminal window

**To deactivate virtual environment:**
```bash
deactivate
```

---

## Directory Structure

```
POC-info-collect/
├── .streamlit/
│   ├── config.toml          # Streamlit configuration
│   └── secrets.toml         # API keys (DO NOT COMMIT)
├── data/
│   └── database.db          # SQLite database
├── pages/
│   ├── 1_📤_Upload.py       # Upload page
│   ├── 2_📄_Documents.py    # Documents management
│   ├── 3_💬_Chat.py         # AI chat assistant
│   ├── 4_📊_Reports.py      # Analytics & reports
│   └── 5_⚙️_Settings.py     # Settings & configuration
├── utils/
│   ├── database.py          # Database functions
│   ├── ocr_service.py       # OCR processing
│   └── chat_service.py      # LLM integration
├── venv/                    # Virtual environment (DO NOT COMMIT)
├── streamlit_app.py         # Main application
├── requirements.txt         # Python dependencies
├── DEPLOYMENT_GUIDE.md      # This file
└── README.md                # Project overview
```

---

## Quick Start Commands

**Complete setup from scratch:**

```powershell
# 1. Navigate to project
cd D:\AI-TEAM\PROJECTS\POC-info-collect

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure API keys
# Edit .streamlit/secrets.toml and add your OpenAI API key

# 6. Run application
streamlit run streamlit_app.py
```

**Daily usage:**

```powershell
# 1. Navigate to project
cd D:\AI-TEAM\PROJECTS\POC-info-collect

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Run application
streamlit run streamlit_app.py
```

---

## Next Steps

1. ✅ **Test Upload:** Upload a sample receipt
2. ✅ **Configure LLM:** Set up your preferred AI provider
3. ✅ **Explore Features:** Try all pages (Upload, Documents, Chat, Reports, Settings)
4. ✅ **Customize:** Adjust settings to your preferences
5. ✅ **Deploy:** Consider deploying to Streamlit Cloud for remote access

---

## Support

**Common Questions:**

- **How do I update the application?**
  ```bash
  git pull  # If using Git
  pip install -r requirements.txt --upgrade
  ```

- **How do I backup my data?**
  ```bash
  # Backup database
  copy data\database.db data\database_backup.db
  ```

- **How do I reset everything?**
  ```bash
  # Delete database
  Remove-Item data\database.db
  # Restart Streamlit
  ```

---

## Security Notes

⚠️ **Important:**
- Never commit `.streamlit/secrets.toml` to Git
- Keep your API keys private
- Add `secrets.toml` to `.gitignore`
- Regularly rotate API keys
- Use environment variables for production

---

**You're all set! 🎉**

The application is now running locally. Access it at http://localhost:8501
