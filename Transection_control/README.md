# 💰 Transaction Control Agent — Financial Reconciliation & Autonomous Execution

A complete end-to-end Python module that acts as an Autonomous Financial Operations Agent. It doesn't just find errors—it takes action.

Built for Hackathon Problem Statement 3, this agent is capable of:

- 🔍 **Multi-System Reconciliation**: Cross-referencing internal ledgers against bank statements.
- ⚠️ **Discrepancy Detection**: Finding missing transactions, amount mismatches, duplicates, and spikes.
- 🧠 **Rule-Based Root Cause Analysis**: Lightning-fast, deterministic heuristic explanations (No API latency).
- ⚡ **Autonomous Execution**: Assigning and executing corrective actions (e.g., "Auto-Block", "Hold Ledger").
- 🛡️ **Enterprise Guardrails**: Routing high-risk actions to a Human-in-the-Loop (HITL) approval queue.
- 🤖 **ML-Based Anomaly Detection**: Utilizing Isolation Forests to flag statistical outliers for fraud review.

## 📁 Project Structure

```plaintext
transection_control/
├── main.py                    ← Entry point (CLI runner)
├── data_processing.py         ← Data loading, synthetic generation, feature engineering
├── requirements.txt           ← Module-specific dependencies
├── finops_agent.py            ← Core FinOpsAgent class (The Agent Logic)
├── models/
│   └── anomaly.py             ← Isolation Forest anomaly detector
├── data/                      ← Auto-generated CSVs & Outputs
│   ├── internal_ledger.csv
│   ├── bank_statement.csv
│   └── issues_report.csv
└── logs/
    └── finops.log             ← Agent decision and execution log
```

## ⚙️ Installation

```bash
# 1. Navigate to the module directory
cd transection_control

# 2. Install dependencies
pip install -r requirements.txt
```

## 🚀 Running the Agent

**Option A — Full run (100k rows)**
```bash
python main.py
```

**Option B — Fast Demo Mode (20k rows, no ML)**
*Perfect for live hackathon presentations to guarantee instant execution.*
```bash
python main.py --rows 20000 --no-ml
```

**Option C — Custom tolerance**
```bash
python main.py --rows 50000 --tol 1.0
```

### CLI flags
| Flag | Default | Description |
|---|---|---|
| `--rows` | `100000` | Number of rows to process |
| `--no-ml` | `off` | Disable Isolation Forest |
| `--tol` | `0.50` | Amount mismatch tolerance (₹) |

## 📂 Using Real PaySim Data (Optional)

1. Download from Kaggle: PaySim Financial Dataset
2. Place the CSV at:
   ```plaintext
   transection_control/data/PS_20174392719_1491204439457_log.csv
   ```
3. Run the pipeline normally — it auto-detects the real file.

*(Note: Without the file, the system automatically generates a realistic synthetic dataset with injected anomalies so the agent always has something to find during demos).*

## 🔍 Sample Output (Action-Oriented)

```plaintext
🚀  Transaction Control Agent starting …

✅ internal_ledger.csv  →  99,700 rows
✅ bank_statement.csv   →  99,547 rows

============================================================
  🔍  RECONCILIATION SUMMARY
============================================================
  Total Transactions :     99,700
  Matched            :     95,841
  Issues Found       :      4,629
------------------------------------------------------------
  ⚠️   DISCREPANCIES & FINANCIAL EXPOSURE
------------------------------------------------------------
  Amount Mismatch               :   1,404  |  ₹    350,985.64
  Duplicate                     :     492  |  ₹  7,184,083.23
  Missing In Bank               :   2,002  |  ₹110,246,519.17
  Ml Anomaly                    :     843  |  ₹211,119,135.65
------------------------------------------------------------
  💰  Total Variance  : ₹1,320,706,953.91
============================================================

  🔔  HIGH-IMPACT AUTONOMOUS ACTIONS
  🚨 Flag: T0008684 | missing_in_bank | Action: Hold Ledger Reconciliation (EXECUTED)
  🚨 Flag: T0026465 | duplicate       | Action: Auto-Block Duplicate Payment (EXECUTED)
  🚨 Flag: T0099122 | ml_anomaly      | Action: Freeze Sender Account (PENDING ADMIN APPROVAL)
  ...
```

## 🏗️ Agent Architecture & Logic Flow

```plaintext
main.py
  └─► FinOpsAgent.run()
        ├─ load_data()          → Ingests data & injects realistic operational noise
        ├─ reconcile()          → Exact ID match + composite-key fuzzy fallback
        ├─ detect_issues()      → Balance check + ML anomaly + spike detection
        ├─ analyze_root_cause() → 1. Maps status to human-readable explanation
        │                         2. Maps status to RECOMMENDED ACTION
        │                         3. Simulates EXECUTION STATUS (Executed vs. HITL)
        ├─ calculate_impact()   → Quantifies exact ₹ variance per category
        └─ save_issues()        → Exports data/issues_report.csv for the Unified UI
```
