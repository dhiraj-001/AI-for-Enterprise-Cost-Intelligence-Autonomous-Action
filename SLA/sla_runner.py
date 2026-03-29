import json
import os
from datetime import datetime, timezone
from pathlib import Path
import pickle

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder, StandardScaler

from utils.alerts import send_automation_email_digest, send_slack_digest
from utils.automation import apply_automation_to_dataframe
from utils.feature_engineering import engineer
from utils.genai import heuristic_sla_pack, multi_agent_sla_pack, pack_to_column_value

ROOT = Path(__file__).resolve().parent

def safe_encode(le: LabelEncoder, val) -> int:
    val = str(val)
    if val in le.classes_:
        return int(le.transform([val])[0])
    return 0

def format_insight_from_json(s: str) -> str:
    if not s:
        return ""
    try:
        d = json.loads(s)
        return (
            f"[Reason] {d.get('reason', '')}\n"
            f"[Action] {d.get('action', '')}\n"
            f"[Escalation] {d.get('escalation', '')}"
        )
    except Exception:
        return s

def run_sla_pipeline() -> dict:
    df_train = pd.read_csv(ROOT / "data" / "train.csv")
    df_test = pd.read_csv(ROOT / "data" / "test.csv")

    df_train["breach"] = df_train["breach"].astype(int)
    df_test["breach"] = df_test["breach"].astype(int)

    df_train = engineer(df_train)
    df_test = engineer(df_test)

    features = [
        "priority_score",
        "estimated_time",
        "time_remaining",
        "completion_percentage",
        "time_ratio",
        "urgency_score",
        "risk_score",
        "tight_deadline",
        "very_tight",
        "assigned_to",
    ]

    X_train = df_train[features].copy()
    y_train = df_train["breach"]
    X_test = df_test[features].copy()

    le = LabelEncoder()
    X_train["assigned_to"] = le.fit_transform(X_train["assigned_to"].astype(str))
    X_test["assigned_to"] = X_test["assigned_to"].apply(lambda v: safe_encode(le, v))

    imp = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    X_train = scaler.fit_transform(imp.fit_transform(X_train))
    X_test = scaler.transform(imp.transform(X_test))

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=15,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    df_test["predicted_breach"] = y_pred
    df_test["probability"] = y_prob
    df_test["SLA_Status"] = df_test["predicted_breach"].map({0: "SAFE", 1: "AT_RISK"})

    df_test = apply_automation_to_dataframe(df_test)

    exposure = float(df_test["financial_exposure_ev"].sum())
    prevention = float(df_test["prevention_value_estimate"].sum())
    at_risk = df_test[df_test["predicted_breach"] == 1]

    manifest = {
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "rows_scored": int(len(df_test)),
        "predicted_at_risk": int((df_test["predicted_breach"] == 1).sum()),
        "total_financial_exposure_ev": exposure,
        "total_prevention_value_estimate": prevention,
    }

    return {
        "results_df": df_test,
        "manifest": manifest,
        "at_risk_df": at_risk,
    }