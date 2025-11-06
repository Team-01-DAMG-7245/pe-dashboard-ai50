# Forbes AI 50 - PE Dashboard (Project ORBIT)

Automated data pipeline for scraping and analyzing Forbes AI 50 companies for private equity intelligence.

---

## Quick Start

### Run Airflow (Docker)
```bash
docker compose up
# Access UI: http://localhost:8080 (admin/admin)
```

### Run App Locally (Dev)
```bash
python -m venv airflow_env
source airflow_env/bin/activate
pip install -r requirements.txt
uvicorn src.api:app --reload        # http://localhost:8000
streamlit run src/streamlit_app.py  # http://localhost:8501
```

---

## Project Structure

```
├── dags/                  # Airflow DAGs (Labs 2-3)
├── data/
│   ├── forbes_ai50_seed.json   # Company list (Lab 0)
│   ├── raw/                     # Scraped HTML/text (Lab 1)
│   ├── structured/              # Pydantic models (Lab 5)
│   └── payloads/                # Dashboard payloads (Lab 6)
├── src/
│   ├── api.py                   # FastAPI endpoints (Lab 7-8)
│   ├── models.py                # Pydantic schemas (Lab 5)
│   ├── s3_utils.py              # Cloud storage (Lab 1)
│   └── streamlit_app.py         # Dashboard UI (Lab 10)
├── requirements.txt
├── docker-compose.yml
└── README.md
```

---

## Setup

### 1. AWS S3 Configuration
```bash
aws configure  # Enter your credentials
export AWS_BUCKET_NAME=quanta-ai50-data
```

### 2. Seed File
Populate `data/forbes_ai50_seed.json` with Forbes AI 50 companies from https://www.forbes.com/lists/ai50/

### 3. Environment Variables
Create `.env`:
```bash
AWS_BUCKET_NAME=quanta-ai50-data
OPENAI_API_KEY=your-api-key-here
```

---

## Running Labs 4-9

### Prerequisites

1. **Create `.env` file** in project root with:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

**Note:** All scripts automatically load API keys from `.env` file. No need to set environment variables manually.

### Step 1: Lab 4 - Vector DB & RAG Index

**Build Vector DB Index:**
```powershell
python src\lab4\index_for_rag_all.py
```

**Expected Output:** Vector DB should have 294+ chunks indexed.

**Verify:**
```powershell
Get-ChildItem data\vector_db -Recurse | Measure-Object
```

### Step 2: Lab 5 - Structured Extraction

**Extract Structured Data:**
```powershell
python src\lab5\structured_extraction.py
```

**Expected Output:** At least 5 companies with structured data in `data/structured/`.

**Verify:**
```powershell
Get-ChildItem data\structured -Filter *.json | Measure-Object
```

### Step 3: Lab 6 - Payload Assembly

**Assemble Payloads:**
```powershell
python src\lab6\assemble_payloads.py
```

**Expected Output:** Payloads assembled for all companies with structured data in `data/payloads/`.

**Verify:**
```powershell
Get-ChildItem data\payloads -Filter *.json | Measure-Object
```

### Step 4: Lab 7 & 8 - Dashboard API

**Start API Server:**
```powershell
.\start_api_server.ps1
```

**Note:** Make sure you have a `.env` file in the project root with:
```
OPENAI_API_KEY=your-api-key-here
```

The server will start on `http://localhost:8002`

**Access API:**
- **Swagger UI**: http://localhost:8002/docs (Interactive API testing)
- **Health Check**: http://localhost:8002/health
- **RAG Dashboard**: `POST http://localhost:8002/dashboard/rag`
- **Structured Dashboard**: `POST http://localhost:8002/dashboard/structured`

**Test API Endpoints in Swagger UI:**

1. **Lab 7 - RAG Dashboard** (`POST /dashboard/rag`):
   - Open http://localhost:8002/docs in your browser
   - Click on `POST /dashboard/rag` endpoint
   - Click "Try it out"
   - Enter JSON:
   ```json
   {
     "company_id": "anthropic",
     "top_k": 10
   }
   ```
   - Click "Execute"

2. **Lab 8 - Structured Dashboard** (`POST /dashboard/structured`):
   - Click on `POST /dashboard/structured` endpoint
   - Click "Try it out"
   - Enter JSON:
   ```json
   {
     "company_id": "anthropic"
   }
   ```
   - Click "Execute"

**Expected Output:**
- Lab 7: Generates 8-section dashboard using RAG pipeline with "Not disclosed." for missing data
- Lab 8: Generates 8-section dashboard using structured payload (more precise, no "Missing Key Information" in Disclosure Gaps)

### Step 5: Lab 9 - Evaluation & Comparison

**Generate Evaluation Dashboards:**

Open a **NEW** PowerShell terminal (keep the API server running) and run:

```powershell
.\run_lab9.ps1
```

**Note:** Make sure you have a `.env` file in the project root with your `OPENAI_API_KEY`.

**Output:** 
- Dashboards saved in `src/lab9/evaluation_output/` directory
- Generates both RAG and Structured dashboards for all companies with payloads

**Fill Evaluation:**
- Review dashboards in `src/lab9/evaluation_output/`
- Fill out `src/lab9/EVAL.md` with rubric scores (0-10 points per company)
- Complete comparison of RAG vs Structured methods

**Expected Output:** `EVAL.md` with rubric and scores for all companies with payloads.

---

## Labs Progress

### ✅ Lab 0: Project Bootstrap
- Repository structure with `dags/`, `data/`, `src/`
- `forbes_ai50_seed.json` with all 50 companies

### ✅ Lab 1: Scrape & Store
- Python scraper for homepage, about, product, careers, blog
- Stores raw HTML + clean text locally
- Uploads to S3: `s3://quanta-ai50-data/ai50/raw/`

### ✅ Lab 2: Full Load Airflow DAG
- `ai50_full_ingest_dag.py` - scrapes all 50 companies
- Schedule: `@once` (manual trigger)
- Output: `data/raw/<company_id>/initial/` + S3

### ✅ Lab 3: Daily Refresh Airflow DAG
- `ai50_daily_refresh_dag.py` - daily updates
- Schedule: `0 3 * * *` (3 AM UTC)
- Tracks changes with content hashing
- Creates dated subfolders per run

### ✅ Lab 4: Vector DB & RAG Index
- Chunk text into 500-1000 tokens
- Embed and store in vector DB (ChromaDB)
- FastAPI endpoint: `/rag/search` (Lab 4 API on port 8001)

### ✅ Lab 5: Structured Extraction (Pydantic)
- Use `instructor` library with LLM
- Extract: Company, Event, Snapshot, Product, Leadership, Visibility
- Output: `data/structured/<company_id>.json`

### ✅ Lab 6: Payload Assembly
- Combine all structured data into dashboard payload
- Output: `data/payloads/<company_id>.json`
- Validation: All payloads can be loaded by `src/structured_pipeline.py`

### ✅ Lab 7: RAG Pipeline Dashboard
- Endpoint: `POST /dashboard/rag`
- Vector DB → LLM → 8-section Markdown dashboard
- Uses "Not disclosed." for missing data

### ✅ Lab 8: Structured Pipeline Dashboard
- Endpoint: `POST /dashboard/structured`
- Pydantic payload → LLM → Markdown dashboard
- More precise and less hallucinatory than RAG

### ✅ Lab 9: Evaluation & Comparison
- Compare RAG vs Structured for 5+ companies
- Rubric: factual correctness, schema adherence, hallucination control
- Output: `EVAL.md` with scores and findings

### 🔄 Lab 10: Dockerize FastAPI + Streamlit
- `docker-compose.yml` for app layer
- FastAPI: http://localhost:8000
- Streamlit: http://localhost:8501

### 🔄 Lab 11: DAG ↔ App Integration
- Daily DAG writes to `data/payloads/`
- App reads from payloads for dashboard generation

---

## Key Commands

```bash
# Airflow
docker compose up               # Start Airflow
docker compose down             # Stop Airflow
docker compose logs -f          # View logs

# Check S3
aws s3 ls s3://quanta-ai50-data/ai50/raw/

# Check scraped data
ls data/raw/ | wc -l           # Count companies scraped

# Labs 4-9 - Complete Sequence
# Step 1: Lab 4 - Vector DB Index
python src\lab4\index_for_rag_all.py

# Step 2: Lab 5 - Structured Extraction
python src\lab5\structured_extraction.py

# Step 3: Lab 6 - Payload Assembly
python src\lab6\assemble_payloads.py

# Step 4: Lab 7/8 - Start API Server (run in separate terminal)
.\start_api_server.ps1

# Step 5: Lab 9 - Evaluation (in new terminal, after API is running)
.\run_lab9.ps1
```

---

## Troubleshooting

**DLL Errors (Windows):**
- Install Visual C++ Redistributables: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Restart terminal after installation

**API Not Starting:**
- Check if port 8002 is available
- Verify `.env` file has `OPENAI_API_KEY` set
- Ensure virtual environment is activated

**Vector DB Empty:**
- Run `python src\index_for_rag_all.py` to populate vector DB
- Check that `data/raw/` contains company directories

**Docker Issues:**
- Ensure Docker Desktop is running
- Check `docker-compose.yml` configuration
- View logs: `docker compose logs -f`

---

## Deliverables

- [x] GitHub repo: `pe-dashboard-ai50`
- [x] Working Airflow DAGs (Lab 2-3)
- [x] FastAPI with `/dashboard/rag`, `/dashboard/structured`
- [x] Vector DB with ChromaDB (Lab 4)
- [x] Structured extraction with Pydantic (Lab 5)
- [x] Payload assembly and validation (Lab 6)
- [x] RAG pipeline dashboard (Lab 7)
- [x] Structured pipeline dashboard (Lab 8)
- [x] `EVAL.md` comparing RAG vs Structured (5+ companies) (Lab 9)
- [ ] Streamlit UI with company dropdown → dashboard
- [ ] Docker for FastAPI + Streamlit
- [ ] Demo video ≤10 mins
- [ ] Contribution attestation
