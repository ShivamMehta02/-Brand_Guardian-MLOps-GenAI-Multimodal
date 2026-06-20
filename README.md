# 🛡️ Brand Guardian AI

> **Azure Multi-modal Compliance Ingestion Engine using LangGraph**

Brand Guardian AI is an intelligent video compliance auditing platform that leverages LangGraph, Azure OpenAI, Azure AI Search, and Azure Video Indexer to automatically audit YouTube video content against brand compliance policies (FTC guidelines, YouTube ad specs, etc.).

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ENTRY POINTS                                 │
│   main.py (CLI)  ←──→  FastAPI Server (backend/src/api/server.py)  │
└──────────┬──────────────────────────┬───────────────────────────────┘
           │       Trigger Audit      │
           ▼                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATION (LangGraph)                      │
│                                                                     │
│   [START] ──→ [Video Processor] ──→ [Compliance Auditor] ──→ [END] │
│                  (yt-dlp +              (RAG + LLM)                 │
│               Azure Video Indexer)                                  │
└──────┬──────────────┬───────────────────────┬───────────────────────┘
       │              │                       │
       ▼              ▼                       ▼
┌──────────────┐ ┌──────────────┐  ┌─────────────────────┐
│ Azure Blob   │ │ Azure Video  │  │ Azure AI Search     │
│ Storage      │ │ Indexer      │  │ (Vector DB)         │
│ (temp video) │ │ (OCR +       │  │ (Policy Knowledge   │
│              │ │  Transcript) │  │  Base)               │
└──────────────┘ └──────────────┘  └─────────────────────┘
                                            │
                                            ▼
                                   ┌─────────────────┐
                                   │ Azure OpenAI    │
                                   │ (GPT-4o + text- │
                                   │  embedding-3)   │
                                   └─────────────────┘

         ┌──────────────────────────────────────────┐
         │     OBSERVABILITY                         │
         │  Azure Application Insights + LangSmith  │
         └──────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology |
|---|---|
| **Orchestration** | LangGraph (Directed Acyclic Graph) |
| **LLM** | Azure OpenAI (GPT-4o) |
| **Embeddings** | Azure OpenAI (text-embedding-3-small) |
| **Vector Store** | Azure AI Search |
| **Video Processing** | Azure Video Indexer + yt-dlp |
| **API Framework** | FastAPI + Uvicorn |
| **Observability** | Azure Monitor (OpenTelemetry) + LangSmith |
| **Containerization** | Docker |
| **Serverless** | Azure Functions |

---

## ✨ Features

### 🎥 Video Compliance Auditing
- Downloads YouTube videos via `yt-dlp`
- Uploads to Azure Video Indexer for speech-to-text transcription and OCR extraction
- Runs multi-modal analysis (audio transcript + on-screen text)

### 📚 RAG-Powered Policy Lookup
- Ingests regulatory PDFs (FTC Influencer Guide, YouTube Ad Specs) into Azure AI Search
- Performs similarity search to retrieve relevant compliance rules
- Grounds LLM responses in actual policy documents to reduce hallucination

### 🤖 AI Compliance Auditor
- Uses GPT-4o as a "Senior Brand Compliance Auditor"
- Identifies violations with structured output (category, severity, description)
- Generates PASS/FAIL status and detailed compliance reports

### 📊 Observability
- Full request tracing via Azure Application Insights
- LangSmith integration for LLM call debugging
- Structured logging throughout the pipeline

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/)** package manager (recommended) or pip
- **Azure Subscription** with the following services provisioned:
  - Azure OpenAI (GPT-4o + text-embedding-3-small deployments)
  - Azure AI Search
  - Azure Video Indexer
  - Azure Blob Storage
  - Azure Application Insights (optional)

### 1. Clone & Install

```bash
# Clone the repository
git clone <repository-url>
cd Brand_Guardian/Brand_Guardian/ComplianceQAPipeline

# Install dependencies with uv
uv sync

# Or with pip
pip install -r azure_functions/requirements.txt
```

### 2. Configure Environment

Copy the `.env` template and fill in your Azure credentials:

```bash
cp .env .env.local
```

Required environment variables:

```env
# Azure OpenAI
AZURE_OPENAI_API_KEY="your-key"
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_API_VERSION="2024-02-01"
AZURE_OPENAI_CHAT_DEPLOYMENT="gpt-4o"
AZURE_OPENAI_EMBEDDING_DEPLOYMENT="text-embedding-3-small"

# Azure AI Search
AZURE_SEARCH_ENDPOINT="https://your-search.search.windows.net"
AZURE_SEARCH_API_KEY="your-key"
AZURE_SEARCH_INDEX_NAME="brand-guardian-index"

# Azure Video Indexer
AZURE_VI_NAME="your-vi-resource"
AZURE_VI_LOCATION="eastus"
AZURE_VI_ACCOUNT_ID="your-account-id"
AZURE_SUBSCRIPTION_ID="your-subscription-id"
AZURE_RESOURCE_GROUP="your-resource-group"

# Observability (optional)
APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=..."
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY="your-langsmith-key"
LANGCHAIN_PROJECT="brand-guardian"
```

### 3. Index the Knowledge Base

Load the compliance PDFs into Azure AI Search:

```bash
uv run python backend/scripts/index_documents.py
```

### 4. Run the Application

**Option A: CLI Mode** (single audit)
```bash
uv run python main.py
```

**Option B: API Server** (production)
```bash
uv run uvicorn backend.src.api.server:app --reload
```

Then visit:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

**Option C: Docker**
```bash
cd backend
docker build -t brand-guardian .
docker run -p 8000:8000 --env-file ../.env brand-guardian
```

### 5. Submit an Audit Request

```bash
curl -X POST http://localhost:8000/audit \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://youtu.be/dT7S75eYhcQ"}'
```

---

## 📁 Project Structure

```
ComplianceQAPipeline/
├── .env                            # Environment variables (Azure keys)
├── .gitignore                      # Git ignore rules
├── .python-version                 # Python 3.12
├── main.py                         # CLI entry point
├── pyproject.toml                  # Project metadata & dependencies
├── uv.lock                         # Locked dependency versions
├── README.md                       # This file
│
├── backend/
│   ├── Dockerfile                  # Container definition
│   ├── data/
│   │   ├── 1001a-influencer-guide-508_1.pdf   # FTC Influencer Guide
│   │   └── youtube-ad-specs.pdf               # YouTube Ad Specifications
│   ├── scripts/
│   │   ├── index_documents.py      # PDF → Azure AI Search indexer
│   │   └── explanation.txt         # Indexing process explanation
│   ├── src/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── server.py           # FastAPI application (POST /audit)
│   │   │   └── telemetry.py        # Azure Monitor OpenTelemetry setup
│   │   ├── graph/
│   │   │   ├── __init__.py
│   │   │   ├── nodes.py            # LangGraph nodes (Indexer + Auditor)
│   │   │   ├── state.py            # Graph state schema (VideoAuditState)
│   │   │   └── workflow.py         # DAG definition (START → Indexer → Auditor → END)
│   │   └── services/
│   │       ├── __init__.py
│   │       └── video_indexer.py    # Azure Video Indexer + yt-dlp integration
│   └── tests/                      # Test directory
│
├── azure_functions/
│   ├── function_app.py             # Azure Functions app definition
│   ├── host.json                   # Functions host configuration
│   ├── local.settings.json         # Local dev settings
│   └── requirements.txt            # Azure Functions dependencies
│
└── .venv/                          # Virtual environment (auto-generated)
```

---

## 🔄 Workflow: How an Audit Works

```
1. Client sends POST /audit with {"video_url": "https://youtu.be/..."}

2. FastAPI receives request → validates → generates session ID

3. LangGraph workflow executes:

   ┌──────────────────────────────────────────────────┐
   │  NODE 1: INDEXER                                  │
   │  • Downloads YouTube video (yt-dlp)               │
   │  • Uploads to Azure Video Indexer                 │
   │  • Waits for processing (polls every 30s)         │
   │  • Extracts: transcript + OCR text + metadata     │
   └──────────────────────┬───────────────────────────┘
                          │
                          ▼
   ┌──────────────────────────────────────────────────┐
   │  NODE 2: COMPLIANCE AUDITOR                       │
   │  • Queries Azure AI Search (RAG retrieval)        │
   │  • Retrieves top-3 matching compliance rules      │
   │  • Sends to GPT-4o with structured prompt         │
   │  • Parses JSON response (violations + status)     │
   └──────────────────────┬───────────────────────────┘
                          │
                          ▼
   ┌──────────────────────────────────────────────────┐
   │  RESPONSE                                         │
   │  {                                                │
   │    "session_id": "...",                           │
   │    "status": "FAIL",                              │
   │    "compliance_results": [...violations...],      │
   │    "final_report": "Summary of findings..."       │
   │  }                                                │
   └──────────────────────────────────────────────────┘
```

---

## 📜 License

This project is for educational and internal use.

---

## 🙏 Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) — Graph-based LLM orchestration
- [Azure OpenAI Service](https://azure.microsoft.com/en-us/products/ai-services/openai-service) — GPT-4o and embeddings
- [Azure AI Search](https://azure.microsoft.com/en-us/products/ai-services/ai-search) — Vector database
- [Azure Video Indexer](https://azure.microsoft.com/en-us/products/ai-video-indexer) — Video analysis
- [FastAPI](https://fastapi.tiangolo.com/) — Modern Python web framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — YouTube video downloader

---

## 🏗️ Production Rollout (`infra/production-rollout` branch)

This branch introduces pre-deployment checklists, CI/CD, and Containerization to ensure the codebase is strictly production-ready.

### 1. Dockerization
The project includes a highly optimized, multi-stage `Dockerfile` in the root directory. 
- **Stage 1 (Builder):** Uses `uv` to resolve and install dependencies into a virtual environment.
- **Stage 2 (Runner):** Uses a minimal `python:3.11-slim` base image, copying only the compiled environment and application code. This reduces attack surface and final image size.

### 2. CI/CD Pipeline
A GitHub Actions workflow (`.github/workflows/ci.yml`) is configured to:
- Enforce code quality via `flake8` linting.
- Prevent regressions by running the unit test suite (`test_workflow.py`).
- Perform an automated "Smoke Test" by starting the FastAPI server in the background and hitting the `/health` endpoint before allowing a merge.

### 3. "Guilty Until Proven Innocent" Audits
- **Dependency Audit:** Checked `requirements.txt` to ensure no hallucinated or vulnerable packages exist.
- **Secrets Management:** Ensured all credentials and API keys are strictly loaded via environment variables (`os.getenv()`) and nothing is hardcoded.
- **Code Cleanliness:** Removed zombie code and added business logic comments detailing *why* architectural decisions (like multi-tenant filtering in Azure Search) were made.

---

## 🌐 Live Portfolio Deployment (`render.yaml` & `vercel.json`)

The application is configured for **Zero-Cost Live Deployment** to showcase to recruiters.

1. **Frontend (Vercel):** The Vite React app can be imported directly into Vercel. `vercel.json` ensures React Router works correctly.
2. **Backend (Render.com):** The FastAPI Python backend deploys to Render's free tier via `render.yaml`.
3. **Safe-Guard (Demo Mode):** The backend is deployed with `DEMO_MODE=true`. This completely bypasses the expensive Azure/OpenAI LangGraph workflow, returning a realistic, instant mock report instead. This guarantees your portfolio costs $0 in API fees while recruiters test it.

> **Note on Render Free Tier:** Render spins down free instances after 15 minutes of inactivity. The first time a recruiter hits "Run Audit", it may take ~30 seconds for the backend to wake up from a cold start. Subsequent requests are instant.
