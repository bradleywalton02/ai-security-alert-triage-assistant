# AI Security Alert Triage Assistant

A defensive cybersecurity portfolio project that uses generative AI to turn raw security alerts into an analyst-facing triage draft. It also uses **pandas** to clean and summarize a batch of alerts and provides a small Streamlit dashboard for demonstration.

## Example: Rule-Based vs. Generative AI Triage

To evaluate the value of generative AI, I created a synthetic EDR alert involving:

- `fodhelper.exe`
- an `ms-settings` registry modification
- possible PowerShell execution
- suspected UAC bypass / privilege escalation

### Rule-Based Result

The local rule-based system detected the `powershell` keyword and classified the alert as:

- Category: Suspicious command execution
- MITRE ATT&CK: T1059.001 — PowerShell
- Priority: P2

This demonstrated a limitation of simple keyword matching because it did not identify the broader privilege-escalation behavior.

### Generative AI Result

The AI-assisted triage identified:

- Category: Suspected privilege escalation / UAC bypass
- MITRE ATT&CK: T1548.002 — Bypass User Account Control
- Priority: P2
- Explicit uncertainties about whether elevation or payload execution actually succeeded

The generative model connected multiple pieces of context while distinguishing confirmed evidence from unverified conclusions.

Human review is still required for every result.

## Improvements I Made

After building the initial version, I made several improvements based on testing:

- Added a more complex synthetic privilege-escalation alert in JSON.
- Added an explicit `uncertainties` field to separate confirmed evidence from inference.
- Replaced prompt-only JSON formatting with JSON Schema Structured Outputs after the model omitted a requested field.
- Added a pandas metric for counting high- and critical-severity alerts.
- Added automated test coverage for the new analytics behavior.

> **Important:** This is an educational portfolio project, not an autonomous incident-response system. AI output can be wrong. Every result is marked for human review.

## What it demonstrates

- Python
- Generative AI / LLM API integration
- JSON input and output
- pandas data analysis
- Security alert triage
- MITRE ATT&CK mapping
- Git-friendly project structure
- Testing with pytest
- Documentation and handoff/runbook practices

## How it works

1. Loads a list of synthetic security alerts from JSON.
2. Uses pandas to normalize the dataset, calculate an explainable baseline risk score, and summarize alert volume.
3. Lets an analyst select an alert.
4. Sends only that alert to a configured LLM in Generative AI mode.
5. Requests structured JSON containing a summary, recommended priority, possible ATT&CK mappings, evidence, investigation steps, and remediation suggestions.
6. Displays the result for analyst review and allows it to be downloaded.

The project also includes a deterministic **local demo mode** so the UI can be tested without an API key. That mode is clearly labeled and is **not** generative AI.

## Project structure

```text
ai-security-alert-triage-assistant/
├── app.py
├── triage.py
├── analytics.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── RUNBOOK.md
├── LEARNING_GUIDE.md
├── PROJECT_WORKLOG.md
├── data/
│   └── sample_alerts.json
└── tests/
    ├── test_analytics.py
    └── test_triage.py
```

## Setup

### 1. Create a virtual environment

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the API

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Add your API key to `.env`.

**Never commit `.env` or an API key to GitHub.**

The `OPENAI_MODEL` value is configurable. If the example model is not available in your API account, replace it with a current text model available to you.

### 4. Run the tests

```bash
pytest
```

### 5. Run the dashboard

```bash
streamlit run app.py
```

## CLI examples

Preview the pipeline without an API call:

```bash
python triage.py --alert ALERT-1001 --demo
```

Run actual generative-AI triage after configuring `.env`:

```bash
python triage.py --alert ALERT-1001
```

Save a result:

```bash
python triage.py --alert ALERT-1001 --output outputs/ALERT-1001.json
```

## Data safety

The included alerts are fictional and use documentation-range IP addresses where applicable. Do not upload real employer, client, or customer security data unless you have explicit authorization and an approved data-handling process.

## Limitations

- LLMs can hallucinate or map an alert to the wrong ATT&CK technique.
- The baseline risk score is a transparent demo heuristic, not a trained risk model.
- A real SOC would enrich alerts with asset criticality, identity context, threat intelligence, historical telemetry, and case-management data.
- The project does not automatically contain, block, delete, isolate, or otherwise act on systems.
- Human review is required for every generated recommendation.

## Suggested next improvements

- Add analyst feedback (correct / incorrect / partially correct) and measure quality.
- Compare source severity to AI-recommended priority.
- Add a second synthetic dataset and benchmark results.
- Add a lightweight SQLite database for triage history.
- Add unit tests with a mocked LLM response.
- Add charts for time-to-triage and alert categories.

## Portfolio note

Before submitting this repository with an internship application, make meaningful changes yourself and document them in `PROJECT_WORKLOG.md`. You should be able to explain every important file, what the AI coding assistant generated, what you changed, how you tested it, and why you made those changes.
