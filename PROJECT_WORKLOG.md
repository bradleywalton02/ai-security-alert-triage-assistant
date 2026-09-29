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

## Change 4 — Automated test

**Test I added:**  

**What failure it protects against:**  

## AI coding assistant review example

Use your real experience, not this wording verbatim.

- What the assistant produced:
- What I disagreed with or changed:
- How I verified the change:
- Why my final version is better:

## Final demo notes

**Model used:**  
**Number of sample alerts:**  
**What worked well:**  
**What still needs improvement:**  
**What I would build next in a real SOC environment:**  
