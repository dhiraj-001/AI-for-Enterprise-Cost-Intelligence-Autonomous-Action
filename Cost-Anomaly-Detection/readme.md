# AI Spend Intelligence System 💰

## 🚨 Key Capabilities

- **Duplicate payments**
  - High spend anomalies  
  - ML-based risk detection

- 💰 **Cost Optimization**
  - Estimated savings per issue
  - Vendor-level leakage insights

- 🤖 **Autonomous Actions (Simulated)**
  - Auto-blocking risky transactions
  - High-priority escalation
  - Monitoring low-risk items

- 📈 **Forecasting**
  - Predict future enterprise spend
  - Identify budget risks early

- 🧪 **Demo Mode**
  - Run system instantly using synthetic data

## 📁 Project Structure

├── main.py # Core multi-agent backend system
├── app.py # Streamlit dashboard (UI layer)
├── enterprise_cost_dataset.csv # Sample input dataset
├── actionable_leakage_targets.csv # Output report
├── SLA/ # SLA configs / docs
├── .gitignore # Ignore data & env files

> ⚠️ Note: Prototyping notebooks (`.ipynb`) are deprecated.

## ⚙️ Installation

### 🔹 1. Clone the repository

```bash
git clone https://github.com/your-username/ai-spend-intelligence.git
cd ai-spend-intelligence
```

### 🔹 2. Create virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
```

### 🔹 3. Install dependencies
```bash
pip install pandas numpy scikit-learn streamlit
```

## ▶️ Usage

### 🔹 1. Run Interactive Dashboard (Recommended)
```bash
streamlit run app.py
```
**Features:**
- Upload your dataset 📂
- Click \"Run AI Agents\" 🚀  
- View insights instantly

### 🔹 2. Run Backend via CLI
```bash
python main.py
```

**This will:**
- Process dataset
- Detect anomalies
- Generate report
- Export results to:
  - `actionable_leakage_targets.csv`

## 📊 Output Example

Each flagged transaction includes:

| Transaction ID | Vendor | Department | Amount | Issue Type | ML Risk Score | Recommended Action | Estimated Savings | Auto Action (execution simulation) |
|---|---|---|---|---|---|---|---|---|
| ... | ... | ... | ... | Duplicate | 0.95 | Block | $5,200 | ✅ Simulated |

## 🧠 How It Works

```
Raw Data
   ↓
Data Processor Agent  
   ↓
Intelligence Detector Agent
   ↓
Forecasting Agent
   ↓
Decision & Execution Agent
   ↓
Dashboard Visualization
```

## 🏆 Use Cases
- Enterprise cost optimization
- Procurement intelligence
- Financial anomaly detection
- Vendor contract analysis
- Budget forecasting

## 📌 Future Improvements
- Real-time data pipeline integration (Kafka / APIs)
- LLM-based decision explanations
- Reinforcement learning for action optimization
- Role-based dashboards (Finance, Procurement)
- Alerting system (Slack/Email integration)

## 🤝 Contributing
Contributions are welcome! Feel free to fork the repo and submit a PR.

## 📄 License
This project is licensed under the MIT License.

## 👨‍💻 Author
**Dhiraj Gogoi**  
B.Tech CSE | Full Stack Developer | AI Enthusiast

## ⭐ Final Note
This project demonstrates how AI agents can autonomously **detect, decide, and act** on enterprise cost inefficiencies, delivering measurable business value.

💡 **Not just insights — actionable intelligence.**

---


