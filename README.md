# Project ORBIT — PE Dashboard for Forbes AI 50

This is the starter package for **Assignment 2 — DAMG7245**.

## Run locally (dev)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.api:app --reload
# in another terminal
streamlit run src/streamlit_app.py
```

## Docker (app layer only)

```bash
cd docker
docker compose up --build
```

This starts:
- FastAPI: http://localhost:8000
- Streamlit: http://localhost:8501

# Add instructions on running on the cloud based on your setup and links to Codelabs, architecture diagrams etc.

---

# Lab 0 — Project Bootstrap & AI 50 Seed

## How to Implement

### 1. Install Dependencies

Navigate to the Lab0 directory and install the required packages:

```bash
cd src/Lab0
pip install -r requirements.txt
```

**Note:** If using Selenium, ensure ChromeDriver is installed:
- Download ChromeDriver from https://chromedriver.chromium.org/
- Add it to your system PATH, or
- Use `webdriver-manager` package (optional) for automatic driver management

### 2. Run the Scraper

Execute the scraper script to fetch and populate the Forbes AI 50 data:

```bash
python scrape_forbes_ai50.py
```

This will:
- Fetch data from https://www.forbes.com/lists/ai50/
- Parse company information
- Save results to `../../data/forbes_ai50_seed.json`

### 3. Verify Output

Check that the seed file was created:

```bash
ls ../../data/forbes_ai50_seed.json
```

The JSON file should contain 50 company entries with the following schema:

```json
[
  {
    "rank": 1,
    "company_name": "Company Name",
    "description": "Brief description",
    "industry": "Industry sector",
    "location": "Headquarters location",
    "year_founded": 2020,
    "funding": "$100M",
    "valuation": "$1B"
  }
]
```

### 4. Troubleshooting

**If the scraper creates template data instead of real data:**

1. Forbes website may use JavaScript rendering that requires Selenium
2. Website structure may have changed
3. Check if ChromeDriver is properly installed and accessible

**Manual Fallback:**
If automated scraping fails, manually populate `data/forbes_ai50_seed.json` with data from https://www.forbes.com/lists/ai50/

### Checkpoint

After successful implementation:
- ✅ `data/forbes_ai50_seed.json` exists
- ✅ File contains 50 company entries
- ✅ All required fields are populated (rank, company_name at minimum)