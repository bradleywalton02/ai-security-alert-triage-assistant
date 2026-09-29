"""
Core triage logic for the AI Security Alert Triage Assistant.

This project is defensive: it analyzes synthetic security alerts and produces
analyst-facing summaries, prioritization, investigation steps, and remediation
suggestions. It does not execute attacker techniques.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


REQUIRED_FIELDS = {"alert_id", "timestamp", "source", "severity", "title", "description"}
ALLOWED_SEVERITIES = {"low", "medium", "high", "critical"}
TRIAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "alert_id": {
            "type": "string"
        },
        "summary": {
            "type": "string"
        },
        "recommended_priority": {
            "type": "string",
            "enum": ["P1", "P2", "P3", "P4"]
        },
        "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
        },
        "likely_category": {
            "type": "string"
        },
        "mitre_attack": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "technique_id": {
                        "type": "string"
                    },
                    "name": {
                        "type": "string"
                    }
                },
                "required": ["technique_id", "name"],
                "additionalProperties": False
            }
        },
        "evidence": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "uncertainties": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "investigation_steps": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "remediation_actions": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "human_review_required": {
            "type": "boolean"
        },
        "rationale": {
            "type": "string"
        }
    },
    "required": [
        "alert_id",
        "summary",
        "recommended_priority",
        "confidence",
        "likely_category",
        "mitre_attack",
        "evidence",
        "uncertainties",
        "investigation_steps",
        "remediation_actions",
        "human_review_required",
        "rationale"
    ],
    "additionalProperties": False
}


def load_alerts(path: str | Path) -> list[dict[str, Any]]:
    """Load a JSON list of alerts from disk and validate each alert."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Input JSON must be a list of alert objects.")

    for alert in data:
        validate_alert(alert)

    return data


def validate_alert(alert: dict[str, Any]) -> None:
    """Validate the minimum schema required by this project."""
    missing = REQUIRED_FIELDS - set(alert)
    if missing:
        raise ValueError(f"Alert is missing required fields: {sorted(missing)}")

    severity = str(alert["severity"]).lower()
    if severity not in ALLOWED_SEVERITIES:
        raise ValueError(
            f"Invalid severity '{alert['severity']}'. "
            f"Expected one of {sorted(ALLOWED_SEVERITIES)}."
        )


def _strip_code_fences(text: str) -> str:
    """Remove Markdown code fences if a model wraps JSON in them."""
    text = text.strip()
    match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else text


def build_prompt(alert: dict[str, Any]) -> str:
    """Build the defensive analyst-assistance prompt."""
    return f"""
You are assisting a cybersecurity analyst with defensive alert triage.

Analyze ONLY the evidence in the alert below. Do not invent logs, identities, malware families, attribution, or facts that are not present. When evidence is insufficient, say "unknown". Your output is advisory and must require human review.

Analyze the alert and populate every field required by the provided output schema.

For uncertainties, explicitly identify important conclusions that cannot be confirmed from the supplied evidence. Distinguish observed facts from reasonable inferences.

For MITRE ATT&CK mappings, include only techniques reasonably supported by the alert. Use an empty array if the evidence is insufficient for a useful mapping.

human_review_required must always be true.

Priority guidance:
P1 = immediate response / likely severe active compromise
P2 = urgent investigation
P3 = normal analyst queue
P4 = low-priority / informational

Synthetic alert:
{json.dumps(alert, indent=2)}
""".strip()


def triage_with_openai(
    alert: dict[str, Any],
    *,
    model: str | None = None,
    client: Any | None = None,
) -> dict[str, Any]:
    """Send one alert to the OpenAI Responses API and parse the JSON result."""
    validate_alert(alert)
    load_dotenv()

    model = model or os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
    api_key = os.getenv("OPENAI_API_KEY")
    if client is None:
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key, "
                "or run with --demo for the local non-AI demonstration mode."
            )
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": (
                    "You are a defensive cybersecurity alert-triage assistant. "
                    "Be evidence-based, cautious, and concise."
                ),
            },
            {"role": "user", "content": build_prompt(alert)},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "security_alert_triage",
                "schema": TRIAGE_SCHEMA,
                "strict": True
            }
        },
    )

    raw = _strip_code_fences(response.output_text)
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "The model did not return valid JSON. Raw model output:\n" + response.output_text
        ) from exc

    result["generated_at"] = datetime.now(timezone.utc).isoformat()
    result["model"] = model
    result["mode"] = "generative_ai"
    return result


def demo_triage(alert: dict[str, Any]) -> dict[str, Any]:
    """
    Local deterministic demonstration mode.

    This is NOT generative AI. It exists so the UI and data pipeline can be
    tested without an API key.
    """
    validate_alert(alert)

    severity = str(alert["severity"]).lower()
    priority_map = {
        "critical": "P1",
        "high": "P2",
        "medium": "P3",
        "low": "P4",
    }

    tags = [str(x).lower() for x in alert.get("tags", [])]
    title_desc = f"{alert.get('title', '')} {alert.get('description', '')}".lower()

    mitre = []
    category = "Security alert requiring review"

    if "powershell" in title_desc or "powershell" in tags:
        category = "Suspicious command execution"
        mitre.append({"technique_id": "T1059.001", "name": "PowerShell"})
    elif "login" in title_desc or "authentication" in tags:
        category = "Suspicious authentication activity"
        mitre.append({"technique_id": "T1110", "name": "Brute Force"})
    elif "ransomware" in title_desc or "mass_file_change" in tags:
        category = "Potential ransomware behavior"
        mitre.append({"technique_id": "T1486", "name": "Data Encrypted for Impact"})

    confidence = float(alert.get("confidence", 0.5))
    return {
        "alert_id": alert["alert_id"],
        "summary": (
            f"{alert['title']}. This local demo uses deterministic rules rather than a "
            "generative model and should only be used to preview the application."
        ),
        "recommended_priority": priority_map[severity],
        "confidence": round(confidence, 2),
        "likely_category": category,
        "mitre_attack": mitre,
        "evidence": [
            f"Source severity: {alert['severity']}",
            f"Alert source: {alert['source']}",
            f"Description: {alert['description']}",
        ],
        "investigation_steps": [
            "Validate the alert against the original telemetry.",
            "Review nearby events for the affected host and user.",
            "Escalate if corroborating evidence indicates active compromise.",
        ],
        "remediation_actions": [
            "Follow the organization's incident-response process if compromise is confirmed."
        ],
        "human_review_required": True,
        "rationale": "Demo priority is mapped directly from source severity.",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": None,
        "mode": "local_demo_non_ai",
    }


def find_alert(alerts: list[dict[str, Any]], alert_id: str) -> dict[str, Any]:
    for alert in alerts:
        if alert["alert_id"] == alert_id:
            return alert
    raise KeyError(f"Alert ID '{alert_id}' was not found.")


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Security Alert Triage Assistant")
    parser.add_argument("--input", default="data/sample_alerts.json", help="Path to JSON alert list")
    parser.add_argument("--alert", required=True, help="Alert ID to triage")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Use deterministic local demo mode (NOT generative AI)",
    )
    parser.add_argument("--output", help="Optional path to write triage JSON")
    args = parser.parse_args()

    alerts = load_alerts(args.input)
    alert = find_alert(alerts, args.alert)
    result = demo_triage(alert) if args.demo else triage_with_openai(alert)

    rendered = json.dumps(result, indent=2)
    print(rendered)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
