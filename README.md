# 💎 Unified Enterprise Cost Intelligence & Autonomous Action Platform

**Built for the ET AI Hackathon 2026 — Problem Statement 3**

An intelligent, multi-agent orchestration platform that continuously monitors enterprise data, identifies cost anomalies, predicts operational SLA breaches, reconciles financial ledgers, and automatically initiates corrective actions within enterprise guardrails.

## 🚀 Overview

This project goes beyond traditional static dashboards. It is a proactive, autonomous control room powered by three specialized AI agents that work together to identify financial leakage and execute mitigation strategies.

- **Spend Intelligence Agent (`Cost-Anomaly-Detection/`)**: Analyzes transactional and vendor procurement data to find duplicate costs, overcharges, and anomalies, recommending instant blockers or vendor disputes.
- **SLA & Penalty Prevention Agent (`SLA/`)**: Forecasts operational service level agreement (SLA) breaches, evaluates the exact financial penalty exposure, and automates risk mitigation assignments (e.g., rerouting work).
- **Financial Operations Agent (`transection_control/`)**: Cross-references internal enterprise ledgers against bank statements to instantly reconcile transactions, flag missing payments, and calculate precise variance exposure.

The entire system is governed by an interactive Human-In-The-Loop (HITL) Streamlit dashboard, ensuring that high-risk autonomous actions (like freezing an account or blocking a payment) require admin approval, perfectly aligning with enterprise compliance workflows.

## 📁 Repository Structure

```plaintext
├── Cost-Anomaly-Detection/ # Agent for finding transactional & procurement cost leakages
├── SLA/                    # Agent for forecasting operational risks & SLA penalty prevention
├── transection_control/    # FinOps Agent for ledger vs. bank reconciliation
├── unified_app.py          # The main Streamlit HITL Control Room dashboard
├── unified_backend.py      # Master orchestrator aggregating all 3 agents into a single pipeline
├── requirements.txt        # Combined required Python packages
└── .gitignore              # Ignored files, environments, cache directories
```

## ✨ Key Features (Hackathon Evaluation Focus)

- **Quantifiable Financial Impact**: Every single anomaly, SLA breach, and missing transaction is mathematically quantified into exact ₹ INR exposure to show immediate ROI.
- **Autonomous Execution**: The system maps issues to specific actions (e.g., "Auto-Block", "Hold Ledger", "Reassign Ticket") instead of just generating reports.
- **Enterprise Approval Guardrails**: Safe actions are executed instantly, while high-impact actions are queued in a centralized HITL approval queue.
- **Deterministic & LLM Fallbacks**: Utilizes lightning-fast, rule-based heuristics and Isolation Forest Machine Learning to guarantee zero-latency execution during live demos, independent of API rate limits.

## ⚙️ Requirements and Installation

Ensure you have Python 3.8+ installed.

1. **Clone the repository**:
   ```bash
   git clone <your-repository-url>
   cd AI_agent
   ```

2. **Create a virtual environment and activate it**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables (Optional)**:
   - If utilizing the OpenAI fallback models in the SLA pipeline, copy `SLA/.env.example` to `.env` in the root and add your `OPENAI_API_KEY`. *(Note: The default demo uses deterministic routing for 100% stability).*

## 🖥️ Usage & Live Demo

Start the unified control room by executing the main Streamlit application:

```bash
streamlit run unified_app.py
```

This will launch a local server (`http://localhost:8501`) where you can:

1. **Load the Demo Dataset** (or upload your own Enterprise CSV) directly from the sidebar.
2. **Click 🚀 Run Multi-Agent Pipeline**.
3. **Watch as the master orchestrator** delegates the data to all three agents and aggregates the exact cost savings, penalty exposure, and reconciliation variance into a single pane of glass.
4. **Navigate the 4 Deep Dive Tabs** to audit individual agent findings and review the global action queue.
