# Learning Guide

This file is here so you can genuinely understand the project rather than only having code that an AI assistant generated.

## 1. What is JSON?

JSON is a text format for structured data.

```json
{
  "alert_id": "ALERT-1001",
  "severity": "high",
  "source": "EDR"
}
```

In Python, that becomes a dictionary. This project reads a JSON **list** of those dictionaries.

Important functions:
- `json.load(...)`: file -> Python objects
- `json.dumps(...)`: Python objects -> JSON text

## 2. What is an API?

An API is a defined way for one program to communicate with another.

In this project:
1. Python builds a prompt.
2. The OpenAI Python library sends a request to a remote model API.
3. The API returns a response.
4. Python reads `response.output_text`.
5. The code converts that returned JSON text back into a Python dictionary.

The API key proves that the request belongs to your API account. That is why it must never be committed to GitHub.

## 3. What is a REST API?

REST is a common style for web APIs built around HTTP requests and resources. You do not need to claim deep REST expertise from this project. The important thing is that you can explain the basic request/response idea and that this application integrates with a remote API using an SDK.

## 4. What is pandas?

pandas is a Python library for working with tabular data. The central object is a `DataFrame`, which is similar to a spreadsheet table.

In `analytics.py`:

```python
df = pd.json_normalize(alerts)
```

turns the JSON alerts into rows and columns.

Then:

```python
df["severity"].value_counts()
```

counts how many alerts have each severity.

And:

```python
df.sort_values("baseline_risk_score", ascending=False)
```

sorts alerts from highest to lowest baseline risk.

## 5. What is the baseline risk score?

It is deliberately simple and explainable. `analytics.py` assigns a base number from the original alert severity and adds a small amount based on the source's confidence score.

It is **not machine learning** and should not be described as machine learning.

The point is to demonstrate cleaning data, creating a derived metric, sorting a dataset, and explaining how the metric works.

## 6. Where is the generative AI?

`triage_with_openai()` in `triage.py`.

The function:
1. validates the alert
2. loads the API configuration
3. builds the prompt
4. sends the alert to the model
5. receives model-generated text
6. parses it as JSON
7. adds metadata about when/how it was generated

The prompt is in `build_prompt()`.

## 7. Why does the prompt say not to invent evidence?

Security analysts need to know what is actually supported by telemetry. LLMs can produce plausible-sounding details that were never present. The prompt tells the model to use only supplied evidence and mark uncertainty.

This is also why every result includes `"human_review_required": true`.

## 8. What is MITRE ATT&CK?

MITRE ATT&CK is a knowledge base that organizes adversary behaviors into tactics and techniques.

This project asks the model for possible mappings, but they must be verified by a human because the alert may not contain enough information for a confident mapping.

## 9. What are tests doing?

The tests use `pytest` and check predictable local behavior such as rejecting malformed alerts, mapping demo severity to priority, calculating risk scores, and producing dataset summary metrics.

The tests intentionally do not call the external LLM. Unit tests should be fast, repeatable, and cheap.

## 10. What should you personally change before publishing?

Do at least these four things yourself:

1. Add one new synthetic alert to `data/sample_alerts.json`.
2. Change the triage prompt and explain why you changed it.
3. Add one new pandas metric to the dashboard.
4. Write at least one new automated test.

Record each change in `PROJECT_WORKLOG.md`.

Then you can truthfully explain that an AI coding assistant helped scaffold the project, but you reviewed it, changed its behavior, tested it, and can explain the design.
