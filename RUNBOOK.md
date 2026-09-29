# Runbook

## Purpose

This runbook explains how another analyst or developer can install, run, test, and troubleshoot the AI Security Alert Triage Assistant.

## Prerequisites

- Python 3.11+ recommended
- Internet access for Generative AI mode
- An API key for the configured model provider
- Synthetic or approved non-sensitive alert data

## Start the application

```bash
source .venv/bin/activate
streamlit run app.py
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
streamlit run app.py
```

## Normal workflow

1. Open the Streamlit URL printed in the terminal.
2. Leave the built-in sample dataset selected or upload a JSON list matching the expected schema.
3. Review the batch overview.
4. Select an alert.
5. Choose **Generative AI** mode.
6. Click **Run triage**.
7. Compare the generated summary and priority to the raw alert.
8. Verify suggested ATT&CK mappings before using them.
9. Download the result if you want to preserve it for a demo.

## Expected alert fields

Required: `alert_id`, `timestamp`, `source`, `severity`, `title`, `description`.

Optional examples: `host`, `user`, `source_ip`, `destination_ip`, `confidence`, `tags`.

Severity must be one of: low, medium, high, critical.

## Troubleshooting

### `OPENAI_API_KEY is not set`

Create `.env` from `.env.example` and add the key.

### Model not found / access error

Change `OPENAI_MODEL` in `.env` to a current text model available in your API account.

### Invalid model JSON

The code strips ordinary Markdown JSON fences, but an LLM can still produce malformed output. Re-run the request or improve `build_prompt()` / add structured outputs.

### Uploaded JSON fails validation

Check that the top-level JSON value is a list and each alert includes every required field.

### Import errors

Activate the virtual environment and run:

```bash
pip install -r requirements.txt
```

## Testing

```bash
pytest
```

The automated tests do not call an external model and therefore do not consume API credits.

## Security / privacy notes

- Never commit `.env`.
- Never place a production secret in sample code.
- Use synthetic data for portfolio demonstrations.
- Treat AI-generated triage as advisory.
- Do not automatically execute remediation actions from model output.
