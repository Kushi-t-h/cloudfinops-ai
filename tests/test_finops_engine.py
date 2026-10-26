import pytest
import pandas as pd
import numpy as np
from src.finops_engine import (
    calculate_cost_kpis,
    analyze_tag_compliance,
    calculate_budget_variance,
    generate_monthly_forecast,
    detect_cost_anomalies,
    calculate_savings_breakdown,
    analyze_ai_usage
)

def test_calculate_cost_kpis():
    data = {
        "date": ["2026-05-01", "2026-05-02", "2026-06-01", "2026-06-02"],
        "month": ["2026-05", "2026-05", "2026-06", "2026-06"],
        "service": ["Amazon EC2", "Amazon S3", "Amazon EC2", "Amazon RDS"],
        "cost": [100.0, 50.0, 120.0, 60.0]
    }
    df = pd.DataFrame(data)
    kpis = calculate_cost_kpis(df)
    
    assert kpis["total_spend"] == 330.0
    assert kpis["service_count"] == 3
    # May spend = 150, June spend = 180 -> MoM = ((180 - 150)/150)*100 = 20%
    assert kpis["mom_change_pct"] == 20.0
    assert kpis["avg_daily_spend"] == round(330.0 / 4, 2)

def test_calculate_cost_kpis_empty():
    df = pd.DataFrame(columns=["date", "month", "service", "cost"])
    kpis = calculate_cost_kpis(df)
    assert kpis["total_spend"] == 0.0
    assert kpis["mom_change_pct"] == 0.0
    assert kpis["service_count"] == 0

def test_analyze_tag_compliance():
    data = {
        "cost": [100.0, 50.0, 50.0],
        "team": ["Data Science", None, "E-Commerce"],
        "application": ["LLM-Copilot", "Risk-Scoring", None],
        "owner": ["sarah.c@company.internal", "sarah.c@company.internal", "sarah.c@company.internal"],
        "service": ["Amazon EC2", "Amazon S3", "Amazon RDS"],
        "environment": ["Production", "Staging", "Development"]
    }
    df = pd.DataFrame(data)
    res = analyze_tag_compliance(df)
    
    assert res["total_spend"] == 200.0
    # Only row 0 has all 3 tags present
    assert res["allocated_spend"] == 100.0
    assert res["unallocated_spend"] == 100.0
    assert res["overall_compliance_pct"] == 50.0
    
    # Team compliance: row 0 and 2 have team -> 150/200 = 75%
    assert res["tag_compliance"]["Team Tag"]["compliance_pct"] == 75.0

def test_analyze_tag_compliance_placeholders():
    """Verify that placeholder strings like 'Unallocated', 'Unassigned', 'None' are treated as missing tags."""
    data = {
        "cost": [100.0, 60.0],
        "team": ["Platform Eng", "Unallocated"],
        "application": ["Checkout-Svc", "Unallocated"],
        "owner": ["sarah.c@company.internal", "Unassigned"],
        "service": ["Amazon EC2", "Amazon S3"],
        "environment": ["Production", "Staging"]
    }
    df = pd.DataFrame(data)
    res = analyze_tag_compliance(df)
    
    assert res["total_spend"] == 160.0
    assert res["allocated_spend"] == 100.0
    assert res["unallocated_spend"] == 60.0
    assert res["overall_compliance_pct"] == 62.5
    assert res["tag_compliance"]["Team Tag"]["missing"] == 60.0

def test_calculate_budget_variance():
    df_billing = pd.DataFrame({
        "month": ["2026-05", "2026-05", "2026-05"],
        "team": ["Platform Eng", "Data Science", "E-Commerce"],
        "cost": [5000.0, 9500.0, 4000.0]
    })
    df_budgets = pd.DataFrame({
        "month": ["2026-05", "2026-05", "2026-05"],
        "team": ["Platform Eng", "Data Science", "E-Commerce"],
        "budget_amount": [6000.0, 8000.0, 4200.0]
    })
    
    df_var = calculate_budget_variance(df_billing, df_budgets, selected_month="2026-05")
    assert len(df_var) == 3
    
    ds_row = df_var[df_var["team"] == "Data Science"].iloc[0]
    assert ds_row["variance"] == -1500.0  # Over budget by $1500
    assert ds_row["remaining_budget_pct"] == -18.75  # (8000 - 9500) / 8000 * 100
    assert ds_row["actual_vs_budget_variance_pct"] == 18.75  # (9500 - 8000) / 8000 * 100
    assert ds_row["status"] == "Over Budget"
    
    ec_row = df_var[df_var["team"] == "E-Commerce"].iloc[0]
    assert ec_row["status"] == "Near Limit (>=90%)"  # 4000/4200 = 95.2%
    assert ec_row["remaining_budget_pct"] == 4.76  # 200/4200 * 100
    assert ec_row["actual_vs_budget_variance_pct"] == -4.76
    
    pe_row = df_var[df_var["team"] == "Platform Eng"].iloc[0]
    assert pe_row["status"] == "On Track"
    assert pe_row["remaining_budget_pct"] == 16.67

def test_calculate_budget_variance_empty_billing():
    """Verify that when billing is empty for a filtered period, budget targets are still evaluated with 0 actuals."""
    df_billing_empty = pd.DataFrame(columns=["month", "team", "cost"])
    df_budgets = pd.DataFrame({
        "month": ["2026-05", "2026-05"],
        "team": ["Platform Eng", "Data Science"],
        "budget_amount": [6000.0, 8000.0]
    })
    df_var = calculate_budget_variance(df_billing_empty, df_budgets, selected_month="2026-05")
    assert len(df_var) == 2
    assert (df_var["actual_spend"] == 0.0).all()
    assert (df_var["variance"] == df_var["budget_amount"]).all()
    assert (df_var["status"] == "On Track").all()

def test_generate_monthly_forecast():
    # 30 days of constant 100 cost (zero historical variance)
    dates = pd.date_range("2026-05-01", periods=30, freq="D")
    df = pd.DataFrame({
        "date": dates.strftime("%Y-%m-%d"),
        "cost": [100.0] * 30
    })
    forecast = generate_monthly_forecast(df)
    assert round(forecast["forecast_amount"], 0) == 3000.0
    # Confidence interval must have strictly valid bounds and distinct spread even with zero sample variance
    assert forecast["lower_bound"] < forecast["forecast_amount"]
    assert forecast["upper_bound"] > forecast["forecast_amount"]
    assert forecast["lower_bound"] >= 0.0

def test_generate_monthly_forecast_edge_cases():
    # Case 1: Single data point (len < 5)
    df_single = pd.DataFrame({
        "date": ["2026-05-01"],
        "cost": [100.0]
    })
    f1 = generate_monthly_forecast(df_single)
    assert f1["forecast_amount"] == 3000.0
    assert f1["lower_bound"] < 3000.0
    assert f1["upper_bound"] > 3000.0
    assert f1["lower_bound"] >= 0.0

    # Case 2: Zero spend across all records
    df_zero = pd.DataFrame({
        "date": ["2026-05-01", "2026-05-02"],
        "cost": [0.0, 0.0]
    })
    f2 = generate_monthly_forecast(df_zero)
    assert f2["forecast_amount"] == 0.0
    assert f2["lower_bound"] == 0.0
    assert f2["upper_bound"] == 0.0

    # Case 3: Empty DataFrame
    f3 = generate_monthly_forecast(pd.DataFrame())
    assert f3["forecast_amount"] == 0.0
    assert f3["lower_bound"] == 0.0
    assert f3["upper_bound"] == 0.0

def test_detect_cost_anomalies():
    # Build 20 days with one huge spike
    dates = pd.date_range("2026-05-01", periods=20, freq="D")
    costs = [50.0] * 19 + [500.0]
    df = pd.DataFrame({
        "date": dates.strftime("%Y-%m-%d"),
        "service": ["Amazon RDS"] * 20,
        "category": ["Database"] * 20,
        "cost": costs
    })
    
    df_anom = detect_cost_anomalies(df, z_threshold=2.5)
    assert not df_anom.empty
    assert df_anom.iloc[0]["service"] == "Amazon RDS"
    assert df_anom.iloc[0]["daily_cost"] == 500.0
    assert "runaway" in df_anom.iloc[0]["explanation"].lower() or "spike" in df_anom.iloc[0]["explanation"].lower()

def test_detect_cost_anomalies_empty_schema():
    """Verify that detect_cost_anomalies on empty inputs returns a DataFrame with expected columns."""
    df_empty = pd.DataFrame(columns=["date", "service", "category", "cost"])
    df_anom = detect_cost_anomalies(df_empty)
    assert df_anom.empty
    expected_cols = ["date", "service", "category", "daily_cost", "expected_baseline", "excess_cost", "surge_pct", "severity", "explanation"]
    assert list(df_anom.columns) == expected_cols

def test_calculate_savings_breakdown():
    df_opt = pd.DataFrame({
        "status": ["Potential", "Potential", "Approved", "Implemented", "Realized"],
        "estimated_monthly_savings": [100.0, 200.0, 150.0, 300.0, 80.0]
    })
    savings = calculate_savings_breakdown(df_opt)
    
    assert savings["potential_savings"] == 300.0
    assert savings["approved_savings"] == 150.0
    assert savings["implemented_savings"] == 300.0
    assert savings["realized_savings"] == 80.0
    # Ensure potential is not mixed into realized
    assert savings["realized_savings"] != savings["potential_savings"]
    assert savings["total_pipeline_savings"] == 830.0

def test_analyze_ai_usage():
    df_ai = pd.DataFrame({
        "date": ["2026-05-01", "2026-05-02"],
        "model_name": ["gpt-4o", "claude-3-5-sonnet"],
        "provider": ["OpenAI Azure API", "Amazon Bedrock"],
        "team": ["Data Science", "E-Commerce"],
        "application": ["LLM-Copilot", "Customer-Portal"],
        "request_count": [1000, 2000],
        "total_tokens": [500000, 800000],
        "estimated_cost": [10.0, 15.0],
        "avg_latency_ms": [600.0, 750.0]
    })
    res = analyze_ai_usage(df_ai)
    assert res["total_ai_spend"] == 25.0
    assert res["total_requests"] == 3000
    assert res["total_tokens"] == 1300000
    # Cost per 1K requests = (25 / 3000) * 1000 = 8.3333
    assert round(res["cost_per_1k_requests"], 2) == 8.33
    assert len(res["by_model"]) == 2

def test_analyze_ai_usage_service_filter_regression():
    """
    Regression test: Selecting 'Amazon Bedrock' in cloud services must filter AI usage
    to only Amazon Bedrock records, altering the KPI totals away from overall totals.
    Also tests an empty match scenario.
    """
    df_ai = pd.DataFrame({
        "date": ["2026-05-01", "2026-05-02", "2026-05-03"],
        "model_name": ["gpt-4o", "claude-3-5-sonnet", "amazon-titan-text-express"],
        "provider": ["OpenAI Azure API", "Amazon Bedrock", "Amazon Bedrock"],
        "team": ["Data Science", "E-Commerce", "Data Science"],
        "application": ["LLM-Copilot", "Customer-Portal", "Risk-Scoring"],
        "request_count": [1000, 2000, 500],
        "total_tokens": [500000, 800000, 100000],
        "estimated_cost": [10.0, 15.0, 2.5],
        "avg_latency_ms": [600.0, 750.0, 400.0]
    })

    # Overall baseline
    res_all = analyze_ai_usage(df_ai)
    assert res_all["total_ai_spend"] == 27.5
    assert res_all["total_tokens"] == 1400000
    assert res_all["total_requests"] == 3500
    assert len(res_all["by_model"]) == 3

    # Filter to only Amazon Bedrock
    selected_services = ["Amazon Bedrock"]
    df_bedrock = df_ai[df_ai["provider"].isin(selected_services)]
    res_bedrock = analyze_ai_usage(df_bedrock)

    assert res_bedrock["total_ai_spend"] == 17.5
    assert res_bedrock["total_tokens"] == 900000
    assert res_bedrock["total_requests"] == 2500
    assert res_bedrock["total_ai_spend"] != res_all["total_ai_spend"]
    assert set(res_bedrock["by_model"]["provider"].unique()) == {"Amazon Bedrock"}
    assert len(res_bedrock["by_model"]) == 2

    # Filter with non-AI service (e.g. Amazon EC2) -> empty AI match
    non_ai_service = ["Amazon EC2"]
    df_empty_match = df_ai[df_ai["provider"].isin(non_ai_service)]
    assert df_empty_match.empty
    res_empty = analyze_ai_usage(df_empty_match)

    assert res_empty["total_ai_spend"] == 0.0
    assert res_empty["total_tokens"] == 0
    assert res_empty["total_requests"] == 0
    assert res_empty["cost_per_1k_requests"] == 0.0
    assert res_empty["by_model"].empty
    assert res_empty["by_app"].empty
    assert list(res_empty["by_model"].columns) == ["model_name", "provider", "total_spend", "total_requests", "total_tokens", "avg_latency"]
    assert list(res_empty["by_app"].columns) == ["application", "total_spend", "total_tokens", "total_requests"]

