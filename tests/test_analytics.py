from analytics import add_risk_scores, alerts_to_dataframe, dataset_summary

ALERTS = [
    {
        "alert_id": "A1",
        "timestamp": "2026-01-01T00:00:00Z",
        "source": "EDR",
        "severity": "critical",
        "title": "Critical test",
        "description": "Synthetic",
        "confidence": 1.0,
    },
    {
        "alert_id": "A2",
        "timestamp": "2026-01-01T00:01:00Z",
        "source": "Identity",
        "severity": "low",
        "title": "Low test",
        "description": "Synthetic",
        "confidence": 0.5,
    },
]


def test_dataframe_and_risk_score():
    df = add_risk_scores(alerts_to_dataframe(ALERTS))
    assert "baseline_risk_score" in df.columns
    assert df.loc[df["alert_id"] == "A1", "baseline_risk_score"].iloc[0] > \
           df.loc[df["alert_id"] == "A2", "baseline_risk_score"].iloc[0]


def test_dataset_summary():
    summary = dataset_summary(ALERTS)
    assert summary["total_alerts"] == 2
    assert summary["severity_counts"]["critical"] == 1
    assert summary["high_priority_alerts"] == 1
    assert summary["top_risk_alerts"][0]["alert_id"] == "A1"
