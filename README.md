# Hackerthorn: SLA & Cost-Leakage Control Room

An intelligent agentic pipeline that continuously monitors enterprise data, identifies cost anomalies, and estimates SLA breach risks with actionable interventions.

## Overview

This project provides a robust, real-time control room powered by AI agents to automatically find savings and mitigate SLA penalties before they happen. It unifies two core sub-systems:

1. **Cost Anomaly Detection (`Cost-Anomaly-Detection/`)**: Analyzes transactional and operational spend to find financial leaks and cost-saving opportunities.
2. **SLA Risk Assessment (`SLA/`)**: Predicts service level agreement (SLA) breaches, evaluating financial exposure and automating risk mitigation assignments.

The system features an interactive Human-In-The-Loop (HITL) Streamlit dashboard for monitoring pipelines, discovering vulnerabilities, and approving mitigating actions.

## Repository Structure

```
├── Cost-Anomaly-Detection/ # Agent for finding transactional & sub-contracting cost leakages
├── SLA/                    # Agent for forecasting operational risks & SLA breaches
├── unified_app.py          # The main Streamlit HITL dashboard
├── unified_backend.py      # Aggregates both AI agents into a single robust pipeline
├── requirements.txt        # Combined required Python packages
└── .gitignore              # Ignored files, environments, cache directories
```

## Features
- **Multi-Agent Pipeline Workflow**: Integrates both cost and SLA intelligent agents seamlessly.
- **Deep Dive Tabs**: Check issues individually with dynamic Plotly visualizations.
- **Action Queue (HITL)**: Review queued pipeline insights like Reassigning, Escalating, or Blocking Payments safely.
- **Real-Time Data Ingestion**: Load new CSV extracts directly through the sidebar and trace live anomalies out of the box.

## Requirements and Installation

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

4. **Set up environment variables**:
   - Copy `SLA/.env.example` to `.env` in the root (if applicable).
   - Add your necessary API keys (e.g., `OPENAI_API_KEY`) if requested by any of the downstream agents.

## Usage

Start the unified control room by executing the main Streamlit application:

```bash
streamlit run unified_app.py
```

This will launch a local server and give you a web interface where you can:
- Upload your Enterprise Dataset (CSV) inside the Control Room
- Run the Multi-Agent Pipeline
- View actionable cost leakage insights, SLA risk distribution, and the autonomous action queue.
