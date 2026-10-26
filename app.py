import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import get_connection, init_database
from src.finops_engine import (
    calculate_cost_kpis,
    analyze_tag_compliance,
    calculate_budget_variance,
    generate_monthly_forecast,
    detect_cost_anomalies,
    calculate_savings_breakdown,
    analyze_ai_usage
)

# Set page configuration
st.set_page_config(
    page_title="CloudFinOps AI — Cloud Cost Intelligence & Optimization",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for high-polish enterprise FinOps aesthetics
st.markdown("""
<style>
    .metric-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }
    .finops-badge {
        display: inline-block;
        padding: 3px 10px;
        font-size: 12px;
        font-weight: 600;
        border-radius: 12px;
    }
    .badge-on-track { background-color: #def7ec; color: #03543f; }
    .badge-warning { background-color: #fef08a; color: #713f12; }
    .badge-alert { background-color: #fde8e8; color: #9b1c1c; }
    .disclaimer-banner {
        background-color: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 10px 16px;
        margin-bottom: 20px;
        border-radius: 4px;
        font-size: 13px;
        color: #14532d;
    }
</style>
""", unsafe_allow_html=True)

# Ensure DB is created & seeded
init_database()

@st.cache_data(ttl=600)
def load_data():
    conn = get_connection()
    df_billing = pd.read_sql("SELECT * FROM cloud_billing", conn)
    df_budgets = pd.read_sql("SELECT * FROM budgets", conn)
    df_opt = pd.read_sql("SELECT * FROM optimization_recommendations", conn)
    df_ai = pd.read_sql("SELECT * FROM ai_usage", conn)
    conn.close()
    
    # Fill Nones gracefully
    df_billing["team"] = df_billing["team"].fillna("Unallocated")
    df_billing["application"] = df_billing["application"].fillna("Unallocated")
    df_billing["owner"] = df_billing["owner"].fillna("Unassigned")
    df_billing["environment"] = df_billing["environment"].fillna("Unknown")
    
    return df_billing, df_budgets, df_opt, df_ai

# Load datasets
df_billing_all, df_budgets_all, df_opt_all, df_ai_all = load_data()

# ----------------- SIDEBAR FILTERS -----------------
st.sidebar.markdown("## ☁️ CloudFinOps AI")
st.sidebar.caption("Portfolio Project | Cloud Cost Intelligence & Optimization")

st.sidebar.markdown("---")
st.sidebar.subheader("Global Filters")

# Date range selection
min_date = pd.to_datetime(df_billing_all["date"].min()).date()
max_date = pd.to_datetime(df_billing_all["date"].max()).date()

date_range = st.sidebar.date_input(
    "Billing Period Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_filter, end_filter = date_range
else:
    start_filter, end_filter = min_date, max_date

# Service filter
all_services = sorted(df_billing_all["service"].unique().tolist())
selected_services = st.sidebar.multiselect(
    "Cloud Services",
    options=all_services,
    default=all_services
)

# Team filter
all_teams = sorted(df_billing_all["team"].unique().tolist())
selected_teams = st.sidebar.multiselect(
    "Teams",
    options=all_teams,
    default=all_teams
)

# Environment filter
all_envs = sorted(df_billing_all["environment"].unique().tolist())
selected_envs = st.sidebar.multiselect(
    "Environments",
    options=all_envs,
    default=all_envs
)

# Apply filters
df_billing_filtered = df_billing_all[
    (pd.to_datetime(df_billing_all["date"]).dt.date >= start_filter) &
    (pd.to_datetime(df_billing_all["date"]).dt.date <= end_filter) &
    (df_billing_all["service"].isin(selected_services if selected_services else all_services)) &
    (df_billing_all["team"].isin(selected_teams if selected_teams else all_teams)) &
    (df_billing_all["environment"].isin(selected_envs if selected_envs else all_envs))
]

active_services = set(selected_services if selected_services else all_services)

df_budgets_filtered = df_budgets_all[df_budgets_all["team"].isin(selected_teams if selected_teams else all_teams)]

# Filter optimization recommendations by team, environment, and service match
df_opt_filtered = df_opt_all[
    (df_opt_all["team"].isin(selected_teams if selected_teams else all_teams)) &
    (df_opt_all["environment"].isin(selected_envs if selected_envs else all_envs)) &
    (df_opt_all["service"].apply(lambda s: any(s == act or s.startswith(act) or act.startswith(s) for act in active_services)))
]

# Filter AI usage by date range, team, and selected AI cloud service providers (e.g. 'Amazon Bedrock', 'OpenAI Azure API')
df_ai_filtered = df_ai_all[
    (pd.to_datetime(df_ai_all["date"]).dt.date >= start_filter) &
    (pd.to_datetime(df_ai_all["date"]).dt.date <= end_filter) &
    (df_ai_all["team"].isin(selected_teams if selected_teams else all_teams)) &
    (df_ai_all["provider"].isin(active_services))
]

# Sidebar info
st.sidebar.markdown("---")
st.sidebar.markdown(
    "ℹ️ **Disclaimer & Role Alignment**\n\n"
    "Built for an **Entry-Level Cloud FinOps Analyst** role demonstrating cost allocation, "
    "unit economics, unit budgeting, anomaly triage, and GenAI token accountability.\n\n"
    "**All data is synthetic** and simulated without requiring real cloud accounts or API keys."
)

# ----------------- MAIN HEADER & TABS -----------------
st.title("CloudFinOps AI — Cloud Cost Intelligence Platform")
st.markdown("""
<div class="disclaimer-banner">
    <strong>Notice:</strong> This platform operates entirely on synthetic cloud billing and usage data. 
    Forecasts, anomaly baselines, and rightsizing savings are simulated estimates intended to demonstrate 
    FinOps Foundation Framework practices (Inform, Optimize, Operate).
</div>
""", unsafe_allow_html=True)

# Primary Navigation Tabs
tabs = st.tabs([
    "📊 Executive Cost Dashboard",
    "🏷️ Cost Allocation & Tags",
    "📈 Budgets & Forecast",
    "⚡ Anomaly Detection",
    "💡 Cost Optimization",
    "🤖 AI FinOps (GenAI)",
    "💰 Savings Tracker",
    "📥 Downloadable Reports"
])

# ================= TAB 1: EXECUTIVE COST DASHBOARD =================
with tabs[0]:
    st.subheader("Cloud Spending Executive Overview")
    
    kpis = calculate_cost_kpis(df_billing_filtered)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="Total Cloud Spend",
            value=f"${kpis['total_spend']:,.2f}",
            delta=f"{kpis['mom_change_pct']:+.1f}% MoM" if kpis['mom_change_pct'] != 0 else None
        )
    with col2:
        st.metric(
            label="Avg Daily Run Rate",
            value=f"${kpis['avg_daily_spend']:,.2f}/day"
        )
    with col3:
        st.metric(
            label="Active Cloud Services",
            value=kpis['service_count']
        )
    with col4:
        # Calculate overall budget utilization across filtered months
        filtered_months = df_billing_filtered["month"].unique().tolist()
        b_sub = df_budgets_all[df_budgets_all["month"].isin(filtered_months)]
        total_budget = b_sub["budget_amount"].sum() if not b_sub.empty else 1.0
        utilization = (kpis['total_spend'] / total_budget) * 100.0 if total_budget > 0 else 0
        st.metric(
            label="Budget Utilization",
            value=f"{utilization:.1f}%",
            delta=f"{'Over Budget' if utilization > 100 else 'Under Budget'}",
            delta_color="inverse"
        )
        
    st.markdown("---")
    
    # Visualizations: Trend & Breakdowns
    t_col1, t_col2 = st.columns([7, 5])
    
    with t_col1:
        st.markdown("##### 📅 Daily Spend Trend with 7-Day Moving Average")
        if not kpis["daily_trend"].empty:
            d_df = kpis["daily_trend"].copy()
            d_df["ma_7d"] = d_df["cost"].rolling(7, min_periods=1).mean()
            fig_daily = go.Figure()
            fig_daily.add_trace(go.Bar(
                x=d_df["date"], y=d_df["cost"],
                name="Daily Actual Spend", marker_color="#93c5fd"
            ))
            fig_daily.add_trace(go.Scatter(
                x=d_df["date"], y=d_df["ma_7d"],
                name="7-Day Moving Average", line=dict(color="#1d4ed8", width=2.5)
            ))
            fig_daily.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=320,
                xaxis_title="Billing Date",
                yaxis_title="Spend ($)"
            )
            st.plotly_chart(fig_daily, use_container_width=True)
        else:
            st.info("No billing data available for current filter selection.")
            
    with t_col2:
        st.markdown("##### 🏢 Monthly Spend Trend")
        if not kpis["monthly_trend"].empty:
            fig_monthly = px.bar(
                kpis["monthly_trend"],
                x="month",
                y="cost",
                text_auto=".2s",
                color_discrete_sequence=["#3b82f6"]
            )
            fig_monthly.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                height=320,
                xaxis_title="Billing Month",
                yaxis_title="Total Monthly Spend ($)"
            )
            st.plotly_chart(fig_monthly, use_container_width=True)
            
    st.markdown("##### Dimensional Spend Distributions")
    d_col1, d_col2, d_col3 = st.columns(3)
    
    with d_col1:
        st.markdown("**Spend by Service**")
        svc_spend = df_billing_filtered.groupby("service")["cost"].sum().reset_index()
        fig_svc = px.pie(svc_spend, names="service", values="cost", hole=0.45, color_discrete_sequence=px.colors.qualitative.Safe)
        fig_svc.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=260)
        st.plotly_chart(fig_svc, use_container_width=True)
        
    with d_col2:
        st.markdown("**Spend by Team**")
        team_spend = df_billing_filtered.groupby("team")["cost"].sum().reset_index()
        fig_team = px.pie(team_spend, names="team", values="cost", hole=0.45, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_team.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=260)
        st.plotly_chart(fig_team, use_container_width=True)
        
    with d_col3:
        st.markdown("**Spend by Environment**")
        env_spend = df_billing_filtered.groupby("environment")["cost"].sum().reset_index()
        fig_env = px.pie(env_spend, names="environment", values="cost", hole=0.45, color_discrete_sequence=px.colors.qualitative.Bold)
        fig_env.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=260)
        st.plotly_chart(fig_env, use_container_width=True)

# ================= TAB 2: COST ALLOCATION & TAGS =================
with tabs[1]:
    st.subheader("Cost Allocation & Tag Hygiene Analysis")
    st.write(
        "FinOps best practices mandate assigning every dollar of cloud spend to a specific business unit, "
        "application, and owner. Untagged infrastructure leads to unallocated 'ghost' spend."
    )
    
    tag_report = analyze_tag_compliance(df_billing_filtered)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Analyzed Spend", f"${tag_report['total_spend']:,.2f}")
    with col2:
        st.metric("Fully Allocated Spend", f"${tag_report['allocated_spend']:,.2f}")
    with col3:
        st.metric(
            "Overall Tag Compliance",
            f"{tag_report['overall_compliance_pct']:.1f}%",
            delta=f"-${tag_report['unallocated_spend']:,.2f} Unallocated",
            delta_color="inverse"
        )
        
    st.markdown("---")
    
    col_t1, col_t2 = st.columns([5, 7])
    
    with col_t1:
        st.markdown("##### 🏷️ Mandatory Tag Compliance Coverage")
        tag_data = []
        for tag_name, details in tag_report["tag_compliance"].items():
            tag_data.append({
                "Tag Key": tag_name,
                "Compliance Rate": f"{details['compliance_pct']:.1f}%",
                "Allocated Spend": f"${details['allocated']:,.2f}",
                "Missing Tag Spend": f"${details['missing']:,.2f}"
            })
        st.table(pd.DataFrame(tag_data))
        
        st.markdown("##### 💡 FinOps Remediation Action")
        st.info(
            "**Policy Recommendation:** Implement AWS SCPs / Azure Policy to deny resource provisioning "
            "without mandatory `Team`, `Application`, and `Owner` tags. Run automated tag discovery pipelines."
        )
        
    with col_t2:
        st.markdown("##### ⚠️ Unallocated Spend Exposure by Service")
        if not tag_report["unallocated_by_service"].empty:
            fig_unalloc = px.bar(
                tag_report["unallocated_by_service"],
                x="cost",
                y="service",
                orientation="h",
                text_auto=".2s",
                color="cost",
                color_continuous_scale="Reds"
            )
            fig_unalloc.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=280,
                xaxis_title="Unallocated Spend ($)",
                yaxis_title="Service"
            )
            st.plotly_chart(fig_unalloc, use_container_width=True)

# ================= TAB 3: BUDGETS & FORECAST =================
with tabs[2]:
    st.subheader("Budget Tracking, Variance Analysis & Predictive Forecasting")
    
    b_col1, b_col2 = st.columns([4, 8])
    with b_col1:
        avail_months = sorted(df_billing_filtered["month"].unique().tolist())
        if not avail_months:
            avail_months = sorted(df_billing_all["month"].unique().tolist())
        selected_b_month = st.selectbox(
            "Select Evaluation Month",
            options=avail_months,
            index=len(avail_months) - 1 if avail_months else 0
        )
        
    variance_df = calculate_budget_variance(df_billing_filtered, df_budgets_filtered, selected_month=selected_b_month)
    
    total_budget_eval = variance_df["budget_amount"].sum()
    total_actual_eval = variance_df["actual_spend"].sum()
    total_variance_eval = variance_df["variance"].sum()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Selected Month Budget", f"${total_budget_eval:,.2f}")
    m2.metric("Selected Month Actuals", f"${total_actual_eval:,.2f}")
    m3.metric(
        "Net Variance ($)",
        f"${total_variance_eval:,.2f}",
        delta=f"Remaining: {(total_variance_eval / total_budget_eval)*100:+.1f}%" if total_budget_eval > 0 else "0%",
        delta_color="normal" if total_variance_eval >= 0 else "inverse"
    )
    
    st.markdown("##### Team Budget vs Actual Spend Breakdown")
    fig_bud = go.Figure()
    fig_bud.add_trace(go.Bar(
        x=variance_df["team"], y=variance_df["budget_amount"],
        name="Allocated Budget", marker_color="#cbd5e1"
    ))
    fig_bud.add_trace(go.Bar(
        x=variance_df["team"], y=variance_df["actual_spend"],
        name="Actual Spend", marker_color="#3b82f6"
    ))
    fig_bud.update_layout(
        barmode="group",
        height=320,
        margin=dict(l=10, r=10, t=20, b=10),
        yaxis_title="Spend ($)"
    )
    st.plotly_chart(fig_bud, use_container_width=True)
    
    st.dataframe(
        variance_df.style.map(
            lambda v: "color: red; font-weight: bold;" if v == "Over Budget" else ("color: orange; font-weight: bold;" if v == "Near Limit (>=90%)" else "color: green;"),
            subset=["status"]
        ),
        column_config={
            "month": "Billing Month",
            "team": "Team",
            "actual_spend": st.column_config.NumberColumn("Actual Spend ($)", format="$%.2f"),
            "budget_amount": st.column_config.NumberColumn("Allocated Budget ($)", format="$%.2f"),
            "variance": st.column_config.NumberColumn("Net Variance ($)", format="$%.2f", help="Budget minus Actual Spend (>0 under budget, <0 over budget)"),
            "remaining_budget_pct": st.column_config.NumberColumn("Remaining Budget (%)", format="%.2f%%", help="Remaining unspent budget as a % of allocated budget"),
            "actual_vs_budget_variance_pct": st.column_config.NumberColumn("Actual vs Budget (%)", format="%+.2f%%", help="Percentage by which actual spend differs from budget"),
            "utilization_pct": st.column_config.NumberColumn("Budget Utilization (%)", format="%.1f%%"),
            "status": "Budget Status"
        },
        use_container_width=True
    )
    
    st.markdown("---")
    st.markdown("#### 🔮 Next-Month Cost Forecasting (EWMA Estimate)")
    
    forecast = generate_monthly_forecast(df_billing_filtered)
    
    f_col1, f_col2, f_col3 = st.columns(3)
    f_col1.metric("Next Month Projected Spend", f"${forecast['forecast_amount']:,.2f}")
    f_col2.metric("Estimated Range (90% CI)", f"${forecast['lower_bound']:,.2f} — ${forecast['upper_bound']:,.2f}")
    f_col3.metric("Projected Daily Run Rate", f"${forecast['daily_run_rate']:,.2f}/day")
    st.caption(f"ℹ️ Model Note: {forecast['explanation']}")

# ================= TAB 4: ANOMALY DETECTION =================
with tabs[3]:
    st.subheader("Automated Cost Anomaly Detection & Incident Triage")
    st.write(
        "Statistical anomaly detection flags unexpected spikes in daily spend per cloud service (> 2.5σ "
        "above 14-day rolling baseline), alerting FinOps analysts before month-end invoice shocks."
    )
    
    df_anomalies = detect_cost_anomalies(df_billing_filtered)
    
    if not df_anomalies.empty:
        a_count = len(df_anomalies)
        total_excess = df_anomalies["excess_cost"].sum()
        
        c1, c2 = st.columns(2)
        c1.metric("Detected Anomaly Incidents", a_count)
        c2.metric("Cumulative Unbudgeted Spike Impact", f"${total_excess:,.2f}")
        
        st.markdown("##### Flagged Spike Events")
        for idx, row in df_anomalies.iterrows():
            severity_color = "🔴" if row["severity"] == "Critical" else "🟠"
            with st.expander(f"{severity_color} {row['date']} — {row['service']} (+{row['surge_pct']}% Spike: +${row['excess_cost']:,.2f})"):
                ac1, ac2, ac3, ac4 = st.columns(4)
                ac1.write(f"**Actual Spend:** ${row['daily_cost']:,.2f}")
                ac2.write(f"**Expected Baseline:** ${row['expected_baseline']:,.2f}")
                ac3.write(f"**Excess Amount:** +${row['excess_cost']:,.2f}")
                ac4.write(f"**Severity Level:** {row['severity']}")
                st.markdown(f"**Root-Cause Diagnosis & Explanation:**\n> {row['explanation']}")
    else:
        st.success("✅ No anomalous spending spikes detected within current filter boundaries.")

# ================= TAB 5: COST OPTIMIZATION =================
with tabs[4]:
    st.subheader("Cost Optimization & Rightsizing Pipeline")
    st.write(
        "Proactive identification of simulated idle, oversized, or unattached cloud resources. "
        "Each action is staged through FinOps lifecycle governance."
    )
    
    st.dataframe(
        df_opt_filtered,
        column_config={
            "resource_id": "Resource ID",
            "resource_name": "Resource Identifier",
            "service": "Service",
            "team": "Owner Team",
            "issue_detected": "Waste Pattern Detected",
            "recommended_action": "FinOps Action Item",
            "current_monthly_spend": st.column_config.NumberColumn(format="$%.2f"),
            "estimated_monthly_savings": st.column_config.NumberColumn(format="$%.2f"),
            "status": "Governance Status"
        },
        use_container_width=True
    )
    
    st.markdown("##### Potential Savings by Cloud Service")
    if not df_opt_filtered.empty:
        opt_by_svc = df_opt_filtered.groupby("service")["estimated_monthly_savings"].sum().reset_index()
        fig_opt = px.bar(
            opt_by_svc,
            x="service",
            y="estimated_monthly_savings",
            text_auto=".2s",
            color="service",
            color_discrete_sequence=px.colors.qualitative.Dark2
        )
        fig_opt.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=300, yaxis_title="Est. Monthly Savings ($)")
        st.plotly_chart(fig_opt, use_container_width=True)
    else:
        st.info("No optimization recommendations match the current filter selection.")

# ================= TAB 6: AI FINOPS (GENAI) =================
with tabs[5]:
    st.subheader("AI FinOps — LLM Token Consumption & Cost Transparency")
    st.write(
        "With rapid generative AI adoption, tracking unit cost per request, prompt/completion token ratios, "
        "and model-level spend is a crucial discipline for contemporary FinOps practitioners."
    )
    
    if df_ai_filtered.empty:
        st.info("ℹ️ No AI FinOps usage records match the current sidebar filter criteria (selected services, teams, or date range).")
    
    ai_metrics = analyze_ai_usage(df_ai_filtered)
    
    ai_c1, ai_c2, ai_c3, ai_c4 = st.columns(4)
    ai_c1.metric("Total GenAI Model Spend", f"${ai_metrics['total_ai_spend']:,.2f}")
    ai_c2.metric("Total Tokens Processed", f"{ai_metrics['total_tokens']:,}")
    ai_c3.metric("Total API Invocations", f"{ai_metrics['total_requests']:,}")
    ai_c4.metric("Cost per 1,000 Requests", f"${ai_metrics['cost_per_1k_requests']:.4f}")
    
    st.markdown("---")
    
    a_col1, a_col2 = st.columns(2)
    
    with a_col1:
        st.markdown("##### 🤖 Spend & Latency by AI Foundation Model")
        if not ai_metrics["by_model"].empty:
            st.dataframe(ai_metrics["by_model"], use_container_width=True)
        else:
            st.info("No model telemetry available for selected filters.")
        
    with a_col2:
        st.markdown("##### 🏢 AI Spend by Consuming Application")
        if not ai_metrics["by_app"].empty:
            fig_ai_app = px.pie(
                ai_metrics["by_app"],
                names="application",
                values="total_spend",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel2
            )
            fig_ai_app.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=280)
            st.plotly_chart(fig_ai_app, use_container_width=True)
        else:
            st.info("No application AI spend available for selected filters.")
        
    st.markdown("##### Daily AI Expenditure Trend by Model")
    if not ai_metrics["daily_ai_spend"].empty:
        fig_ai_daily = px.area(
            ai_metrics["daily_ai_spend"],
            x="date",
            y="estimated_cost",
            color="model_name",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_ai_daily.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=300, yaxis_title="Cost ($)")
        st.plotly_chart(fig_ai_daily, use_container_width=True)
    else:
        st.info("No daily AI expenditure data available for selected filters.")

# ================= TAB 7: SAVINGS TRACKER =================
with tabs[6]:
    st.subheader("FinOps Savings Realization Governance Lifecycle")
    st.write(
        "A foundational tenet of FinOps is maintaining a strict separation between **Potential (Estimated)** "
        "savings and **Realized (Audited)** savings. An initiative only converts to Realized once engineering "
        "executes the change and invoice validation confirms the reduction."
    )
    
    savings = calculate_savings_breakdown(df_opt_filtered)
    
    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric("1. Potential (Identified)", f"${savings['potential_savings']:,.2f}")
    sc2.metric("2. Approved (Committed)", f"${savings['approved_savings']:,.2f}")
    sc3.metric("3. Implemented (In Verification)", f"${savings['implemented_savings']:,.2f}")
    sc4.metric("4. Realized (Verified Savings)", f"${savings['realized_savings']:,.2f}")
    
    st.markdown("---")
    
    lifecycle_df = pd.DataFrame([
        {"Stage": "1. Potential", "Amount": savings['potential_savings'], "Description": "Identified by scanner; pending architecture & engineering review."},
        {"Stage": "2. Approved", "Amount": savings['approved_savings'], "Description": "Accepted by team engineering leads; scheduled in sprint backlog."},
        {"Stage": "3. Implemented", "Amount": savings['implemented_savings'], "Description": "Resource rightsized or terminated; telemetry under observation."},
        {"Stage": "4. Realized", "Amount": savings['realized_savings'], "Description": "Confirmed spend drop on subsequent cloud billing cycles."}
    ])
    
    l_col1, l_col2 = st.columns([7, 5])
    with l_col1:
        st.markdown("##### 🚀 Savings Governance Funnel")
        fig_funnel = px.funnel(
            lifecycle_df,
            x="Amount",
            y="Stage",
            color="Stage",
            color_discrete_sequence=["#94a3b8", "#60a5fa", "#f59e0b", "#10b981"]
        )
        fig_funnel.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=300)
        st.plotly_chart(fig_funnel, use_container_width=True)
        
    with l_col2:
        st.markdown("##### Lifecycle Stage Audit Definitions")
        st.dataframe(lifecycle_df[["Stage", "Amount", "Description"]], use_container_width=True)
        st.caption("🔒 FinOps Rule: Realized savings strictly exclude unexecuted estimates.")

# ================= TAB 8: DOWNLOADABLE REPORTS =================
with tabs[7]:
    st.subheader("FinOps Analyst Reporting & Data Export")
    st.write(
        "Generate and download automated, audit-ready CSV reports for cross-functional stakeholders "
        "(Finance, Engineering leadership, and Product managers)."
    )
    
    rep_col1, rep_col2 = st.columns(2)
    
    with rep_col1:
        st.markdown("#### 1. Daily Cost & Tag Attribution Report")
        st.caption("Complete granular daily records with service, team, environment, and tagging attributes.")
        csv_billing = df_billing_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download Billing Breakdown (CSV)",
            data=csv_billing,
            file_name="cloudfinops_cost_breakdown.csv",
            mime="text/csv"
        )
        
        st.markdown("---")
        st.markdown("#### 2. Monthly Budget Variance Report")
        st.caption("Summary of team budgets, actuals, dollar variance, and threshold compliance status.")
        csv_variance = calculate_budget_variance(df_billing_filtered, df_budgets_filtered).to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download Budget Variance Report (CSV)",
            data=csv_variance,
            file_name="cloudfinops_budget_variance.csv",
            mime="text/csv"
        )
        
    with rep_col2:
        st.markdown("#### 3. Flagged Spending Anomalies Report")
        st.caption("All statistical spend surges with excess cost impact and root-cause annotations.")
        csv_anomalies = detect_cost_anomalies(df_billing_filtered).to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download Anomalies Incident Log (CSV)",
            data=csv_anomalies,
            file_name="cloudfinops_anomalies_log.csv",
            mime="text/csv"
        )
        
        st.markdown("---")
        st.markdown("#### 4. Rightsizing & Savings Opportunities Report")
        st.caption("Resource-level rightsizing recommendations, confidence tiers, and governance status.")
        csv_opt = df_opt_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download Optimization Recommendations (CSV)",
            data=csv_opt,
            file_name="cloudfinops_optimization_recommendations.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.caption("CloudFinOps AI — Cloud Cost Intelligence & Optimization Platform | Python, Streamlit, Plotly, SQLite | Designed for Cloud FinOps Analyst Portfolio")
