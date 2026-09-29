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

    with st.expander("View Raw Alert", expanded=True):
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

        if result.get("human_review_required"):
            st.info("Human review required before taking action.")

        priority_col, confidence_col = st.columns(2)

        priority_col.metric(
            "Recommended priority",
            result.get("recommended_priority", "Unknown")
        )

        confidence = result.get("confidence")
        confidence_text = (
            f"{confidence:.0%}"
            if isinstance(confidence, (int, float))
            else "Unknown"
        )

        confidence_col.metric(
            "Confidence",
            confidence_text
        )

        st.markdown("### Summary")
        st.write(result.get("summary", "No summary available."))

        st.markdown("**Category**")
        st.write(result.get("likely_category", "Unknown"))

        mitre = result.get("mitre_attack", [])

        if mitre:
            st.markdown("### MITRE ATT&CK")

            for technique in mitre:
                st.markdown(
                    f"- **{technique.get('technique_id', 'Unknown')}** — "
                    f"{technique.get('name', 'Unknown')}"
                )

        uncertainties = result.get("uncertainties", [])

        if uncertainties:
            with st.expander("Uncertainties"):
                for item in uncertainties:
                    st.markdown(f"- {item}")

        evidence = result.get("evidence", [])

        if evidence:
            with st.expander("Evidence"):
                for item in evidence:
                    st.markdown(f"- {item}")

        investigation_steps = result.get("investigation_steps", [])

        if investigation_steps:
            with st.expander("Investigation Steps"):
                for number, step in enumerate(investigation_steps, start=1):
                    st.markdown(f"{number}. {step}")

        remediation_actions = result.get("remediation_actions", [])

        if remediation_actions:
            with st.expander("Remediation Actions"):
                for number, action in enumerate(remediation_actions, start=1):
                    st.markdown(f"{number}. {action}")

        rationale = result.get("rationale")

        if rationale:
            with st.expander("Priority Rationale"):
                st.write(rationale)

        with st.expander("View Full JSON"):
            st.json(result)

        st.download_button(
            "Download triage result",
            data=json.dumps(result, indent=2),
            file_name=f"{selected_id}_triage.json",
            mime="application/json",
        )
