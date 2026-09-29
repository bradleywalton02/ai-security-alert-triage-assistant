"""Pandas-based batch analysis for security alert datasets."""

from __future__ import annotations

from typing import Any

import pandas as pd

SEVERITY_WEIGHT = {
    "low": 20,
    "medium": 40,
    "high": 65,
    "critical": 85,
}


def alerts_to_dataframe(alerts: list[dict[str, Any]]) -> pd.DataFrame:
    """Normalize a list of JSON alert objects into a pandas DataFrame."""
    if not alerts:
        return pd.DataFrame()

    df = pd.json_normalize(alerts)
    if "severity" in df.columns:
        df["severity"] = df["severity"].astype(str).str.lower()
    if "confidence" in df.columns:
        df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce")
    return df


def calculate_risk_score(row: pd.Series) -> float:
    """Calculate a simple, explainable 0-100 baseline risk score."""
    severity = str(row.get("severity", "low")).lower()
    base = SEVERITY_WEIGHT.get(severity, 20)

    confidence = row.get("confidence", 0.5)
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.5

    confidence = max(0.0, min(confidence, 1.0))
    score = base + confidence * 15
    return round(min(score, 100.0), 1)


def add_risk_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the DataFrame with a baseline_risk_score column."""
    if df.empty:
        return df.copy()

    scored = df.copy()
    scored["baseline_risk_score"] = scored.apply(calculate_risk_score, axis=1)
    return scored


def dataset_summary(alerts: list[dict[str, Any]]) -> dict[str, Any]:
    """Create JSON-serializable summary metrics from an alert list."""
    df = add_risk_scores(alerts_to_dataframe(alerts))
    if df.empty:
        return {
            "total_alerts": 0,
            "severity_counts": {},
            "source_counts": {},
            "average_confidence": None,
            "high_priority_alerts": 0,
            "top_risk_alerts": [],
        }

    severity_counts = (
        df["severity"].value_counts().to_dict() if "severity" in df.columns else {}
    )
    high_priority_alerts = int(
        df["severity"].isin(["high", "critical"]).sum()
    )
    source_counts = (
        df["source"].value_counts().to_dict() if "source" in df.columns else {}
    )

    average_confidence = None
    if "confidence" in df.columns and df["confidence"].notna().any():
        average_confidence = round(float(df["confidence"].mean()), 3)

    top_cols = [c for c in ["alert_id", "title", "severity", "baseline_risk_score"] if c in df.columns]
    top_risk = (
        df.sort_values("baseline_risk_score", ascending=False)[top_cols]
        .head(5)
        .to_dict(orient="records")
    )

    return {
        "total_alerts": int(len(df)),
        "severity_counts": {str(k): int(v) for k, v in severity_counts.items()},
        "source_counts": {str(k): int(v) for k, v in source_counts.items()},
        "average_confidence": average_confidence,
        "high_priority_alerts": high_priority_alerts,
        "top_risk_alerts": top_risk,
    }
