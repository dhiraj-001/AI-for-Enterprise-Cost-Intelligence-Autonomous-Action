from __future__ import annotations

import json
from datetime import datetime, timezone
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from unified_backend import UnifiedEnterpriseAgent

# --- 1. Page Configuration & Premium CSS ---
st.set_page_config(
    page_title="Hackerthorn — SLA & Cost Control Room",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at top right, #1a1c23, #0e1117);
    }

    /* Glassmorphism sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* KPI Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.08);
        border-color: #4DABF7;
    }

    /* AI Panel */
    .ai-panel {
        background: linear-gradient(135deg, rgba(63, 94, 251, 0.1) 0%, rgba(252, 70, 107, 0.1) 100%);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin-bottom: 30px;
    }

    h1, h2, h3 {
        color: #ffffff;
        font-weight: 700 !important;
    }

    .stMetric label {
        color: #adb5bd !important;
        font-size: 14px !important;
    }
</style>
""", unsafe_allow_html=True)

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
    df.loc[5:7, ["Vendor", "Amount", "Date"]] = df.loc[0, ["Vendor", "Amount", "Date"]] 
    df.loc[10, "Amount"] = 280_000 
    df.loc[45, "Amount"] = 195_000
    return df

# --- 2. Session State ---
if "pipeline_run" not in st.session_state:
    st.session_state.pipeline_run = False
if "raw_data" not in st.session_state:
    st.session_state.raw_data = None
if "spend_issues" not in st.session_state:
    st.session_state.spend_issues = pd.DataFrame()
if "sla_df" not in st.session_state:
    st.session_state.sla_df = pd.DataFrame()
if "finops_results" not in st.session_state:
    st.session_state.finops_results = {}
if "sla_manifest" not in st.session_state:
    st.session_state.sla_manifest = {}
if "totals" not in st.session_state:
    st.session_state.totals = {"cost": 0, "sla": 0, "finops_variance": 0, "combined": 0}

# --- 3. Sidebar: Live Data Ingestion ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/diamond.png", width=60)
    st.title("Control Room")
    st.caption("v3.0 • Unified Enterprise Intelligence")
    st.divider()

    # Option A: Load Demo Data
    if st.button("Load Demo Dataset"):
        st.session_state.raw_data = load_demo_data()
        st.session_state.pipeline_run = False 

    # Option B: Upload CSV
    uploaded_file = st.file_uploader("Or Upload Dataset (CSV)", type=["csv"])
    if uploaded_file is not None:
        st.session_state.raw_data = pd.read_csv(uploaded_file)
        st.session_state.pipeline_run = False 

    # Run Button
    if st.session_state.raw_data is not None:
        spend_df = st.session_state.raw_data
        st.success(f"Loaded {len(spend_df)} rows.")
        
        if st.button("🚀 Run Multi-Agent Pipeline", type="primary", use_container_width=True):
            with st.spinner("Agents are analyzing cost leakage, SLA risks, & reconciling ledgers..."):
                agent = UnifiedEnterpriseAgent()
                results = agent.run(spend_df)
                
                st.session_state.spend_issues = results["spend_results"]["actionable_issues"]
                st.session_state.sla_df = results["sla_results"]["results_df"]
                st.session_state.finops_results = results.get("finops_results", {})
                st.session_state.sla_manifest = results["sla_results"]["manifest"]
                
                st.session_state.totals["cost"] = results.get('total_cost_savings', 0)
                st.session_state.totals["sla"] = results.get('total_sla_prevention', 0)
                st.session_state.totals["finops_variance"] = results.get('finops_variance', 0)
                st.session_state.totals["combined"] = results.get('total_combined_impact', 0)
                
                st.session_state.pipeline_run = True

    st.divider()
    st.markdown("**Continuous monitoring:** Upload daily extracts to simulate real-time agent routing and corrective action.")

# --- 4. Main Dashboard Header ---
st.title("Autonomous SLA & Cost Control Room")
st.markdown("---")

if not st.session_state.pipeline_run:
    st.info("👋 Welcome! Please load the demo dataset or upload a CSV in the sidebar, then run the pipeline to populate the dashboard.")
    st.stop()

# --- 5. Extract Data for Visuals ---
df = st.session_state.sla_df
spend_issues = st.session_state.spend_issues
finops_data = st.session_state.finops_results.get("issues", pd.DataFrame())
m = st.session_state.sla_manifest

if "predicted_breach" in df.columns:
    at_risk = df[df["predicted_breach"] == 1].copy()
    safe_n = int((df["predicted_breach"] == 0).sum())
else:
    at_risk = pd.DataFrame()
    safe_n = 0

risk_n = len(at_risk)
exposure = float(pd.to_numeric(df.get("financial_exposure_ev", 0), errors="coerce").fillna(0).sum())
cost_prevented = st.session_state.totals['cost']
finops_variance = st.session_state.totals['finops_variance']

# Count pending human-in-the-loop actions
queued_actions = len(spend_issues) + len(at_risk) + len(finops_data)

# --- 6. KPI Row (Premium Style) ---
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("SLA Penalty Exposure", f"₹{exposure:,.0f}", delta=f"{risk_n} Tasks at Risk", delta_color="inverse")
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Cost Leakage Prevented", f"₹{cost_prevented:,.0f}", delta="Agent Recovered")
    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Reconciliation Variance", f"₹{finops_variance:,.0f}", delta="Financial Discrepancy", delta_color="inverse")
    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Queued Actions (HITL)", f"{queued_actions:,}", delta="Awaiting Approval", delta_color="off")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 7. Dynamic AI Insights Section ---
with st.container():
    st.markdown('<div class="ai-panel">', unsafe_allow_html=True)
    top_issue = spend_issues["Issue_Type"].mode()[0] if not spend_issues.empty else "N/A"
    
    dynamic_narrative = (
        f"### Actionable Enterprise Intelligence\n"
        f"The Unified Multi-Agent System has successfully processed the operational and financial batches.\n\n"
        f"**1. Spend Intelligence:** Identified **{len(spend_issues)} cost leakage anomalies** (Primary driver: **{top_issue}**) "
        f"resulting in **₹{cost_prevented:,.0f}** of recovered value.\n"
        f"**2. Operations SLA:** Flagged **{risk_n} tasks at risk of breach**, representing **₹{exposure:,.0f}** in potential penalties.\n"
        f"**3. Financial Operations:** Reconciled internal ledgers with bank statements, catching **₹{finops_variance:,.0f}** in variance exposure.\n\n"
        f"All high-risk paths have been routed to the pending Human-in-the-Loop queue."
    )
    
    st.markdown(dynamic_narrative)
    if m:
        st.caption(f"Last pipeline run (UTC): {m.get('run_at_utc', datetime.now(timezone.utc).strftime('%H:%M:%S'))}")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 8. Deep Dive Tabs ---
# NOW WITH 4 TABS TO SHOW ALL 3 AGENTS!
tab_a, tab_b, tab_c, tab_d = st.tabs([
    "🛒 Spend Intelligence", 
    "⚠️ SLA Operations", 
    "🏦 Financial Reconciliation", 
    "🤖 Global Action Queue"
])

# TAB A: Cost Intelligence
with tab_a:
    st.subheader("Detected Procurement Leakage & Anomalies")
    if not spend_issues.empty:
        st.dataframe(spend_issues, use_container_width=True, height=300)
        
        if "Department" in spend_issues.columns and "Estimated_Savings" in spend_issues.columns:
            fig_spend = px.bar(
                spend_issues, x="Department", y="Estimated_Savings", color="Issue_Type", 
                title="Potential Savings by Department", template="plotly_dark"
            )
            fig_spend.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_spend, use_container_width=True)
    else:
        st.info("No cost anomalies detected in this batch.")

# TAB B: SLA Risk Overview
with tab_b:
    st.subheader("Operational SLA Risk Concentration")
    colx, coly = st.columns(2)
    with colx:
        if "automation_action" in at_risk.columns and not at_risk.empty:
            ap = at_risk["automation_action"].value_counts().reset_index()
            ap.columns = ["action", "count"]
            fig = px.bar(ap, x="action", y="count", title="Automation mix (at-risk only)", template="plotly_dark")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    with coly:
        if "assigned_to" in at_risk.columns and not at_risk.empty:
            owners = at_risk.groupby("assigned_to").size().reset_index(name="at_risk")
            owners = owners.sort_values("at_risk", ascending=False).head(12)
            fig2 = px.bar(owners, x="assigned_to", y="at_risk", title="At-risk workload by current owner", template="plotly_dark")
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, use_container_width=True)

# TAB C: Financial Operations (FinOps Agent)
with tab_c:
    st.subheader("Ledger vs. Bank Reconciliation")
    st.markdown("Identifies missing transactions, amount mismatches, duplicate entries, and statistical anomalies.")
    
    if not finops_data.empty:
        cols = ["transaction_id", "status", "amount", "root_cause", "recommended_action", "execution_status"]
        available = [c for c in cols if c in finops_data.columns]
        st.dataframe(finops_data[available], use_container_width=True, height=350)
    else:
        st.info("No reconciliation discrepancies found in this run.")

# TAB D: Action Queue (HITL)
with tab_d:
    st.markdown("### Human-in-the-Loop Approval Queue")
    st.caption("Review queued pathways across all three systems before executing autonomous actions.")
    
    st.write("**1. Procurement/Spend Interventions**")
    if not spend_issues.empty:
        st.dataframe(
            spend_issues[["Transaction_ID", "Issue_Type", "Recommended_Action", "Estimated_Savings", "Auto_Action"]], 
            use_container_width=True
        )
    
    st.write("**2. Operational SLA Interventions**")
    if not at_risk.empty:
        cols_to_show = [c for c in ["assigned_to", "probability", "financial_exposure_ev", "automation_action", "AI_Insight"] if c in at_risk.columns]
        st.dataframe(at_risk[cols_to_show], use_container_width=True)

    st.write("**3. Financial Reconciliation Actions**")
    if not finops_data.empty:
        f_cols = ["transaction_id", "status", "recommended_action", "execution_status"]
        f_avail = [c for c in f_cols if c in finops_data.columns]
        st.dataframe(finops_data[f_avail], use_container_width=True)