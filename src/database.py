import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cloudfinops.db")

def get_connection(db_path=None):
    if db_path is None:
        db_path = DB_PATH
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    return conn

def generate_synthetic_data(seed=42):
    """
    Generates realistic, internally consistent synthetic billing and usage data
    covering the last 6 months (May 2026 to October 2026).
    Disclosed: All data is synthetic and generated for demonstration/portfolio purposes.
    """
    np.random.seed(seed)
    
    # Dates spanning 180 days up to late Oct 2026
    end_date = datetime(2026, 10, 25)
    start_date = end_date - timedelta(days=180)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    services = [
        ("Amazon EC2", "Compute", 120.0, 30.0),
        ("Amazon S3", "Storage", 45.0, 8.0),
        ("Amazon RDS", "Database", 85.0, 15.0),
        ("AWS Lambda", "Serverless", 15.0, 5.0),
        ("Amazon EKS", "Containers", 95.0, 20.0),
        ("CloudFront", "Networking", 25.0, 6.0),
        ("Amazon Bedrock", "AI/ML", 70.0, 25.0),
        ("OpenAI Azure API", "AI/ML", 90.0, 35.0)
    ]
    
    teams = ["Platform Eng", "Data Science", "E-Commerce", "Core Banking", "Security & SRE"]
    environments = ["Production", "Staging", "Development", "Sandbox"]
    owners = ["sarah.c@company.internal", "devon.m@company.internal", "amit.k@company.internal", "elena.r@company.internal", "marcus.t@company.internal"]
    applications = ["Checkout-Svc", "Recommendation-Engine", "Customer-Portal", "ETL-Pipeline", "LLM-Copilot", "Risk-Scoring"]
    
    billing_records = []
    
    for dt in date_range:
        date_str = dt.strftime("%Y-%m-%d")
        month_str = dt.strftime("%Y-%m")
        # Day of week seasonality (Mon-Fri slightly higher)
        is_weekend = dt.weekday() >= 5
        dow_factor = 0.82 if is_weekend else 1.05
        
        # Monthly growth trend: +2% per month
        day_index = (dt - start_date).days
        growth_factor = 1.0 + (day_index / 180.0) * 0.15
        
        for svc_name, category, base_cost, variance in services:
            # Generate 2 to 4 charge items per service per day across teams
            num_entries = np.random.randint(1, 4)
            for _ in range(num_entries):
                team = np.random.choice(teams)
                env = np.random.choice(environments, p=[0.55, 0.20, 0.15, 0.10])
                app = np.random.choice(applications)
                owner = np.random.choice(owners)
                
                # Tag compliance simulation (some records intentionally miss tags)
                # 8% miss team, 12% miss owner, 15% miss application
                tag_team = None if np.random.random() < 0.08 else team
                tag_owner = None if np.random.random() < 0.12 else owner
                tag_app = None if np.random.random() < 0.15 else app
                tag_env = env # Env is typically mandatory from AWS account/VPC
                
                # Base cost with noise
                raw_cost = max(2.0, np.random.normal(base_cost / num_entries, variance / 2.0))
                cost = round(raw_cost * dow_factor * growth_factor, 2)
                
                # Inject 3 controlled anomalies:
                # 1. RDS failover / unindexed query run spike in July 2026
                if svc_name == "Amazon RDS" and "2026-07-14" <= date_str <= "2026-07-18":
                    cost = round(cost * 4.2, 2)
                # 2. Bedrock LLM experiment batch spike in Sept 2026
                if svc_name == "Amazon Bedrock" and "2026-09-08" <= date_str <= "2026-09-11":
                    cost = round(cost * 5.0, 2)
                # 3. Data Science EKS worker runaway node pool in Oct 2026
                if svc_name == "Amazon EKS" and team == "Data Science" and "2026-10-12" <= date_str <= "2026-10-15":
                    cost = round(cost * 3.8, 2)
                    
                usage_amount = round(cost * np.random.uniform(1.2, 2.5), 1)
                
                billing_records.append({
                    "date": date_str,
                    "month": month_str,
                    "service": svc_name,
                    "category": category,
                    "team": tag_team,
                    "environment": tag_env,
                    "application": tag_app,
                    "owner": tag_owner,
                    "cost": cost,
                    "usage_amount": usage_amount,
                    "is_synthetic": 1
                })
                
    df_billing = pd.DataFrame(billing_records)
    
    # 2. Sample Budgets table
    months = sorted(list(df_billing["month"].unique()))
    budget_records = []
    
    # Base monthly budget ~ $25,000 to $32,000 total distributed by team
    team_budget_weights = {
        "Platform Eng": 7000,
        "Data Science": 8000,
        "E-Commerce": 6500,
        "Core Banking": 6000,
        "Security & SRE": 3500
    }
    
    for m in months:
        for t, b_amount in team_budget_weights.items():
            # Add slight budget inflation over time
            adj_b = b_amount * (1.0 + (months.index(m) * 0.02))
            budget_records.append({
                "month": m,
                "team": t,
                "budget_amount": round(adj_b, 2)
            })
    df_budgets = pd.DataFrame(budget_records)
    
    # 3. Cost Optimization recommendations (idle & underutilized resources)
    optimization_records = [
        {
            "resource_id": "i-09f481ab7c2e39110",
            "resource_name": "checkout-api-worker-03",
            "service": "Amazon EC2",
            "team": "E-Commerce",
            "environment": "Production",
            "issue_detected": "Average CPU utilization < 4.2% over 30 days (m5.4xlarge)",
            "recommended_action": "Rightsize to m5.xlarge or leverage AWS Auto Scaling group",
            "current_monthly_spend": 584.00,
            "estimated_monthly_savings": 438.00,
            "savings_confidence": "High",
            "status": "Potential"  # Potential, Approved, Implemented, Realized
        },
        {
            "resource_id": "vol-0a8177dbe10214c76",
            "resource_name": "unattached-etl-temp-vol",
            "service": "Amazon EC2 (EBS)",
            "team": "Data Science",
            "environment": "Development",
            "issue_detected": "Unattached gp3 volume (1.5 TB) inactive for 45 days",
            "recommended_action": "Create snapshot backup and delete unattached volume",
            "current_monthly_spend": 120.00,
            "estimated_monthly_savings": 120.00,
            "savings_confidence": "High",
            "status": "Approved"
        },
        {
            "resource_id": "db-qa-customer-replica",
            "resource_name": "customer-qa-db-read-replica",
            "service": "Amazon RDS",
            "team": "Core Banking",
            "environment": "Staging",
            "issue_detected": "Read replica idle with 0 connections outside business hours",
            "recommended_action": "Schedule automated nightly/weekend stop-start instances",
            "current_monthly_spend": 340.00,
            "estimated_monthly_savings": 195.00,
            "savings_confidence": "Medium",
            "status": "Implemented"
        },
        {
            "resource_id": "natgw-0561df02aa9931b01",
            "resource_name": "dev-legacy-nat-gateway",
            "service": "CloudFront / VPC",
            "team": "Platform Eng",
            "environment": "Development",
            "issue_detected": "Redundant NAT Gateway in Dev with < 100MB/month traffic",
            "recommended_action": "Consolidate into single AZ NAT gateway or route via VPC endpoints",
            "current_monthly_spend": 68.00,
            "estimated_monthly_savings": 54.00,
            "savings_confidence": "High",
            "status": "Realized"
        },
        {
            "resource_id": "s3-analytics-raw-logs-2025",
            "resource_name": "company-raw-telemetry-bucket",
            "service": "Amazon S3",
            "team": "Security & SRE",
            "environment": "Production",
            "issue_detected": "28 TB Standard tier data untouched > 90 days",
            "recommended_action": "Enable S3 Lifecycle policy to transition to Glacier Flexible Retrieval",
            "current_monthly_spend": 644.00,
            "estimated_monthly_savings": 515.00,
            "savings_confidence": "High",
            "status": "Approved"
        },
        {
            "resource_id": "eks-nodepool-spark-spot",
            "resource_name": "ds-spark-batch-ondemand",
            "service": "Amazon EKS",
            "team": "Data Science",
            "environment": "Development",
            "issue_detected": "Batch analytics workloads running 100% on On-Demand instances",
            "recommended_action": "Migrate fault-tolerant Spark worker pods to EC2 Spot Instances",
            "current_monthly_spend": 980.00,
            "estimated_monthly_savings": 680.00,
            "savings_confidence": "Medium",
            "status": "Potential"
        },
        {
            "resource_id": "lambda-heavy-memory-invoker",
            "resource_name": "invoice-pdf-generator",
            "service": "AWS Lambda",
            "team": "E-Commerce",
            "environment": "Production",
            "issue_detected": "Overprovisioned memory (3008 MB configured, max 320 MB used)",
            "recommended_action": "Rightsize Lambda memory configuration to 512 MB via AWS Compute Optimizer",
            "current_monthly_spend": 145.00,
            "estimated_monthly_savings": 85.00,
            "savings_confidence": "High",
            "status": "Realized"
        }
    ]
    df_opt = pd.DataFrame(optimization_records)
    
    # 4. AI FinOps usage records (LLM & GenAI API tracking)
    ai_models = [
        ("gpt-4o", "OpenAI Azure API", 5.00, 15.00),     # $ per 1M input / output tokens
        ("gpt-4o-mini", "OpenAI Azure API", 0.15, 0.60),
        ("claude-3-5-sonnet", "Amazon Bedrock", 3.00, 15.00),
        ("amazon-titan-text-express", "Amazon Bedrock", 0.20, 0.60),
        ("text-embedding-3-small", "OpenAI Azure API", 0.02, 0.00)
    ]
    
    ai_records = []
    # Generate daily AI telemetry across apps
    for dt in date_range:
        date_str = dt.strftime("%Y-%m-%d")
        month_str = dt.strftime("%Y-%m")
        for model_name, provider, in_rate_m, out_rate_m in ai_models:
            # 2 to 5 batch logs per day
            for _ in range(np.random.randint(1, 4)):
                team = np.random.choice(["Data Science", "E-Commerce", "Core Banking"])
                app = np.random.choice(["LLM-Copilot", "Risk-Scoring", "Customer-Portal"])
                requests = int(np.random.exponential(scale=350) + 20)
                prompt_tokens = int(requests * np.random.uniform(400, 1800))
                completion_tokens = int(requests * np.random.uniform(150, 600)) if out_rate_m > 0 else 0
                
                cost = (prompt_tokens / 1_000_000.0 * in_rate_m) + (completion_tokens / 1_000_000.0 * out_rate_m)
                cost = round(cost, 4)
                
                ai_records.append({
                    "date": date_str,
                    "month": month_str,
                    "model_name": model_name,
                    "provider": provider,
                    "team": team,
                    "application": app,
                    "request_count": requests,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                    "estimated_cost": cost,
                    "avg_latency_ms": round(float(np.random.normal(650, 120)), 1),
                    "is_synthetic": 1
                })
    df_ai = pd.DataFrame(ai_records)
    
    return df_billing, df_budgets, df_opt, df_ai

def init_database(db_path=None):
    """Initializes SQLite tables and seeds data if empty."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cloud_billing (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        month TEXT NOT NULL,
        service TEXT NOT NULL,
        category TEXT NOT NULL,
        team TEXT,
        environment TEXT,
        application TEXT,
        owner TEXT,
        cost REAL NOT NULL,
        usage_amount REAL,
        is_synthetic INTEGER DEFAULT 1
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month TEXT NOT NULL,
        team TEXT NOT NULL,
        budget_amount REAL NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS optimization_recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resource_id TEXT NOT NULL,
        resource_name TEXT NOT NULL,
        service TEXT NOT NULL,
        team TEXT NOT NULL,
        environment TEXT NOT NULL,
        issue_detected TEXT NOT NULL,
        recommended_action TEXT NOT NULL,
        current_monthly_spend REAL NOT NULL,
        estimated_monthly_savings REAL NOT NULL,
        savings_confidence TEXT NOT NULL,
        status TEXT NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        month TEXT NOT NULL,
        model_name TEXT NOT NULL,
        provider TEXT NOT NULL,
        team TEXT NOT NULL,
        application TEXT NOT NULL,
        request_count INTEGER NOT NULL,
        prompt_tokens INTEGER NOT NULL,
        completion_tokens INTEGER NOT NULL,
        total_tokens INTEGER NOT NULL,
        estimated_cost REAL NOT NULL,
        avg_latency_ms REAL,
        is_synthetic INTEGER DEFAULT 1
    )
    """)
    conn.commit()
    
    # Check if empty
    cursor.execute("SELECT COUNT(*) FROM cloud_billing")
    count = cursor.fetchone()[0]
    
    if count == 0:
        df_billing, df_budgets, df_opt, df_ai = generate_synthetic_data()
        df_billing.to_sql("cloud_billing", conn, if_exists="append", index=False)
        df_budgets.to_sql("budgets", conn, if_exists="append", index=False)
        df_opt.to_sql("optimization_recommendations", conn, if_exists="append", index=False)
        df_ai.to_sql("ai_usage", conn, if_exists="append", index=False)
        conn.commit()
        
    conn.close()

if __name__ == "__main__":
    init_database()
    print("Database initialized and seeded successfully.")
