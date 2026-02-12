# Information Collection System - REVISED Architecture (Local N8N + Streamlit)

## 1. System Architecture Overview

This document provides the revised architecture for a **local-first, cost-effective** deployment using **N8N**, **Streamlit**, and **Python**.

---

## 2. Simplified Local Architecture

```mermaid
graph TB
    subgraph "Data Sources"
        EMAIL[Email<br/>IMAP]
        WHATSAPP[WhatsApp<br/>Business API]
        UPLOAD[Manual Upload<br/>Streamlit]
    end
    
    subgraph "N8N Workflows (Port 5678)"
        WF1[Email Ingestion<br/>Workflow]
        WF2[WhatsApp Ingestion<br/>Workflow]
        WF3[Processing<br/>Workflow]
        WF4[API Integration<br/>Workflow]
    end
    
    subgraph "Python Services (Port 8001)"
        OCR[OCR Service<br/>FastAPI]
        CLASS[Classifier]
        CHAT[Chat Service<br/>OpenAI]
    end
    
    subgraph "Storage (Local)"
        FILES[/data/raw/<br/>Local Files]
        DB[(SQLite<br/>database.db)]
    end
    
    subgraph "Streamlit UI (Port 8501)"
        DASH[Dashboard]
        DOCS[Documents]
        CHATUI[Chat]
        SETTINGS[Settings]
    end
    
    subgraph "External"
        API[Custom API]
    end
    
    EMAIL --> WF1
    WHATSAPP --> WF2
    UPLOAD --> WF3
    
    WF1 & WF2 --> FILES
    WF1 & WF2 & WF3 --> OCR
    OCR --> CLASS
    CLASS --> DB
    
    WF4 --> API
    
    DB --> DASH & DOCS & CHATUI
    CHATUI --> CHAT
    CHAT --> DB
```

---

## 3. Docker Compose Architecture

```mermaid
graph TB
    subgraph "Docker Compose Stack"
        subgraph "Container: n8n"
            N8N[N8N Server<br/>:5678]
            N8N_DATA[/home/node/.n8n]
        end
        
        subgraph "Container: python-services"
            FASTAPI[FastAPI<br/>:8001]
            OCR_SVC[OCR Service]
            CHAT_SVC[Chat Service]
        end
        
        subgraph "Container: streamlit"
            ST[Streamlit App<br/>:8501]
        end
        
        subgraph "Host Volumes"
            DATA[./data/<br/>SQLite + Files]
            N8N_VOL[./data/n8n/]
        end
    end
    
    N8N --> FASTAPI
    ST --> FASTAPI
    ST --> DATA
    FASTAPI --> DATA
    N8N_DATA -.-> N8N_VOL
```

---

## 4. N8N Workflow Diagrams

### 4.1 Email Ingestion Workflow

```mermaid
flowchart LR
    START([Email Trigger<br/>IMAP Poll]) --> FILTER{Has<br/>Attachment?}
    FILTER -->|No| SKIP([Skip])
    FILTER -->|Yes| EXTRACT[Extract<br/>Attachments]
    EXTRACT --> SAVE[Save to<br/>/data/raw/]
    SAVE --> HTTP1[HTTP Request<br/>OCR Service]
    HTTP1 --> PARSE[Parse<br/>Response]
    PARSE --> DB[Save to<br/>SQLite]
    DB --> RULES{Match<br/>Rules?}
    RULES -->|Yes| API[Call Custom<br/>API]
    RULES -->|No| DONE([Done])
    API --> DONE
```

### 4.2 WhatsApp Ingestion Workflow

```mermaid
flowchart LR
    START([Webhook<br/>Trigger]) --> CHECK{Has<br/>Media?}
    CHECK -->|No| TEXT[Process<br/>Text Only]
    CHECK -->|Yes| DOWNLOAD[Download<br/>Media]
    DOWNLOAD --> SAVE[Save to<br/>/data/raw/]
    SAVE --> HTTP[HTTP Request<br/>OCR Service]
    HTTP --> DB[Save to<br/>SQLite]
    DB --> REPLY[Send WhatsApp<br/>Confirmation]
    REPLY --> DONE([Done])
    TEXT --> DB
```

### 4.3 Processing Workflow (Called by Upload)

```mermaid
flowchart LR
    START([Webhook<br/>from Streamlit]) --> VALIDATE{Valid<br/>File?}
    VALIDATE -->|No| ERROR[Return<br/>Error]
    VALIDATE -->|Yes| OCR[Call OCR<br/>Service]
    OCR --> CLASSIFY[Call<br/>Classifier]
    CLASSIFY --> EXTRACT[Extract<br/>Entities]
    EXTRACT --> VALIDATE2{Data<br/>Valid?}
    VALIDATE2 -->|No| REVIEW[Flag for<br/>Review]
    VALIDATE2 -->|Yes| DB[Save to<br/>SQLite]
    DB --> SUCCESS[Return<br/>Success]
```

---

## 5. Data Flow

### 5.1 Document Processing Flow

```mermaid
sequenceDiagram
    participant Source as Email/WhatsApp/Upload
    participant N8N as N8N Workflow
    participant FS as File System
    participant OCR as OCR Service
    participant DB as SQLite
    participant API as Custom API
    
    Source->>N8N: New document
    N8N->>FS: Save raw file
    N8N->>OCR: POST /ocr/invoice
    OCR-->>N8N: Extracted data
    N8N->>DB: INSERT transaction
    N8N->>N8N: Evaluate rules
    alt Rule matched
        N8N->>API: POST /api/expense
        API-->>N8N: Confirmation
    end
    N8N-->>Source: Success notification
```

### 5.2 Chat Query Flow

```mermaid
sequenceDiagram
    participant User as User
    participant UI as Streamlit
    participant Chat as Chat Service
    participant DB as SQLite
    participant LLM as OpenAI
    
    User->>UI: Ask question
    UI->>Chat: POST /chat
    Chat->>Chat: Parse query
    Chat->>DB: Execute SQL
    DB-->>Chat: Results
    Chat->>LLM: Format with context
    LLM-->>Chat: Natural language response
    Chat-->>UI: Response
    UI-->>User: Display answer
```

---

## 6. Database Schema (SQLite)

```mermaid
erDiagram
    DOCUMENTS ||--o{ TRANSACTIONS : contains
    TRANSACTIONS }o--|| CATEGORIES : belongs_to
    
    DOCUMENTS {
        integer id PK
        text source
        text document_type
        text status
        real confidence_score
        text file_path
        timestamp uploaded_at
        timestamp processed_at
        text metadata
    }
    
    TRANSACTIONS {
        integer id PK
        integer document_id FK
        text vendor_name
        text invoice_number
        date transaction_date
        real amount
        text currency
        real tax_amount
        text category
        text department
        text status
        text notes
    }
    
    CATEGORIES {
        integer id PK
        text name
        integer parent_id FK
        text department
    }
```

---

## 7. Streamlit UI Structure

```mermaid
graph TB
    MAIN[app.py<br/>Main Entry]
    
    subgraph "Pages"
        DASH[pages/dashboard.py]
        UP[pages/upload.py]
        DOCS[pages/documents.py]
        CHAT[pages/chat.py]
        SET[pages/settings.py]
    end
    
    subgraph "Components"
        METRICS[components/metrics.py]
        CHARTS[components/charts.py]
        TABLE[components/table.py]
    end
    
    subgraph "Utils"
        DB_UTIL[utils/database.py]
        API_UTIL[utils/api_client.py]
    end
    
    MAIN --> DASH & UP & DOCS & CHAT & SET
    DASH --> METRICS & CHARTS
    DOCS --> TABLE
    CHAT --> API_UTIL
    DASH & DOCS --> DB_UTIL
```

---

## 8. File Structure

```
POC-info-collect/
├── docker-compose.yml
├── .env
├── README.md
│
├── data/                      # Shared volume
│   ├── raw/                   # Raw uploaded files
│   │   ├── email/
│   │   ├── whatsapp/
│   │   └── upload/
│   ├── database.db            # SQLite database
│   └── n8n/                   # N8N workflows & data
│
├── services/                  # Python services
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py               # FastAPI app
│   ├── ocr_service.py
│   ├── classifier.py
│   └── chat_service.py
│
├── frontend/                  # Streamlit UI
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py                # Main Streamlit app
│   ├── pages/
│   │   ├── dashboard.py
│   │   ├── upload.py
│   │   ├── documents.py
│   │   ├── chat.py
│   │   └── settings.py
│   ├── components/
│   │   ├── metrics.py
│   │   └── charts.py
│   └── utils/
│       ├── database.py
│       └── api_client.py
│
└── n8n-workflows/            # N8N workflow exports
    ├── email_ingestion.json
    ├── whatsapp_ingestion.json
    ├── processing.json
    └── api_integration.json
```

---

## 9. Network & Ports

```mermaid
graph LR
    subgraph "Host Machine"
        BROWSER[Web Browser]
    end
    
    subgraph "Docker Network"
        N8N[N8N<br/>:5678]
        SERVICES[Python Services<br/>:8001]
        STREAMLIT[Streamlit<br/>:8501]
    end
    
    BROWSER -->|http://localhost:5678| N8N
    BROWSER -->|http://localhost:8501| STREAMLIT
    STREAMLIT -->|Internal| SERVICES
    N8N -->|Internal| SERVICES
```

**Port Mapping:**
- `5678` → N8N Web UI
- `8001` → Python Services API
- `8501` → Streamlit UI

---

## 10. Deployment Flow

```mermaid
flowchart TB
    START([Start]) --> CLONE[Clone Repository]
    CLONE --> ENV[Create .env file]
    ENV --> DOCKER{Docker<br/>Installed?}
    DOCKER -->|No| INSTALL[Install Docker]
    DOCKER -->|Yes| BUILD[docker-compose build]
    INSTALL --> BUILD
    BUILD --> UP[docker-compose up]
    UP --> WAIT[Wait for services<br/>to start]
    WAIT --> N8N_UI[Open N8N<br/>localhost:5678]
    N8N_UI --> IMPORT[Import workflows]
    IMPORT --> CONFIG[Configure<br/>credentials]
    CONFIG --> ST_UI[Open Streamlit<br/>localhost:8501]
    ST_UI --> READY([System Ready])
```

---

## 11. Cost Comparison

```mermaid
graph TB
    subgraph "Cloud Architecture (Original)"
        C1[AWS Infrastructure: $200-500]
        C2[RDS Database: $100-200]
        C3[S3 Storage: $50-100]
        C4[AI Services: $300-800]
        C5[Monitoring: $50-100]
        TOTAL1[Total: $700-1,700/month]
    end
    
    subgraph "Local Architecture (Revised)"
        L1[Infrastructure: $0]
        L2[Database: $0]
        L3[Storage: $0]
        L4[AI Services: $130]
        L5[Monitoring: $0]
        TOTAL2[Total: $130/month]
    end
    
    C1 & C2 & C3 & C4 & C5 --> TOTAL1
    L1 & L2 & L3 & L4 & L5 --> TOTAL2
    
    style TOTAL2 fill:#90EE90
    style TOTAL1 fill:#FFB6C1
```

**92% Cost Reduction!**

---

## 12. Scaling Path

```mermaid
flowchart LR
    MVP[MVP<br/>Local SQLite] --> STAGE1[Stage 1<br/>Local PostgreSQL]
    STAGE1 --> STAGE2[Stage 2<br/>Cloud PostgreSQL<br/>+ S3]
    STAGE2 --> PROD[Production<br/>Full Cloud<br/>Kubernetes]
    
    MVP -.->|Easy upgrade| STAGE1
    STAGE1 -.->|Minimal changes| STAGE2
    STAGE2 -.->|Containerized| PROD
```

---

## 13. Integration Architecture

```mermaid
graph LR
    subgraph "Internal System"
        N8N[N8N Workflow]
        MAPPER[Data Mapper<br/>Node]
    end
    
    subgraph "Custom API"
        ENDPOINT[POST /api/expense]
        AUTH[API Key Auth]
    end
    
    N8N --> MAPPER
    MAPPER --> AUTH
    AUTH --> ENDPOINT
    
    ENDPOINT -.->|Webhook| N8N
```

**N8N HTTP Request Node Configuration:**
```json
{
  "method": "POST",
  "url": "https://your-api.com/api/expense",
  "authentication": "headerAuth",
  "headerAuth": {
    "name": "X-API-Key",
    "value": "your-api-key"
  },
  "body": {
    "vendor": "={{$json.vendor_name}}",
    "amount": "={{$json.amount}}",
    "date": "={{$json.transaction_date}}",
    "category": "={{$json.category}}"
  }
}
```

---

## 14. Monitoring (Simple)

```mermaid
graph TB
    subgraph "N8N Built-in"
        EXEC[Execution Logs]
        ERRORS[Error Tracking]
    end
    
    subgraph "Streamlit Dashboard"
        STATS[Processing Stats]
        HEALTH[System Health]
    end
    
    subgraph "Docker"
        LOGS[Container Logs<br/>docker-compose logs]
    end
```

**Monitoring Commands:**
```bash
# View N8N logs
docker-compose logs -f n8n

# View Python service logs
docker-compose logs -f python-services

# View Streamlit logs
docker-compose logs -f streamlit

# Check system status
docker-compose ps
```

---

*This revised architecture provides a practical, cost-effective solution that can be deployed locally and scaled to cloud when needed.*
