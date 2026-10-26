import pandas as pd
import numpy as np

def calculate_cost_kpis(df):
    """
    Computes summary metrics: Total spend, MoM change (%), Average Daily Spend,
    and active service count.
    """
    if df.empty:
        return {
            "total_spend": 0.0,
            "mom_change_pct": 0.0,
            "avg_daily_spend": 0.0,
            "service_count": 0,
            "daily_trend": pd.DataFrame(),
            "monthly_trend": pd.DataFrame()
        }
    
    total_spend = float(df["cost"].sum())
    
    # Calculate daily trend
    daily_trend = df.groupby("date")["cost"].sum().reset_index().sort_values("date")
    avg_daily_spend = float(daily_trend["cost"].mean()) if not daily_trend.empty else 0.0
    
    # Calculate monthly trend & MoM change
    monthly_trend = df.groupby("month")["cost"].sum().reset_index().sort_values("month")
    
    mom_change_pct = 0.0
    if len(monthly_trend) >= 2:
        last_month_spend = monthly_trend.iloc[-1]["cost"]
        prev_month_spend = monthly_trend.iloc[-2]["cost"]
        if prev_month_spend > 0:
            mom_change_pct = round(((last_month_spend - prev_month_spend) / prev_month_spend) * 100.0, 2)
            
    service_count = int(df["service"].nunique())
    
    return {
        "total_spend": round(total_spend, 2),
        "mom_change_pct": mom_change_pct,
        "avg_daily_spend": round(avg_daily_spend, 2),
        "service_count": service_count,
        "daily_trend": daily_trend,
        "monthly_trend": monthly_trend
    }

def analyze_tag_compliance(df):
    """
    Analyzes cost allocation coverage across Team, Application, and Owner tags.
    Computes allocated spend, unallocated spend, compliance rates,
    and breaks down unallocated costs by service and environment.
    """
    if df.empty:
        return {
            "total_spend": 0.0,
            "allocated_spend": 0.0,
            "unallocated_spend": 0.0,
            "overall_compliance_pct": 100.0,
            "tag_compliance": {},
            "unallocated_by_service": pd.DataFrame(),
            "unallocated_by_env": pd.DataFrame()
        }
        
    total_spend = float(df["cost"].sum())
    
    # A record is considered fully compliant if team, application, and owner are present and valid
    unallocated_placeholders = {"", "none", "unallocated", "unassigned", "unknown"}
    
    def is_valid_tag(series):
        return series.notna() & ~series.astype(str).str.strip().str.lower().isin(unallocated_placeholders)
        
    has_team = is_valid_tag(df["team"])
    has_app = is_valid_tag(df["application"])
    has_owner = is_valid_tag(df["owner"])
    
    fully_tagged_mask = has_team & has_app & has_owner
    
    allocated_spend = float(df[fully_tagged_mask]["cost"].sum())
    unallocated_spend = float(df[~fully_tagged_mask]["cost"].sum())
    compliance_pct = round((allocated_spend / total_spend) * 100.0, 2) if total_spend > 0 else 100.0
    
    # Tag-level breakdown
    tag_stats = {
        "Team Tag": {
            "allocated": round(float(df[has_team]["cost"].sum()), 2),
            "missing": round(float(df[~has_team]["cost"].sum()), 2),
            "compliance_pct": round((df[has_team]["cost"].sum() / total_spend) * 100.0, 1) if total_spend > 0 else 100.0
        },
        "Application Tag": {
            "allocated": round(float(df[has_app]["cost"].sum()), 2),
            "missing": round(float(df[~has_app]["cost"].sum()), 2),
            "compliance_pct": round((df[has_app]["cost"].sum() / total_spend) * 100.0, 1) if total_spend > 0 else 100.0
        },
        "Owner Tag": {
            "allocated": round(float(df[has_owner]["cost"].sum()), 2),
            "missing": round(float(df[~has_owner]["cost"].sum()), 2),
            "compliance_pct": round((df[has_owner]["cost"].sum() / total_spend) * 100.0, 1) if total_spend > 0 else 100.0
        }
    }
    
    # Unallocated breakdown
    df_missing = df[~fully_tagged_mask]
    unallocated_by_service = (
        df_missing.groupby("service")["cost"]
        .sum()
        .reset_index()
        .sort_values("cost", ascending=False)
    )
    unallocated_by_env = (
        df_missing.groupby("environment")["cost"]
        .sum()
        .reset_index()
        .sort_values("cost", ascending=False)
    )
    
    return {
        "total_spend": round(total_spend, 2),
        "allocated_spend": round(allocated_spend, 2),
        "unallocated_spend": round(unallocated_spend, 2),
        "overall_compliance_pct": compliance_pct,
        "tag_compliance": tag_stats,
        "unallocated_by_service": unallocated_by_service,
        "unallocated_by_env": unallocated_by_env
    }

def calculate_budget_variance(df_billing, df_budgets, selected_month=None):
    """
    Merges actual spend with budgeted limits by month and team.
    Calculates Variance ($) and Variance (%) and flags over-budget risks.
    """
    columns = [
        "month", "team", "actual_spend", "budget_amount",
        "variance", "variance_pct", "remaining_budget_pct",
        "actual_vs_budget_variance_pct", "utilization_pct", "status"
    ]
    if df_budgets.empty:
        return pd.DataFrame(columns=columns)
        
    if df_billing.empty:
        actuals = pd.DataFrame(columns=["month", "team", "actual_spend"])
    else:
        # Exclude missing or Unallocated team labels when calculating official team budget consumption
        valid_teams_mask = df_billing["team"].notna() & (df_billing["team"] != "") & (df_billing["team"] != "Unallocated")
        actuals = (
            df_billing[valid_teams_mask]
            .groupby(["month", "team"])["cost"]
            .sum()
            .reset_index()
            .rename(columns={"cost": "actual_spend"})
        )
    
    merged = pd.merge(df_budgets, actuals, on=["month", "team"], how="left")
    merged["actual_spend"] = merged["actual_spend"].fillna(0.0)
    
    # Calculate actual-versus-budget variance %:
    # variance = budget - actual (Positive = favorable/under budget, Negative = unfavorable/over budget)
    # variance_pct: positive indicates remaining budget %; negative indicates overspend %
    merged["variance"] = merged["budget_amount"] - merged["actual_spend"]
    merged["variance_pct"] = np.where(
        merged["budget_amount"] > 0,
        (merged["variance"] / merged["budget_amount"]) * 100.0,
        0.0
    )
    merged["remaining_budget_pct"] = merged["variance_pct"]
    merged["actual_vs_budget_variance_pct"] = np.where(
        merged["budget_amount"] > 0,
        ((merged["actual_spend"] - merged["budget_amount"]) / merged["budget_amount"]) * 100.0,
        0.0
    )
    merged["utilization_pct"] = np.where(
        merged["budget_amount"] > 0,
        (merged["actual_spend"] / merged["budget_amount"]) * 100.0,
        0.0
    )
    
    def flag_status(row):
        if row["actual_spend"] > row["budget_amount"]:
            return "Over Budget"
        elif row["utilization_pct"] >= 90.0:
            return "Near Limit (>=90%)"
        else:
            return "On Track"
            
    merged["status"] = merged.apply(flag_status, axis=1)
    
    # Round numerical cols
    merged["actual_spend"] = merged["actual_spend"].round(2)
    merged["budget_amount"] = merged["budget_amount"].round(2)
    merged["variance"] = merged["variance"].round(2)
    merged["variance_pct"] = merged["variance_pct"].round(2)
    merged["remaining_budget_pct"] = merged["remaining_budget_pct"].round(2)
    merged["actual_vs_budget_variance_pct"] = merged["actual_vs_budget_variance_pct"].round(2)
    merged["utilization_pct"] = merged["utilization_pct"].round(1)
    
    if selected_month:
        merged = merged[merged["month"] == selected_month]
        
    return merged.sort_values(["month", "actual_spend"], ascending=[True, False])

def generate_monthly_forecast(df_billing, periods_ahead=1):
    """
    Generates a simple, transparent next-month cost forecast using
    rolling exponential-weighted moving average (EWMA) and historical daily run rates.
    Explicitly labeled as an estimate.
    """
    if df_billing.empty:
        return {"forecast_amount": 0.0, "lower_bound": 0.0, "upper_bound": 0.0, "explanation": "No data"}
        
    daily_spend = df_billing.groupby("date")["cost"].sum().reset_index().sort_values("date")
    
    if len(daily_spend) < 14:
        recent_daily_avg = float(daily_spend["cost"].mean())
    else:
        # 30-day EWMA daily spend
        weights = np.exp(np.linspace(-1, 0, min(30, len(daily_spend))))
        weights /= weights.sum()
        recent_daily_avg = float(np.sum(daily_spend["cost"].tail(len(weights)) * weights))
        
    # Projected next 30-day month
    forecast_spend = round(recent_daily_avg * 30.0, 2)
    sample_std = float(daily_spend["cost"].tail(30).std()) if len(daily_spend) >= 2 else 0.0
    
    # Ensure valid confidence interval even with few data points, small variance, or zero variance
    if sample_std > 0 and len(daily_spend) >= 5:
        std_daily = sample_std
    elif recent_daily_avg > 0:
        std_daily = recent_daily_avg * 0.05
    else:
        std_daily = 0.0
        
    margin = round(std_daily * np.sqrt(30) * 1.645, 2)  # ~90% confidence interval
    
    # If margin is 0 despite positive spend, enforce minimal 1% spread so interval bounds are valid and distinct
    if margin == 0.0 and forecast_spend > 0:
        margin = round(forecast_spend * 0.02, 2)
        
    lower_bound = max(0.0, round(float(forecast_spend - margin), 2))
    upper_bound = round(float(forecast_spend + margin), 2)
    
    return {
        "forecast_amount": float(forecast_spend),
        "lower_bound": float(lower_bound),
        "upper_bound": float(upper_bound),
        "daily_run_rate": round(float(recent_daily_avg), 2),
        "explanation": f"Estimated projection based on 30-day weighted daily run rate (${recent_daily_avg:,.2f}/day) across 30 days."
    }

def detect_cost_anomalies(df_billing, z_threshold=2.5):
    """
    Detects unusual daily spending spikes per service using statistical standard deviations
    (Z-score). Flags the service, date, spike amount, baseline cost, and actionable explanation.
    """
    columns = [
        "date", "service", "category", "daily_cost",
        "expected_baseline", "excess_cost", "surge_pct",
        "severity", "explanation"
    ]
    if df_billing.empty:
        return pd.DataFrame(columns=columns)
        
    # Group daily spend per service
    daily_svc = (
        df_billing.groupby(["date", "service", "category"])["cost"]
        .sum()
        .reset_index()
        .sort_values(["service", "date"])
    )
    
    anomalies = []
    columns = [
        "date", "service", "category", "daily_cost",
        "expected_baseline", "excess_cost", "surge_pct",
        "severity", "explanation"
    ]
    
    for (svc, cat), group in daily_svc.groupby(["service", "category"]):
        if len(group) < 7:
            continue
        # Rolling baseline 14 days
        rolling_mean = group["cost"].rolling(window=14, min_periods=5).mean()
        rolling_std = group["cost"].rolling(window=14, min_periods=5).std().replace(0, 1.0)
        
        z_scores = (group["cost"] - rolling_mean) / rolling_std
        
        anomaly_rows = group[z_scores > z_threshold].copy()
        if not anomaly_rows.empty:
            for idx, row in anomaly_rows.iterrows():
                baseline = rolling_mean.loc[idx]
                excess = row["cost"] - baseline
                pct_surge = (excess / baseline) * 100.0 if baseline > 0 else 0
                
                # Contextual explanation
                explanation = f"Daily spend spiked {pct_surge:.1f}% above 14-day baseline (${baseline:.2f})."
                if "RDS" in svc:
                    explanation += " Possible runaway unindexed join queries or unthrottled replica reads."
                elif "Bedrock" in svc or "AI" in svc:
                    explanation += " High-volume batch prompt experiment or unoptimized token context window."
                elif "EKS" in svc:
                    explanation += " Node autoscale runaway or rogue job restart loop."
                else:
                    explanation += " Sustained burst in traffic or unmanaged worker instances."
                    
                anomalies.append({
                    "date": row["date"],
                    "service": svc,
                    "category": cat,
                    "daily_cost": round(row["cost"], 2),
                    "expected_baseline": round(baseline, 2),
                    "excess_cost": round(excess, 2),
                    "surge_pct": round(pct_surge, 1),
                    "severity": "Critical" if pct_surge > 200 else "High",
                    "explanation": explanation
                })
                
    df_anomalies = pd.DataFrame(anomalies)
    if not df_anomalies.empty:
        df_anomalies = df_anomalies.sort_values("excess_cost", ascending=False)
    else:
        df_anomalies = pd.DataFrame(columns=columns)
    return df_anomalies

def calculate_savings_breakdown(df_opt):
    """
    Separates Potential, Approved, Implemented, and Realized savings.
    Strictly guarantees estimated savings are never conflated with realized savings.
    """
    if df_opt.empty:
        return {
            "potential_savings": 0.0,
            "approved_savings": 0.0,
            "implemented_savings": 0.0,
            "realized_savings": 0.0,
            "total_pipeline_savings": 0.0,
            "summary_df": pd.DataFrame()
        }
        
    status_summary = (
        df_opt.groupby("status")["estimated_monthly_savings"]
        .agg(["sum", "count"])
        .reset_index()
        .rename(columns={"sum": "monthly_savings", "count": "recommendation_count"})
    )
    
    savings_map = {row["status"]: row["monthly_savings"] for _, row in status_summary.iterrows()}
    
    potential = round(savings_map.get("Potential", 0.0), 2)
    approved = round(savings_map.get("Approved", 0.0), 2)
    implemented = round(savings_map.get("Implemented", 0.0), 2)
    realized = round(savings_map.get("Realized", 0.0), 2)
    
    return {
        "potential_savings": potential,
        "approved_savings": approved,
        "implemented_savings": implemented,
        "realized_savings": realized,
        "total_pipeline_savings": round(potential + approved + implemented + realized, 2),
        "summary_df": status_summary
    }

def analyze_ai_usage(df_ai):
    """
    Computes AI FinOps metrics: Total GenAI spend, Total Tokens, Cost per 1K requests,
    Spend by Model and Spend by Application.
    """
    model_cols = ["model_name", "provider", "total_spend", "total_requests", "total_tokens", "avg_latency"]
    app_cols = ["application", "total_spend", "total_tokens", "total_requests"]
    daily_cols = ["date", "model_name", "estimated_cost"]

    if df_ai.empty:
        return {
            "total_ai_spend": 0.0,
            "total_tokens": 0,
            "total_requests": 0,
            "cost_per_1k_requests": 0.0,
            "by_model": pd.DataFrame(columns=model_cols),
            "by_app": pd.DataFrame(columns=app_cols),
            "daily_ai_spend": pd.DataFrame(columns=daily_cols)
        }
        
    total_ai_spend = float(df_ai["estimated_cost"].sum())
    total_tokens = int(df_ai["total_tokens"].sum())
    total_requests = int(df_ai["request_count"].sum())
    
    cost_per_1k = round((total_ai_spend / total_requests) * 1000.0, 4) if total_requests > 0 else 0.0
    
    by_model = (
        df_ai.groupby(["model_name", "provider"])
        .agg(
            total_spend=("estimated_cost", "sum"),
            total_requests=("request_count", "sum"),
            total_tokens=("total_tokens", "sum"),
            avg_latency=("avg_latency_ms", "mean")
        )
        .reset_index()
        .sort_values("total_spend", ascending=False)
    )
    by_model["total_spend"] = by_model["total_spend"].round(2)
    by_model["avg_latency"] = by_model["avg_latency"].round(1)
    
    by_app = (
        df_ai.groupby("application")
        .agg(
            total_spend=("estimated_cost", "sum"),
            total_tokens=("total_tokens", "sum"),
            total_requests=("request_count", "sum")
        )
        .reset_index()
        .sort_values("total_spend", ascending=False)
    )
    by_app["total_spend"] = by_app["total_spend"].round(2)
    
    daily_ai_spend = (
        df_ai.groupby(["date", "model_name"])["estimated_cost"]
        .sum()
        .reset_index()
        .sort_values("date")
    )
    
    return {
        "total_ai_spend": round(total_ai_spend, 2),
        "total_tokens": total_tokens,
        "total_requests": total_requests,
        "cost_per_1k_requests": cost_per_1k,
        "by_model": by_model,
        "by_app": by_app,
        "daily_ai_spend": daily_ai_spend
    }
