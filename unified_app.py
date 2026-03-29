from __future__ import annotations

import json
from datetime import datetime, timezone
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

from unified_backend import UnifiedEnterpriseAgent

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Hackerthorn — SLA & Cost Control Room",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Demo Data Generator ---
@st.cache_data
def load_demo_data():
    """Generates a realistic synthetic dataset with built-in anomalies."""
    np.random.seed(42)
    n = 500
    rng = pd.date_range("2024-01-01", periods=n, freq="D")
    df = pd.DataFrame({
        "Transaction_ID": [f"TXN{1000 + i}" for i in range(n)],
        "Vendor": np.random.choice(["AWS", "Salesforce", "Oracle", "Zoom", "Slack", "Adobe", "Microsoft"], n),
        "Category": np.random.choice(["Cloud", "SaaS", "Infra", "Marketing", "HR"], n),
        "Amount": np.round(np.random.exponential(scale=5000, size=n), 2),
        "Date": np.random.choice(rng, n),
        "Department": np.random.choice(["Engineering", "Sales", "HR", "Marketing", "Finance"], n),
    })
    
    # Plant obvious anomalies for the AI to find
    # 1. Duplicate payments
    df.loc[5:7, ["Vendor", "Amount", "Date"]] = df.loc[0, ["Vendor", "Amount", "Date"]] 
    # 2. High spend outliers
    df.loc[10, "Amount"] = 280_000 
    df.loc[45, "Amount"] = 195_000
    
    return df

# --- 2. Session State (Keeps data alive while clicking tabs) ---
if "pipeline_run" not in st.session_state:
    st.session_state.pipeline_run = False
if "raw_data" not in st.session_state:
    st.session_state.raw_data = None
if "spend_issues" not in st.session_state:
    st.session_state.spend_issues = pd.DataFrame()
if "sla_df" not in st.session_state:
    st.session_state.sla_df = pd.DataFrame()
if "sla_manifest" not in st.session_state:
    st.session_state.sla_manifest = {}
if "totals" not in st.session_state:
    st.session_state.totals = {"cost": 0, "sla": 0, "combined": 0}

# --- 3. Sidebar: Live Data Ingestion ---
st.sidebar.title("Control Room")

# Option A: Load Demo Data
if st.sidebar.button("Load Demo Dataset"):
    st.session_state.raw_data = load_demo_data()
    st.session_state.pipeline_run = False # Reset pipeline if new data loaded

# Option B: Upload CSV
uploaded_file = st.sidebar.file_uploader("Or Upload Enterprise Dataset (CSV)", type=["csv"])
if uploaded_file is not None:
    st.session_state.raw_data = pd.read_csv(uploaded_file)
    st.session_state.pipeline_run = False # Reset pipeline if new data loaded

# If data is loaded (either demo or uploaded), show the Run button
if st.session_state.raw_data is not None:
    spend_df = st.session_state.raw_data
    st.sidebar.success(f"Loaded {len(spend_df)} rows.")
    
    if st.sidebar.button("Run Multi-Agent Pipeline", type="primary"):
        with st.spinner("Agents are analyzing cost leakage & SLA risks..."):
            # Run your backend agent
            agent = UnifiedEnterpriseAgent()
            results = agent.run(spend_df)
            
            # Save results to session state
            st.session_state.spend_issues = results["spend_results"]["actionable_issues"]
            st.session_state.sla_df = results["sla_results"]["results_df"]
            st.session_state.sla_manifest = results["sla_results"]["manifest"]
            
            st.session_state.totals["cost"] = results.get('total_cost_savings', 0)
            st.session_state.totals["sla"] = results.get('total_sla_prevention', 0)
            st.session_state.totals["combined"] = results.get('total_combined_impact', 0)
            
            st.session_state.pipeline_run = True

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Continuous monitoring:** Upload daily extracts to simulate real-time agent routing and corrective action."
)

# --- 4. Main Dashboard Header ---
st.title("Hackerthorn SLA & Cost-Leakage Control Room")
st.caption("AI that continuously monitors data, identifies cost leakage, and initiates corrective actions.")

if not st.session_state.pipeline_run:
    st.info("👈 Please load the demo dataset or upload a CSV, then run the pipeline from the sidebar to populate the control room.")
    st.stop()

# --- 5. Extract Data for Visuals ---
df = st.session_state.sla_df
spend_issues = st.session_state.spend_issues
m = st.session_state.sla_manifest

# SLA calculations
if "predicted_breach" in df.columns:
    at_risk = df[df["predicted_breach"] == 1].copy()
    safe_n = int((df["predicted_breach"] == 0).sum())
else:
    at_risk = pd.DataFrame()
    safe_n = 0

risk_n = len(at_risk)
exposure = float(pd.to_numeric(df.get("financial_exposure_ev", 0), errors="coerce").fillna(0).sum())
prevention = float(pd.to_numeric(df.get("prevention_value_estimate", 0), errors="coerce").fillna(0).sum())

# --- 6. Top-Level Impact Metrics ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Tasks SAFE", f"{safe_n:,}")
c2.metric("Tasks AT RISK", f"{risk_n:,}")
c3.metric("Expected Penalty Exposure", f"₹{exposure:,.0f}")
c4.metric("Cost Leakage Prevented", f"₹{st.session_state.totals['cost']:,.0f}")

if m:
    st.success(f"Last pipeline run (UTC): **{m.get('run_at_utc', datetime.now(timezone.utc).strftime('%H:%M:%S'))}** · LLM-deep rows: **{m.get('genai_llm_rows', 0)}**")

# --- 7. Deep Dive Tabs ---
tab_a, tab_b, tab_c = st.tabs(["Cost Intelligence", "SLA Risk Distribution", "Automation Action Queue"])

# TAB A: Cost Intelligence
with tab_a:
    st.subheader("Detected Cost Leakage & Anomalies")
    if not spend_issues.empty:
        st.dataframe(spend_issues, use_container_width=True, height=300)
        
        if "Department" in spend_issues.columns and "Estimated_Savings" in spend_issues.columns:
            fig_spend = px.bar(
                spend_issues, 
                x="Department", 
                y="Estimated_Savings", 
                color="Issue_Type", 
                title="Potential Savings by Department"
            )
            st.plotly_chart(fig_spend, use_container_width=True)
    else:
        st.write("No cost anomalies detected in this batch.")

# TAB B: SLA Risk Overview
with tab_b:
    st.subheader("Risk Concentration")
    colx, coly = st.columns(2)
    with colx:
        if "automation_action" in at_risk.columns and not at_risk.empty:
            ap = at_risk["automation_action"].value_counts().reset_index()
            ap.columns = ["action", "count"]
            fig = px.bar(ap, x="action", y="count", title="Automation mix (at-risk only)")
            st.plotly_chart(fig, use_container_width=True)
    with coly:
        if "assigned_to" in at_risk.columns and not at_risk.empty:
            owners = at_risk.groupby("assigned_to").size().reset_index(name="at_risk")
            owners = owners.sort_values("at_risk", ascending=False).head(12)
            fig2 = px.bar(owners, x="assigned_to", y="at_risk", title="At-risk workload by current owner")
            st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Probability vs Penalty")
    if not at_risk.empty and "probability" in at_risk.columns and "penalty_cost" in at_risk.columns:
        scat = at_risk.copy()
        scat["penalty_cost"] = pd.to_numeric(scat["penalty_cost"], errors="coerce")
        fig3 = px.scatter(
            scat,
            x="probability",
            y="penalty_cost",
            color="automation_action" if "automation_action" in scat.columns else None,
            title="Model confidence × contractual penalty",
        )
        st.plotly_chart(fig3, use_container_width=True)

# TAB C: Action Queue (HITL)
with tab_c:
    st.markdown("### Human-in-the-Loop Approval Queue")
    st.caption("Review queued REASSIGN, ESCALATE, and BLOCK PAYMENT pathways before execution.")
    
    st.write("**Cost Agent Queue**")
    if not spend_issues.empty:
        st.dataframe(spend_issues[["Transaction_ID", "Issue_Type", "Recommended_Action", "Estimated_Savings", "Auto_Action"]], use_container_width=True)
    
    st.write("**SLA Agent Queue**")
    if not at_risk.empty:
        cols_to_show = [c for c in ["assigned_to", "probability", "financial_exposure_ev", "automation_action", "AI_Insight"] if c in at_risk.columns]
        st.dataframe(at_risk[cols_to_show], use_container_width=True)