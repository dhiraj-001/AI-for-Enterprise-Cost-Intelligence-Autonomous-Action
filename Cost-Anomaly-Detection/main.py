import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings("ignore")


## verify the file path 

df = pd.read_csv('/home/dhiraj/python DS/hackathon/AI_agent/Cost-Anomaly-Detection/enterprise_cost_dataset.csv')



# ─────────────────────────────────────────────────────────────────────────────
# AGENT 1: DATA PROCESSOR (The Gatekeeper & Health Monitor)
# ─────────────────────────────────────────────────────────────────────────────
class DataProcessor:
    """Cleans data and monitors for process drift (e.g., missing fields)."""
    
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = [c.strip().replace(" ", "_") for c in df.columns]
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

        before = len(df)
        df.dropna(subset=["Transaction_ID", "Amount", "Date"], inplace=True)
        if before - len(df) > 0:
            print(f"  [Data Agent] Warning: Dropped {before - len(df)} corrupted rows. Pipeline health degraded.")

        for col in ["Vendor", "Category", "Department"]:
            if col in df.columns:
                df[col].fillna("Unknown", inplace=True)

        df.drop_duplicates(inplace=True)
        return df.reset_index(drop=True)

# ─────────────────────────────────────────────────────────────────────────────
# AGENT 2: INTELLIGENCE DETECTOR (The ML Detective)
# ─────────────────────────────────────────────────────────────────────────────
class IntelligenceDetector:
    """Combines Rule-based, Unsupervised (Isolation Forest), and Supervised (Random Forest) AI."""
    
    def __init__(self, contamination: float = 0.05):
        self.contamination = contamination

    def detect(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # 1. Rule-Based: High Spend Threshold (95th percentile per category)
        df["Category_Threshold"] = df.groupby("Category")["Amount"].transform(lambda x: x.quantile(0.95))
        df["is_high_spend"] = (df["Amount"] > df["Category_Threshold"]).astype(int)
        
        # 2. Rule-Based: Exact Duplicates
        key = ["Vendor", "Amount", "Date"]
        df["is_duplicate"] = (df.duplicated(subset=key, keep="first") & df.duplicated(subset=key, keep=False)).astype(int)

        # 3. Unsupervised ML: Isolation Forest
        iso_forest = IsolationForest(contamination=self.contamination, random_state=42)
        df["iso_anomaly"] = iso_forest.fit_predict(df[["Amount"]].values)
        df["iso_anomaly"] = df["iso_anomaly"].map({-1: 1, 1: 0}) # 1 = Anomaly

        # 4. Feature Engineering (ADD THIS)
        df["day_of_week"] = df["Date"].dt.dayofweek
        df["month"] = df["Date"].dt.month
        df["vendor_freq"] = df.groupby("Vendor")["Transaction_ID"].transform("count")

        # 4. Supervised ML: Random Forest Risk Scorer
        # We use the strict 'is_high_spend' as our initial ground truth to train the model to find deeper categorical patterns
        features = [
            "Amount",
            "day_of_week",
            "month",
            "vendor_freq",
            "Vendor",
            "Department",
            "Category"
        ]
        available_features = [f for f in features if f in df.columns]
        
        X = pd.get_dummies(df[available_features])
        y = df["is_high_spend"]
        
        # Train Random Forest
        rf_model = RandomForestClassifier(min_samples_split=10, random_state=42)
        rf_model.fit(X, y)
        df["ML_Risk_Score"] = rf_model.predict_proba(X)[:, 1]

        df["Issue_Type"] = "None"

        df.loc[df["is_duplicate"] == 1, "Issue_Type"] = "Duplicate Payment"
        df.loc[df["is_high_spend"] == 1, "Issue_Type"] = "Category Overspend"
        df.loc[df["iso_anomaly"] == 1, "Issue_Type"] = "Statistical Outlier (Isolation Forest)"
        df.loc[df["ML_Risk_Score"] > 0.75, "Issue_Type"] = "High ML Risk (Pattern)"
        
        anomalies = df[df["Issue_Type"] != "None"].copy()
        
        print(f"  [Intelligence Agent] Detected {len(anomalies)} anomalies across {len(df)} transactions.")
        return anomalies.drop(columns=["Category_Threshold", "is_high_spend", "is_duplicate", "iso_anomaly"])

# ─────────────────────────────────────────────────────────────────────────────
# AGENT 3: FORECASTING ENGINE (The Predictor)
# ─────────────────────────────────────────────────────────────────────────────
class ForecastingAgent:
    """Predicts future spend using Linear Regression to warn of budget breaches."""
    
    def forecast(self, df: pd.DataFrame, days: int = 30) -> dict:
        daily_spend = df.groupby("Date")["Amount"].sum().reset_index()
        daily_spend = daily_spend.sort_values("Date")
        daily_spend["day_num"] = np.arange(len(daily_spend))

        X = daily_spend[["day_num"]]
        y = daily_spend["Amount"]

        model = LinearRegression()
        model.fit(X, y)

        future_X = np.arange(len(daily_spend), len(daily_spend) + days).reshape(-1, 1)
        predictions = model.predict(future_X)
        
        total_predicted_spend = predictions.sum()
        
        print(f"  [Forecasting Agent] Projected 30-day spend: ₹{total_predicted_spend:,.2f}")
        return {
            "model": model,
            "projected_30d_spend": total_predicted_spend,
            "trend": "Upward" if model.coef_[0] > 0 else "Downward"
        }

# ─────────────────────────────────────────────────────────────────────────────
# AGENT 4: DECISION & EXECUTION ENGINE (The Fixer)
# ─────────────────────────────────────────────────────────────────────────────
class DecisionEngine:
    """Assigns autonomous actions and calculates recoverable financial impact."""
    
    ACTION_MAP = {
        "Duplicate Payment":                      ("Block Payment via API", 1.00),
        "Category Overspend":                     ("Alert Department Head", 0.15),
        "Statistical Outlier (Isolation Forest)": ("Flag for Audit", 0.10),
        "High ML Risk (Pattern)":                 ("Investigate Vendor", 0.20),
    }

    def apply(self, anomalies: pd.DataFrame) -> pd.DataFrame:
        if anomalies.empty:
            return pd.DataFrame()

        def get_action(issue):
            return self.ACTION_MAP.get(issue, ("Manual Review", 0.05))[0]

        def get_savings(row):
            _, rate = self.ACTION_MAP.get(row["Issue_Type"], ("Manual Review", 0.05))
            return round(row["Amount"] * rate, 2)

        results = anomalies.copy()
        def auto_action(row):
            if row["Issue_Type"] == "Duplicate Payment":
                return "AUTO-BLOCKED"
            elif row.get("ML_Risk_Score", 0) > 0.8:
                return "HIGH PRIORITY REVIEW"
            else:
                return "Monitor"

        results["Auto_Action"] = results.apply(auto_action, axis=1)
        results["Recommended_Action"] = results["Issue_Type"].apply(get_action)
        results["Estimated_Savings"]  = results.apply(get_savings, axis=1)

        # Reorder columns for clean reporting
        cols = ["Transaction_ID", "Date", "Vendor", "Department", "Amount", "Issue_Type", "ML_Risk_Score", "Recommended_Action", "Estimated_Savings","Auto_Action"]
        available_cols = [c for c in cols if c in results.columns]
        
        print(f"  [Decision Agent] Mapped {len(results)} actions. Potential savings: ₹{results['Estimated_Savings'].sum():,.2f}")
        return results[available_cols].sort_values(by="Estimated_Savings", ascending=False)


class ExecutionAgent:
    """Executes actions automatically (simulated for MVP)."""

    def execute(self, issues_df: pd.DataFrame) -> pd.DataFrame:
        if issues_df.empty:
            return issues_df
        
        def execute_action(row):
            if row["Issue_Type"] == "Duplicate Payment":
                return "Payment Blocked"
            elif row["Issue_Type"] == "Category Overspend":
                return "Alert Sent to Manager"
            elif row["Issue_Type"] == "High ML Risk (Pattern)":
                return "Vendor Flagged for Review"
            else:
                return "Logged for Monitoring"
        
        issues_df["Execution_Status"] = issues_df.apply(execute_action, axis=1)
        
        print(f"  [Execution Agent] Executed {len(issues_df)} automated actions.")
        return issues_df



# ─────────────────────────────────────────────────────────────────────────────
# ORCHESTRATOR: AI SPEND INTELLIGENCE SYSTEM
# ─────────────────────────────────────────────────────────────────────────────
class SpendIntelligenceSystem:
    def __init__(self):
        self.processor   = DataProcessor()
        self.detector    = IntelligenceDetector()
        self.forecaster  = ForecastingAgent()
        self.engine      = DecisionEngine()
        self.executor = ExecutionAgent()

    def run(self, raw_df: pd.DataFrame) -> dict:
        print("\n" + "═"*60)
        print("🚀 INIT: AI SPEND INTELLIGENCE SYSTEM")
        print("═"*60)

        clean_df  = self.processor.process(raw_df)
        anomalies = self.detector.detect(clean_df)
        forecast  = self.forecaster.forecast(clean_df)
        issues_df = self.engine.apply(anomalies)
        issues_df = self.engine.apply(anomalies)
        issues_df = self.executor.execute(issues_df)

        # Step 3: Automation Rate
        automation_rate = (
            (issues_df["Execution_Status"] != "Logged for Monitoring").sum() / len(issues_df)
        ) * 100

        print(f"🤖 Automation Rate: {automation_rate:.2f}%")

        print("\n✅ SYSTEM RUN COMPLETE. Summary generated.\n")
        
        return {
            "clean_data": clean_df,
            "actionable_issues": issues_df,
            "forecast_metrics": forecast
        }




# ─────────────────────────────────────────────────────────────────────────────
# EXECUTION
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Assuming 'df' is your existing raw dataframe in your environment
    if 'df' in locals():
        system = SpendIntelligenceSystem()
        results = system.run(df)
        
        final_output = results["actionable_issues"][
            [
                "Transaction_ID",
                "Vendor",
                "Department",
                "Amount",
                "Issue_Type",
                "ML_Risk_Score",
                "Estimated_Savings",
                "Auto_Action"
            ]
        ]

        print("🔍 TOP 10 HIGH-RISK TRANSACTIONS:")
        print(final_output.sort_values("ML_Risk_Score", ascending=False).head(10).to_string(index=False))
        
        # --- NEW: Export the full results to a CSV file ---
        output_file = "actionable_leakage_targets.csv"
        results["actionable_issues"].to_csv(output_file, index=False)
        print(f"\n📁 Successfully exported all detected issues to '{output_file}'")
        
    else:
        print("Please load your dataset into a variable named 'df' before running.")