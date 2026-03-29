import os
import sys
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ── Paths ───────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinOps Agent | Premium Dashboard",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS for Premium Look ──────────────────────────────────────────────
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

# ── Data Helpers ────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    issues = pd.read_csv("data/issues_report.csv") if os.path.exists("data/issues_report.csv") else pd.DataFrame()
    ledger = pd.read_csv("data/internal_ledger.csv") if os.path.exists("data/internal_ledger.csv") else pd.DataFrame()
    return issues, ledger

def fmt_inr(val):
    return f"₹{float(val):,.2f}"

def calculate_accurate_variance(issues_df):
    """Calculates true variance (handling mismatches correctly)."""
    if issues_df.empty:
        return 0
    # If the backend saved impact_inr, use it. Otherwise, calculate on the fly.
    if "impact_inr" in issues_df.columns:
        return issues_df["impact_inr"].sum()
    
    impact = np.where(
        issues_df["status"] == "amount_mismatch",
        issues_df.get("amount_variance", 0).fillna(0),
        issues_df.get("amount", 0).fillna(0)
    )
    return impact.sum()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/diamond.png", width=60)
    st.title("FinOps Agent")
    st.caption("v2.0 • Autonomous Cost Intelligence")
    
    st.divider()
    if st.button("🚀 Run AI Pipeline", type="primary", use_container_width=True):
        with st.spinner("Agent analyzing and executing actions..."):
            from finops_agent import FinOpsAgent
            agent = FinOpsAgent(n_rows=20000)
            agent.run()
            st.cache_data.clear()
            st.experimental_rerun()

    st.divider()
    st.subheader("Configuration")
    confidence_threshold = st.slider("Anomaly Confidence", 0.0, 1.0, 0.8)
    period_filter = st.multiselect("Select Period", ["January", "February", "March"], default=["January", "February", "March"])

# ── Load State ─────────────────────────────────────────────────────────────
issues_df, ledger_df = load_data()

if issues_df.empty:
    st.info("👋 Welcome! Please run the pipeline in the sidebar to begin analysis.")
    st.stop()

# ── Header ──────────────────────────────────────────────────────────────────
st.title("Autonomous Reconciliation Dashboard")
st.markdown("---")

# ── KPI Row ─────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

total_var = calculate_accurate_variance(issues_df)
auto_actions = len(issues_df[issues_df.get("execution_status", "") == "EXECUTED"]) if "execution_status" in issues_df.columns else 0

with c1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Total Transactions", f"{len(ledger_df):,}", delta=None)
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Detected Issues", f"{len(issues_df):,}", delta=f"{len(issues_df)/len(ledger_df)*100:.1f}%", delta_color="inverse")
    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Financial Exposure", fmt_inr(total_var), delta="Critical", delta_color="inverse")
    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Autonomous Actions Executed", f"{auto_actions}", delta="Resolved Instantly")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Dynamic AI Insights Section ─────────────────────────────────────────────
st.subheader("💎 Agent Strategic Insights")
with st.container():
    st.markdown('<div class="ai-panel">', unsafe_allow_html=True)
    
    # Dynamically generate the narrative based on actual data
    top_issue_type = issues_df["status"].mode()[0].replace('_', ' ').title() if not issues_df.empty else "Unknown"
    highest_val = issues_df["amount"].max() if not issues_df.empty else 0
    
    dynamic_narrative = (
        f"### Actionable Financial Intelligence\n"
        f"The Autonomous FinOps Agent has processed the latest transaction batch. "
        f"We identified **{len(issues_df):,} discrepancies** resulting in a total financial exposure of **{fmt_inr(total_var)}**.\n\n"
        f"**Primary Bottleneck:** The most frequent anomaly detected is **{top_issue_type}**. "
        f"The single highest-risk transaction flagged is valued at **{fmt_inr(highest_val)}**.\n\n"
        f"**System Actions Taken:**\n"
        f"1. **{auto_actions} actions** were executed autonomously (e.g., Auto-Blocking duplicates).\n"
        f"2. High-value anomalies and ML-flagged fraud risks have been routed to the pending queue for Admin approval."
    )
    
    st.markdown(dynamic_narrative)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Visual Analytics ────────────────────────────────────────────────────────
col_l, col_r = st.columns([2, 1])

with col_l:
    st.subheader("📈 MoM Variance Trends")
    if "month" in ledger_df.columns:
        monthly_data = ledger_df.groupby("month")[["amount", "budget_amount"]].sum().reindex(["January", "February", "March"])
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Actual', x=monthly_data.index, y=monthly_data['amount'], marker_color='#4DABF7'))
        fig.add_trace(go.Bar(name='Budget', x=monthly_data.index, y=monthly_data['budget_amount'], marker_color='rgba(255,255,255,0.2)'))
        fig.update_layout(
            barmode='group', 
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

with col_r:
    st.subheader("🎯 Issue Distribution")
    dist = issues_df["status"].value_counts().reset_index()
    dist.columns = ["Status", "Count"]
    fig_pie = px.pie(dist, values="Count", names="Status", hole=0.6, 
                    color_discrete_sequence=px.colors.sequential.RdBu)
    fig_pie.update_layout(
        showlegend=False, 
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ── Transaction Explorer ─────────────────────────────────────────────────────
st.subheader("🔍 Transaction Intelligence & Action Queue")
st.caption("Review the agent's findings and autonomous actions below.")

selected_status = st.selectbox("Focus Area", ["All Issues"] + list(issues_df["status"].unique()))
if selected_status != "All Issues":
    filtered_df = issues_df[issues_df["status"] == selected_status]
else:
    filtered_df = issues_df

# Display dataframe with the new action columns highlighted
cols_to_show = ["transaction_id", "status", "amount", "recommended_action", "execution_status", "genai_insight"]
available_cols = [c for c in cols_to_show if c in filtered_df.columns]

st.dataframe(
    filtered_df[available_cols].sort_values("amount", ascending=False).head(100),
    use_container_width=True,
    column_config={
        "amount": st.column_config.NumberColumn("Amount", format="₹%d"),
        "status": st.column_config.TextColumn("Discrepancy Type"),
        "recommended_action": st.column_config.TextColumn("Agent Action Taken"),
        "execution_status": st.column_config.TextColumn("Status"),
        "genai_insight": st.column_config.TextColumn("Agent Assessment", width="large")
    }
)

st.divider()
st.caption("FinOps Agent Platform • Fully Autonomous Execution • v2.0")