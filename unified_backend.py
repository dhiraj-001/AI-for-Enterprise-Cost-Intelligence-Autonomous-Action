import sys
from pathlib import Path
import pandas as pd

# Add project folders to path
ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT / "Cost-Anomaly-Detection"))
sys.path.append(str(ROOT / "SLA"))

from main import SpendIntelligenceSystem
from sla_runner import run_sla_pipeline   # you'll create this

class UnifiedEnterpriseAgent:
    def __init__(self):
        self.spend_system = SpendIntelligenceSystem()

    def run(self, spend_df: pd.DataFrame):
        spend_results = self.spend_system.run(spend_df)
        sla_results = run_sla_pipeline()

        spend_issues = spend_results["actionable_issues"]
        sla_df = sla_results["results_df"]
        sla_manifest = sla_results["manifest"]

        total_cost_savings = (
            spend_issues["Estimated_Savings"].sum()
            if not spend_issues.empty else 0
        )

        total_sla_prevention = sla_manifest.get("total_prevention_value_estimate", 0)

        total_combined_impact = total_cost_savings + total_sla_prevention

        return {
            "spend_results": spend_results,
            "sla_results": sla_results,
            "total_cost_savings": total_cost_savings,
            "total_sla_prevention": total_sla_prevention,
            "total_combined_impact": total_combined_impact,
        }