import streamlit as st
import pandas as pd
import numpy as np

# Import your multi-agent backend
from main import SpendIntelligenceSystem

# 1. Page Configuration
st.set_page_config(page_title="AI Spend Intelligence", layout="wide", page_icon="💰")

# --- NEW: Demo Data Generator ---
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
# ---------------------------------

# 2. Header Section
st.title("💰 AI Spend Intelligence Dashboard")
st.markdown("Upload your raw transaction data to let the Multi-Agent System detect cost leakage, forecast budget breaches, and recommend automated actions.")

# 3. Data Ingestion UI (Upload or Demo)
df = None

# Create two columns for the upload vs demo option
col_upload, col_demo = st.columns([2, 1])

with col_upload:
    uploaded_file = st.file_uploader("📂 Upload your dataset (CSV)", type=["csv"])

with col_demo:
    st.write("<br>", unsafe_allow_html=True) # Spacer to align with uploader
    st.write("**Don't have a file?**")
    if st.button("📊 Try with Demo Data", use_container_width=True):
        st.session_state["use_demo"] = True

# Logic to determine which dataframe to use
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.session_state["use_demo"] = False # Reset demo flag if a file is uploaded
elif st.session_state.get("use_demo", False):
    df = load_demo_data()
    st.info("💡 Currently using synthetic demo data. Upload a file to override this.")

# 4. Trigger the Agents (Only runs if df is successfully loaded)
if df is not None:
    # Show a quick preview of what was loaded
    with st.expander("👀 Preview Raw Data"):
        st.dataframe(df.head())

    if st.button("🚀 Run AI Agents", type="primary"):
        
        # A spinner gives great UX while the ML models run
        with st.spinner("Agents are analyzing the data..."):
            
            # Initialize and run your backend system
            system = SpendIntelligenceSystem()
            results = system.run(df)
            issues_df = results["actionable_issues"]

            st.divider()

            if issues_df.empty:
                st.success("✅ No anomalies detected! Your spend data looks clean.")
            else:
                # 5. Dashboard Rendering (KPIs)
                st.subheader("📊 Executive Summary")
                
                col1, col2, col3 = st.columns(3)
                
                total_issues = len(issues_df)
                total_savings = issues_df["Estimated_Savings"].sum()
                
                automated_actions = issues_df[issues_df["Recommended_Action"] != "Manual Review"]
                automation_rate = (len(automated_actions) / total_issues) * 100 if total_issues > 0 else 0

                col1.metric("Total Issues Detected", total_issues)
                col2.metric("Total Recoverable Savings", f"₹{total_savings:,.0f}")
                col3.metric("🤖 Automation Rate", f"{automation_rate:.1f}%")

                st.divider()

                # 6. Charts Section
                col_chart1, col_chart2 = st.columns(2)
                
                with col_chart1:
                    st.subheader("📈 Top Vendors by Cost Leakage")
                    vendor_data = issues_df.groupby("Vendor")["Estimated_Savings"].sum().sort_values(ascending=False)
                    st.bar_chart(vendor_data)

                with col_chart2:
                    st.subheader("🏢 Department-wise Leakage")
                    dept_data = issues_df.groupby("Department")["Estimated_Savings"].sum()
                    st.bar_chart(dept_data)

                # 7. Data Table
                st.subheader("📋 Actionable Issues & Agent Decisions")
                st.dataframe(issues_df, use_container_width=True)

                # 8. Execution Logs
                st.divider()
                st.subheader("🤖 Agent Execution Logs")
                st.success("✅ Data Agent → Data cleaned and validated")
                st.success("🔍 Detection Agent → Anomalies and ML patterns detected")
                st.success("🧠 Decision Agent → Corrective actions generated")
                st.info("⚡ Execution Agent → Actions queued for API execution")