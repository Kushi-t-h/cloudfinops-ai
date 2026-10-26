# CloudFinOps AI — Cloud Cost Intelligence & Optimization Platform

**A portfolio project tailored for an Entry-Level Cloud FinOps Analyst role.**

CloudFinOps AI is an interactive cloud cost analytics and optimization dashboard built with Python, Streamlit, Pandas, SQLite, and Plotly. It demonstrates cloud financial management practices aligned with the FinOps Foundation's **Inform, Optimize, and Operate** framework.

> **Data transparency:** This project uses synthetic cloud billing, resource, budget, and AI usage data. Forecasts, anomaly baselines, and savings figures are illustrative estimates, not measurements from a real cloud account.

## Overview

CloudFinOps AI helps users explore cloud spending, allocate costs to teams and applications, monitor budgets, identify unusual spending patterns, and evaluate optimization opportunities through an interactive dashboard.

The application includes global filters for billing periods, cloud services, teams, and environments. Users can investigate how filtering affects dashboard metrics and download supported analytical results.

## Key Features

### 1. Executive Cost Dashboard
- Cloud spending overview and average daily run rate.
- Month-over-month spending changes.
- Budget utilization indicators.
- Spending breakdowns by service, team, and environment.

### 2. Cost Allocation & Tag Compliance
- Evaluates mandatory Team, Application, and Owner tags.
- Calculates tag compliance and allocated spending.
- Identifies missing-tag and unallocated spending.
- Highlights services contributing to unallocated cost exposure.

### 3. Budget Tracking & Forecasting
- Compares monthly budgets with actual spending.
- Calculates remaining budget and actual-versus-budget variance percentages.
- Classifies budget status, including On Track, Near Limit, and Over Budget.
- Estimates next-month spending using an exponentially weighted moving average (EWMA).
- Displays an estimated forecast range.

### 4. Cost Anomaly Detection
- Identifies unusual spending spikes against a historical baseline.
- Displays detected incidents, excess spending, and severity.
- Provides rule-based root-cause explanations to support investigation.

### 5. Cost Optimization & Rightsizing
- Highlights simulated idle or underutilized resources.
- Includes examples such as unattached storage, oversized compute resources, and idle database replicas.
- Estimates potential monthly savings by resource or service.
- Supports prioritization of optimization opportunities.

### 6. AI FinOps — GenAI Cost Transparency
- Analyzes simulated AI model and API usage.
- Tracks input and output tokens, API invocations, and model-level spending.
- Compares spending across models, providers, and consuming applications.
- Calculates cost per 1,000 requests.

### 7. Savings Realization Tracker
Tracks optimization initiatives through four distinct stages:

1. **Potential:** Estimated savings identified.
2. **Approved:** Savings initiatives accepted for implementation.
3. **Implemented:** Changes reported as implemented and awaiting validation.
4. **Realized:** Savings recorded as verified in the simulated workflow.

Potential savings are not treated as realized savings. In a real FinOps environment, realized savings should be validated against actual billing data after implementation.

### 8. Exportable Reports
Provides CSV exports for supported analytical views, including budget variance, spending analysis, anomalies, and optimization opportunities.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Dashboard | Streamlit |
| Data processing | Pandas, NumPy |
| Database | SQLite |
| Visualization | Plotly |
| Testing | Pytest |
| Version control | Git and GitHub |

## Architecture

```text
                 User
                  |
                  v
        Streamlit Dashboard
     Global Filters and Tabs
                  |
                  v
       FinOps Analytics Engine
         Python + Pandas
                  |
       +----------+-----------+
       |          |           |
       v          v           v
   Cost KPIs   Budgets &    Anomalies &
   Allocation  Forecasting  Optimization
       |          |           |
       +----------+-----------+
                  |
                  v
           SQLite Database
      Billing, Budgets, Resources,
          and AI Usage Data
                  |
                  v
        Plotly Visualizations
        and CSV Downloads
```

## Project Structure

```text
cloudfinops-ai/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── run.bat
├── run.ps1
├── data/
│   └── cloudfinops.db       # Generated locally; not committed
├── src/
│   ├── __init__.py
│   ├── database.py
│   └── finops_engine.py
└── tests/
    ├── __init__.py
    └── test_finops_engine.py
```

## Getting Started

### Prerequisites

- Python 3.11 recommended.
- Git, if cloning the repository.
- Internet access to install Python dependencies.

### 1. Clone the repository

```powershell
git clone https://github.com/Kushi-t-h/cloudfinops-ai.git
cd cloudfinops-ai
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use the following command for the current terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Initialize the database

If the database has not been created, run:

```powershell
python src/database.py
```

This should create and populate the local SQLite database if the database initialization script is designed to do so. Avoid rerunning initialization if it resets existing records.

### 5. Start the dashboard

```powershell
streamlit run app.py
```

Open the local URL displayed in your terminal, usually:

`http://localhost:8501`

### Windows launcher scripts

The project also includes `run.bat` and `run.ps1` for launching the application on Windows. Use these after verifying that their setup and launch commands match your local environment.

## Running Tests

Run the test suite from the project root:

```powershell
python -m pytest tests -v
```

The latest reported test run completed successfully with **13 passed**.

The tests cover:

- Cloud cost KPI calculations.
- Empty-input handling.
- Mandatory tag compliance.
- Budget variance calculations.
- Monthly forecasting and edge cases.
- Cost anomaly detection.
- Savings breakdown calculations.
- AI usage analytics and service-filter behavior.

To reproduce the results, run the test command in your own environment. Test counts may change as the project evolves.

## Using the Dashboard

1. Launch the application.
2. Set the billing period in the sidebar.
3. Select one or more cloud services, teams, and environments.
4. Open each dashboard tab to inspect the corresponding analysis.
5. Compare budget and actual spending.
6. Review detected anomalies and investigate their explanations.
7. Examine optimization opportunities and estimated savings.
8. Review AI model usage and cost metrics.
9. Explore savings lifecycle stages and export available reports.

**Tip:** Change one global filter at a time to understand how the selected service, team, or environment affects the displayed metrics.

## FinOps Concepts Demonstrated

- Cloud cost visibility and reporting.
- Cost allocation, tagging, and ownership.
- Budget monitoring and variance analysis.
- Spending forecasting.
- Cost anomaly detection and triage.
- Resource utilization and rightsizing opportunities.
- GenAI cost attribution and unit economics.
- Savings governance and realization tracking.

## Limitations & Governance

- **Synthetic data:** The application does not represent actual AWS, Azure, or Google Cloud billing records.
- **No live cloud integration:** Cloud provider credentials and live billing APIs are not required.
- **Estimated forecasts:** Forecasts depend on the available simulated historical data and assumptions.
- **Simulated anomaly explanations:** Root-cause descriptions are analytical hypotheses, not verified production incidents.
- **Estimated optimization savings:** Recommendations require engineering review and validation before implementation.
- **No direct resource modification:** The application does not terminate, resize, or modify real cloud resources.
- **Simulated savings verification:** The savings lifecycle demonstrates governance concepts; it does not independently audit real invoices.

## Future Enhancements

- Integrate AWS Cost and Usage Reports or equivalent cloud billing exports.
- Add support for Azure and Google Cloud billing datasets.
- Introduce configurable budgets and cost anomaly thresholds.
- Improve forecast evaluation using historical holdout data.
- Add role-based access control and audit logging.
- Integrate validated resource utilization metrics for more accurate optimization recommendations.
- Add unit-cost KPIs for business services and AI workloads.

## Author

**Kushi T H**

Computer Science and Data Science Engineering Student  
CMR Institute of Technology, Bengaluru

GitHub: https://github.com/Kushi-t-h

---

*CloudFinOps AI is an educational portfolio project intended to demonstrate practical cloud financial management, data analytics, dashboard development, and FinOps governance concepts.*
