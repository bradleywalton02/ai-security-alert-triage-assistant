"""Streamlit UI for the AI Security Alert Triage Assistant."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from analytics import add_risk_scores, alerts_to_dataframe, dataset_summary
from triage import demo_triage, triage_with_openai, validate_alert

load_dotenv()

st.set_page_config(page_title="AI Security Alert Triage Assistant", layout="wide")

st.title("AI Security Alert Triage Assistant")
st.caption(
    "Defensive portfolio project using synthetic alerts. "
    "AI output is advisory and requires analyst review."
)

with st.sidebar:
    st.header("Triage mode")
    mode = st.radio(
        "Choose a mode",
        ["Generative AI", "Local demo (non-AI)"],
        help="The local demo uses rules only. Use Generative AI for the actual portfolio demonstration.",
    )
    st.info(
        "Use only synthetic or otherwise approved non-sensitive data. "
        "Generative AI mode sends the selected alert to the configured API."
    )

sample_path = Path("data/sample_alerts.json")
sample_alerts = json.loads(sample_path.read_text(encoding="utf-8"))

uploaded = st.file_uploader("Upload an alert dataset (JSON list)", type=["json"])
if uploaded is not None:
    try:
        alerts = json.load(uploaded)
        if not isinstance(alerts, list):
            raise ValueError("The uploaded JSON must contain a list of alert objects.")
        for item in alerts:
            validate_alert(item)
    except Exception as exc:
        st.error(f"Could not load dataset: {exc}")
        st.stop()
else:
    alerts = sample_alerts

summary = dataset_summary(alerts)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Alerts", summary["total_alerts"])
m2.metric("Average source confidence", summary["average_confidence"] or "N/A")
m3.metric("High-priority alerts", summary["high_priority_alerts"])
m4.metric("Critical alerts", summary["severity_counts"].get("critical", 0))

st.subheader("Batch overview")
df = add_risk_scores(alerts_to_dataframe(alerts))
display_columns = [
    c
    for c in ["alert_id", "title", "source", "severity", "confidence", "baseline_risk_score"]
    if c in df.columns
]
st.dataframe(
    df[display_columns].sort_values("baseline_risk_score", ascending=False),
    use_container_width=True,
    hide_index=True,
)

alert_ids = [a["alert_id"] for a in alerts]
selected_id = st.selectbox("Select an alert to triage", alert_ids)
selected = next(a for a in alerts if a["alert_id"] == selected_id)

left, right = st.columns(2)

with left:
    st.subheader("Raw alert")
    st.json(selected)

with right:
    st.subheader("Analyst triage")
    if st.button("Run triage", type="primary"):
        try:
            with st.spinner("Analyzing alert..."):
                if mode == "Generative AI":
                    result = triage_with_openai(selected)
                else:
                    result = demo_triage(selected)
            st.session_state["last_result"] = result
        except Exception as exc:
            st.error(str(exc))

    result = st.session_state.get("last_result")
    if result and result.get("alert_id") == selected_id:
        if result.get("mode") == "local_demo_non_ai":
            st.warning("This result is from deterministic demo mode, not generative AI.")
        st.json(result)

        st.download_button(
            "Download triage result",
            data=json.dumps(result, indent=2),
            file_name=f"{selected_id}_triage.json",
            mime="application/json",
        )
