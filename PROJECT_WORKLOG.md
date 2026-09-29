# Project Worklog

Use this to document your own work before you publish the repository.

A strong interview answer is not "AI wrote the project for me." A stronger and accurate answer is: an AI coding assistant helped scaffold a first version, then you reviewed the code, changed specific behavior, tested it, and made engineering decisions yourself.

## Starting point

**Date:**  
**What the AI assistant scaffolded:**
- Python alert loader / validator
- OpenAI API integration
- Streamlit dashboard
- pandas batch analysis
- sample synthetic alerts
- initial unit tests
- documentation

## Change 1 — New Synthetic Alert

What I added:
Added ALERT-1006, a synthetic EDR alert representing a possible UAC bypass and privilege-escalation attempt using fodhelper.exe and PowerShell.

Why:
I wanted a more complex alert that contained multiple security behaviors so I could compare simple rule-based triage with generative-AI triage.

What I learned:
The local rule-based system recognized the PowerShell keyword and mapped it to T1059.001, but it did not understand the broader UAC-bypass context. This showed a limitation of simple keyword matching.

When I ran ALERT-1006 through the local rule-based system, it recognized the PowerShell keyword and mapped the alert to T1059.001, but it missed the broader privilege-escalation behavior.

When I ran the same alert through the generative-AI mode, the model identified the likely UAC bypass behavior and mapped it to T1548.002 (Bypass User Account Control). It also distinguished between confirmed evidence and inference by noting that PowerShell execution was suggested but not confirmed.

This showed me how generative AI can analyze relationships between multiple pieces of alert context that simple keyword matching may miss, while still requiring human review.

## Change 2 — Structured Outputs

Original behavior:
The application asked the model to return JSON with an uncertainties field, but the model omitted that field in one response.

What I changed:
I added a JSON Schema and enabled Structured Outputs through the API. The schema requires every expected field, restricts recommended_priority to P1-P4, constrains confidence to 0-1, and prevents unexpected fields.

Why:
Prompt instructions alone did not guarantee a consistent response structure. A security tool needs predictable output so the application and analyst can reliably process every result.

How I tested it:
I ran ALERT-1006 again. The response included the required uncertainties array and followed the defined schema.

## Change 3 — pandas Metric

Metric I added:
High-Priority Alerts, which counts alerts with a severity of high or critical.

How the pandas code works:
I selected the severity column from the DataFrame and used .isin(["high", "critical"]) to create a Boolean series identifying which alerts matched those severities. I then used .sum() to count the matching rows.

Why the metric is useful:
It gives an analyst a quick view of how many alerts in the current dataset may require more immediate attention instead of relying only on the total alert count.

How I tested it:
I updated the analytics unit test to verify that a dataset containing one critical alert and one low-severity alert returns one high-priority alert. I also confirmed that the dashboard correctly showed three high-priority alerts in the six-alert sample dataset.

## Change 4 — Analyst Interface

**What I changed:**  
Replaced the raw JSON-only analyst output with a more readable Streamlit interface showing recommended priority, confidence, summary, category, MITRE ATT&CK mappings, and collapsible sections for uncertainties, evidence, investigation steps, remediation actions, rationale, and full JSON.

**Why:**  
The original interface exposed the model response as one large JSON block, which was difficult to scan. I wanted the output to be easier for an analyst to review quickly while still preserving the complete structured response for transparency and debugging.

**How I tested it:**  
I reran ALERT-1006 and confirmed that the same structured triage data was still available while the most important information was easier to read in the dashboard.

**What I learned:**  
Good security tooling is not only about generating useful analysis; the information also needs to be presented in a way that supports quick human review.

## AI coding assistant review example

Use your real experience, not this wording verbatim.

- What the assistant produced:
The initial project scaffold included the Python alert-triage logic, Streamlit interface, pandas-based analytics, synthetic sample alerts, OpenAI API integration, unit tests, and project documentation.
- What I disagreed with or changed:
  I added a more complex synthetic privilege-escalation alert to test the system against behavior involving fodhelper.exe, registry modification, and possible PowerShell execution. I found that the original rule-based triage focused on the PowerShell keyword and missed the broader UAC-bypass behavior. I also found that prompt instructions alone did not reliably enforce the expected output structure when the model omitted the uncertainties field. I changed the implementation to use JSON Schema Structured Outputs and added a pandas metric for high-priority alerts.
- How I verified the change:
  I ran the same synthetic alert through both the local rule-based mode and the generative-AI mode and compared the results. I verified that Structured Outputs consistently returned the required uncertainties field. I also added an automated test for the new pandas metric and confirmed that the full test suite passed.
- Why my final version is better:
  The final version produces more predictable structured output, explicitly separates confirmed evidence from uncertainty, better demonstrates the value of contextual AI analysis compared with simple keyword rules, and provides a clearer dashboard view of high-priority alerts.

## Final demo notes

**Model used:** GPT-5.6 Luna
**Number of sample alerts:**  6
**What worked well:** 
The generative-AI triage was able to connect multiple pieces of alert context and distinguish confirmed evidence from inference. Structured Outputs made the response format consistent, and the pandas dashboard made it easy to summarize and prioritize the sample dataset.
**What still needs improvement:** 
The system currently relies on synthetic alerts and does not use real SOC telemetry or enrichment sources. MITRE ATT&CK mappings and remediation recommendations still require analyst validation. The baseline risk score is a simple heuristic rather than a trained or production-grade scoring model.
**What I would build next in a real SOC environment:** 
I would add enrichment from asset inventory, identity context, threat intelligence, and historical alert data; store triage history in a database; add analyst feedback to measure recommendation quality; and compare AI-generated triage against analyst decisions over time.
