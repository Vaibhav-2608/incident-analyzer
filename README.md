# incident-analyzer
**Practical AI Assignment 1 — Technology Operations Intern**

## Overview
A local web prototype for analyzing sample application logs. It summarizes error-level entries, detects repeated failure patterns, assigns a transparent preliminary severity, suggests troubleshooting steps, and creates a Markdown incident report.

## Features
- Upload `.log` or `.txt` files, or paste logs into the interface.
- Counts log levels and extracts `ERROR`, `CRITICAL`, and `FATAL` lines.
- Detects common patterns: API timeouts, database connection issues, authentication failures, resource pressure, network/dependency failures, and application exceptions.
- Assigns Critical / High / Medium / Low severity with an explanation.
- Provides practical next steps and escalation guidance.
- Downloads a shareable incident report.
- Runs locally without an external API key.

## Technology and approach
- Python: application logic and pattern matching.
- Streamlit: browser-based interface.
- Regular expressions and keyword rules: transparent baseline log analysis.

**AI integration note:** This initial implementation uses rule-based analysis rather than a generative AI model. This is intentional for a reliable, reproducible demo. An LLM API can be added as an optional second stage to interpret the extracted evidence, while keeping rule-based evidence and severity visible. Do not claim an external AI model was used unless you implement and test that integration.

## Setup
Requires Python 3.10 or newer.

```bash
# 1. Create and activate a virtual environment
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the app
streamlit run app.py
```

Open the local URL printed in the terminal (usually `http://localhost:8501`).

## Demo
1. Open `sample_logs/payment_timeout.log`.
2. Copy and paste the content, or upload the file.
3. Click **Analyze incident**.
4. Review severity, matching evidence, hypotheses, next steps, and escalation guidance.
5. Download the incident report.

## Example expected interpretation
The sample log contains repeated payment API timeouts and database connection failures. The prototype should identify these patterns, assign a preliminary severity, and recommend checking API latency, database availability, and connection-pool saturation. These are hypotheses to verify, not confirmed root causes.

## Testing checklist
- [ ] Empty input shows a helpful warning.
- [ ] Error logs appear in the evidence section.
- [ ] Repeated timeout/database messages are counted as patterns.
- [ ] Severity includes a reason.
- [ ] Report downloads as Markdown.
- [ ] Test with logs that contain no errors and with malformed/unstructured lines.

## Assumptions and limitations
- Input is sample or simulated text logs; no production system is accessed.
- Log formats vary, so unstructured lines may be classified as `UNKNOWN`.
- Keyword matches can produce false positives or miss unfamiliar failure modes.
- Severity is a preliminary heuristic; real severity also depends on customer impact, scope, duration, and service objectives.
- The prototype does not connect to monitoring, ticketing, or deployment systems.
- Root cause must be verified by a human using metrics, traces, recent changes, and service-owner knowledge.
- Do not paste secrets, credentials, personal data, or production logs into the demo.

## Suggested presentation outline (10 minutes)
1. Problem and objective (1 min)
2. Architecture and workflow (1 min)
3. Live demo with sample payment logs (3 min)
4. Explain pattern detection and severity rationale (2 min)
5. Testing, limitations, and safe use of AI (2 min)
6. Summary and next improvements (1 min)

## Q&A topics to prepare
- Why use rules instead of only an LLM? Rules make evidence and baseline severity reproducible; an LLM can be added for summarization but should not invent evidence.
- How do you avoid presenting guesses as facts? Show matched log lines and label root-cause statements as hypotheses.
- How would you improve it? Add structured parsers, optional LLM summarization, unit tests, JSON output, monitoring integrations, and role-based access.
- Is it production-ready? No. It is a local prototype for simulated data, as requested by the assignment.

## Individual contribution
Replace this section with an accurate description of what you personally implemented, tested, and learned. If you used AI assistance, disclose it honestly and be ready to explain every major function.
