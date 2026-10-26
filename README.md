# CloudFinOps AI — Cloud Cost Intelligence & Optimization Platform

> **Portfolio Project tailored for Entry-Level Cloud FinOps Analyst Role**  
> *Demonstrating Cloud Financial Management principles aligned with the FinOps Foundation Framework (Inform, Optimize, Operate).*

---

## 📌 Executive Summary
**CloudFinOps AI** is an interactive, enterprise-grade cloud financial intelligence and governance platform designed to provide complete visibility, unit economic accountability, anomaly triage, and rightsizing governance across multi-cloud environments.

Built using **Python, Pandas, SQLite, Plotly, and Streamlit**, the system simulates a real enterprise cloud environment with 6+ months of historical multi-service telemetry, budget allocations, resource wastage patterns, and generative AI (LLM) token consumption metrics.

> **Transparency Notice:** All billing, resource, and token metrics are generated synthetically for portfolio, demonstration, and interview evaluation purposes. The application does not require AWS/Azure/GCP credentials or paid API keys. Forecasts and recommendations are labeled as estimates.

---

## 🚀 Core Features

| Feature Module | FinOps Domain | Description |
| :--- | :--- | :--- |
| **1. Executive Cost Dashboard** | *Inform Phase* | Real-time cloud spend tracking, MoM change %, 7-day rolling moving averages, dimensional spend distributions by service, team, and environment. |
| **2. Cost Allocation & Tag Hygiene** | *Inform Phase* | Evaluates mandatory tag compliance (`Team`, `Application`, `Owner`), exposes untagged "ghost" spend, and surfaces unallocated exposure per service. |
| **3. Budget & Predictive Forecasting** | *Inform & Operate* | Monthly budget vs actual variance analysis ($ and %), status categorization (`Over Budget`, `Near Limit`, `On Track`), and next-month EWMA cost forecasting with 90% confidence bands. |
| **4. Cost Anomaly Detection** | *Operate Phase* | Statistical surge detection (> 2.5 standard deviations above 14-day rolling baseline) with automatic root-cause diagnosis annotations. |
| **5. Cost Optimization Engine** | *Optimize Phase* | Identifies simulated idle/underutilized instances, unattached EBS storage, overprovisioned Lambda memory, and idle database replicas with estimated monthly savings. |
| **6. AI FinOps (GenAI Accountability)** | *Unit Economics* | Analyzes simulated LLM/API usage across OpenAI and Amazon Bedrock, prompt/completion token ratios, cost per 1,000 requests, and application attribution. |
| **7. Savings Realization Tracker** | *Governance* | Strict lifecycle separation of **Potential**, **Approved**, **Implemented**, and **Realized** savings, ensuring estimates are never conflated with realized cash savings. |
| **8. Exportable Executive Reports** | *Governance* | Downloadable, audit-ready CSV exports for daily spend breakdowns, budget variance, detected anomalies, and rightsizing opportunities. |

---

## 🏗️ Architecture & Technology Stack

```
   ┌─────────────────────────────────────────────────────────────┐
   │                   Streamlit Web Dashboard                  │
   │               (Interactive Filters & Tabs)                  │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
          ┌───────────────────────┴───────────────────────┐
          ▼                                               ▼
   ┌──────────────────────────────┐        ┌──────────────────────────────┐
   │      Plotly Visualizations    │        │       FinOps Analytics       │
   │   (Trends, Pies, Funnels)    │        │            Engine            │
   └──────────────────────────────┘        └──────────────┬───────────────┘
                                                          │
                                                          ▼
                                           ┌──────────────────────────────┐
                                           │        SQLite Database        │
                                           │  (cloud_billing, budgets,    │
                                           │   optimization, ai_usage)    │
                                           └──────────────────────────────┘
```

- **Backend Logic & Data Manipulation:** Python 3.10+, Pandas, NumPy
- **Persistence Layer:** Embedded SQLite 3 (`data/cloudfinops.db`)
- **Interactive UI & Presentation:** Streamlit (v1.35+)
- **Data Visualizations:** Plotly Express & Plotly Graph Objects
- **Testing Suite:** Pytest

---

## 📂 Project Structure

```
cloudfinops-ai/
├── app.py                      # Main Streamlit dashboard application
├── requirements.txt            # Python dependencies
├── run.bat                     # Windows cmd double-click launcher
├── run.ps1                     # PowerShell launch script
├── README.md                   # Complete documentation & interview guide
├── data/
│   └── cloudfinops.db          # Embedded SQLite database (auto-generated)
├── src/
│   ├── __init__.py
│   ├── database.py             # Schema definition & synthetic data generator
│   └── finops_engine.py        # Core FinOps business logic & KPIs
└── tests/
    ├── __init__.py
    └── test_finops_engine.py   # Comprehensive unit test suite
```

---

## ⚡ Quickstart & Setup Instructions (Windows)

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13 installed on Windows.

### Option A: One-Click Launch (Recommended)
Simply right-click or double-click:
```powershell
.\run.ps1
```
or run `run.bat` in Command Prompt.

### Option B: Manual Terminal Execution
1. Navigate to the project directory:
   ```powershell
   cd C:\Users\kushi\.gemini\antigravity\scratch\cloudfinops-ai
   ```
2. (Optional) Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Initialize the SQLite database and seed synthetic records:
   ```powershell
   python src/database.py
   ```
5. Launch the Streamlit dashboard:
   ```powershell
   streamlit run app.py
   ```
6. Open your browser at `http://localhost:8501`.

---

## 🧪 Running the Unit Tests

The test suite validates cost KPI calculations, budget variance rules, tag hygiene calculations, statistical anomaly detection, and the strict isolation of realized savings.

To execute tests:
```powershell
python -m pytest tests -v
```
**Test Results:**
```
tests/test_finops_engine.py::test_calculate_cost_kpis PASSED             [ 12%]
tests/test_finops_engine.py::test_calculate_cost_kpis_empty PASSED       [ 25%]
tests/test_finops_engine.py::test_analyze_tag_compliance PASSED          [ 37%]
tests/test_finops_engine.py::test_calculate_budget_variance PASSED       [ 50%]
tests/test_finops_engine.py::test_generate_monthly_forecast PASSED       [ 62%]
tests/test_finops_engine.py::test_detect_cost_anomalies PASSED           [ 75%]
tests/test_finops_engine.py::test_calculate_savings_breakdown PASSED     [ 87%]
tests/test_finops_engine.py::test_analyze_ai_usage PASSED                [100%]
============================== 8 passed in 1.60s ==============================
```

---

## 📊 Sample Insights Produced by the Platform

1. **Tag Hygiene Deficit:** Over **12%** of cloud spend lacked explicit `Owner` attribution and **15%** lacked `Application` tags, introducing unallocated overhead in shared EKS and S3 buckets.
2. **Budget Variance Triage:** In October 2026, the **Data Science** team exceeded their \$8,000 budget by **18.7%** due to unoptimized Spark batch nodes running on On-Demand instances instead of Spot.
3. **Automated Anomaly Capture:** Identified a +320% spike in **Amazon RDS** database spending between July 14–18, caused by an unindexed query runaway across development read replicas.
4. **AI Unit Economics:** Identified that while `gpt-4o` accounts for only 24% of GenAI requests, it drove 68% of total AI spend. Switching summarization tasks to `gpt-4o-mini` cuts token expenditures by ~60%.
5. **Verified Savings Separation:** Identified \$1,118/month in potential rightsizing savings, but strictly credited only \$139/month as **Realized** following confirmed engineering validation.

---

## ⚠️ Limitations & Governance Disclosure
- **Synthetic Data:** All billing line items, resource utilization stats, and LLM token counts are generated algorithmically.
- **No Direct Cloud Writes:** This platform operates on billing feeds and read replicas; it does not execute destructive terminate API calls directly against cloud providers.
- **Estimation Disclosures:** All rightsizing recommendations and EWMA forecasting projections represent statistical estimates and require human FinOps validation prior to architectural execution.
