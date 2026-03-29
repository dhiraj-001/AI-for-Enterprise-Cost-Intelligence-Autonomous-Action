import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add project folders to Python's path so it can find the modules
ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT / "Cost-Anomaly-Detection"))
sys.path.append(str(ROOT / "SLA"))
sys.path.append(str(ROOT / "transection_control")) # Add the FinOps folder

# Import the three autonomous agents
from main import SpendIntelligenceSystem
from sla_runner import run_sla_pipeline
from finops_agent import FinOpsAgent 

class UnifiedEnterpriseAgent:
    def __init__(self):
        # Initialize the classes
        self.spend_system = SpendIntelligenceSystem()
        # Limit rows to 2,000 so the Streamlit dashboard loads instantly during your demo
        self.finops_agent = FinOpsAgent(n_rows=2000) 

    def run(self, spend_df: pd.DataFrame) -> dict:
        """Executes all three enterprise agents and aggregates their financial impact."""
        
        # ─────────────────────────────────────────────────────────
        # 1. Run Spend Agent (Procurement & Vendor Cost Leakage)
        # ─────────────────────────────────────────────────────────
        spend_results = self.spend_system.run(spend_df)
        spend_issues = spend_results["actionable_issues"]
        
        # ─────────────────────────────────────────────────────────
        # 2. Run SLA Agent (Operational Risk & Penalty Prevention)
        # ─────────────────────────────────────────────────────────
        sla_results = run_sla_pipeline() # Reads its own operational dataset
        sla_manifest = sla_results["manifest"]
        
        # ─────────────────────────────────────────────────────────
        # 3. Run FinOps Agent (Ledger vs Bank Reconciliation)
        # ─────────────────────────────────────────────────────────
        finops_results = self.finops_agent.run() # Reads internal_ledger and bank_statement
        finops_issues = finops_results["issues"]

        # ─────────────────────────────────────────────────────────
        # Calculate Global Financial Impact
        # ─────────────────────────────────────────────────────────
        # A. Cost Savings (Spend)
        total_cost_savings = float(spend_issues["Estimated_Savings"].sum()) if not spend_issues.empty else 0.0
        
        # B. Penalty Prevention (SLA)
        total_sla_prevention = float(sla_manifest.get("total_prevention_value_estimate", 0.0))
        
        # C. Financial Exposure (FinOps)
        finops_variance = 0.0
        if not finops_issues.empty:
            impact = np.where(
                finops_issues["status"] == "amount_mismatch",
                finops_issues.get("amount_variance", 0).fillna(0),
                finops_issues.get("amount", 0).fillna(0)
            )
            finops_variance = float(impact.sum())

        total_combined_impact = total_cost_savings + total_sla_prevention + finops_variance

        # Return the structured dictionary expected by Streamlit
        return {
            "spend_results": spend_results,
            "sla_results": sla_results,
            "finops_results": finops_results,
            "total_cost_savings": total_cost_savings,
            "total_sla_prevention": total_sla_prevention,
            "finops_variance": finops_variance,
            "total_combined_impact": total_combined_impact,
        }