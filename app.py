import re
from collections import Counter
from datetime import datetime
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="AI Incident Analyzer", page_icon="🛠️", layout="wide")

LEVEL_PATTERN = re.compile(r"\b(CRITICAL|FATAL|ERROR|WARN(?:ING)?|INFO|DEBUG)\b", re.I)
TIMESTAMP_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:,\d+|\.\d+)?\b")
PATTERNS = [
    ("Payment/API timeout", re.compile(r"timeout|timed out|deadline exceeded", re.I)),
    ("Database connection issue", re.compile(r"database|db connection|connection pool|too many connections|connection refused", re.I)),
    ("Authentication/authorization", re.compile(r"unauthorized|forbidden|authentication failed|invalid token|permission denied", re.I)),
    ("Resource pressure", re.compile(r"out of memory|oom|memory pressure|cpu high|disk full|no space left", re.I)),
    ("Dependency/network failure", re.compile(r"connection reset|network unreachable|dns|host not found|upstream unavailable", re.I)),
    ("Application exception", re.compile(r"exception|traceback|stack trace|nullpointer|segmentation fault", re.I)),
]

def parse_logs(raw_text):
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    counts = Counter()
    errors = []
    pattern_counts = Counter()
    for line in lines:
        match = LEVEL_PATTERN.search(line)
        level = match.group(1).upper().replace("WARNING", "WARN") if match else "UNKNOWN"
        counts[level] += 1
        if level in {"CRITICAL", "FATAL", "ERROR"}:
            errors.append(line)
        for label, pattern in PATTERNS:
            if pattern.search(line):
                pattern_counts[label] += 1
    return lines, counts, errors, pattern_counts

def severity_for(lines, counts, patterns):
    critical_terms = re.compile(r"\b(CRITICAL|FATAL)\b|data loss|security breach|service unavailable", re.I)
    high_terms = re.compile(r"\bERROR\b|payment|database|timed out|timeout|connection refused", re.I)
    if any(critical_terms.search(line) for line in lines):
        return "Critical", "Critical/fatal markers or potentially severe service-impact language appeared in the supplied logs."
    if counts.get("ERROR", 0) + counts.get("FATAL", 0) >= 5 or patterns.get("Database connection issue", 0) >= 3:
        return "High", "Multiple errors or repeated database connection failures suggest a potentially broad service impact."
    if counts.get("ERROR", 0) > 0 or patterns:
        return "Medium", "Errors or a recognizable failure pattern are present, but the supplied logs alone do not confirm a full outage."
    return "Low", "No explicit error-level entries or recognized failure patterns were detected in the supplied logs."

def deterministic_analysis(raw_text):
    lines, counts, errors, patterns = parse_logs(raw_text)
    severity, reason = severity_for(lines, counts, patterns)
    if not lines:
        return {"lines": lines, "counts": counts, "errors": errors, "patterns": patterns,
                "severity": "Low", "reason": "No non-empty log lines were supplied.",
                "likely_cause": "Insufficient evidence.", "steps": ["Paste or upload application logs and analyze again."],
                "impact": "Cannot estimate impact without log evidence.", "escalation": "Escalate only if users are reporting an active issue or monitoring shows service impact."}
    if patterns:
        top = patterns.most_common(1)[0][0]
        likely = f"The strongest observed pattern is **{top}**. This is a hypothesis based on matching log text, not a confirmed root cause."
    else:
        likely = "No known failure pattern was confidently matched. Review the raw log lines and application context."
    steps = []
    if patterns.get("Payment/API timeout", 0):
        steps += ["Check API latency, timeout thresholds, recent deploys, and upstream dependency health."]
    if patterns.get("Database connection issue", 0):
        steps += ["Check database availability, connection-pool saturation, connection limits, and database-side logs."]
    if patterns.get("Resource pressure", 0):
        steps += ["Check CPU, memory, disk usage, and recent resource changes on the affected host/container."]
    if patterns.get("Authentication/authorization", 0):
        steps += ["Validate credentials, token expiry, permissions, and recent identity/configuration changes."]
    if patterns.get("Dependency/network failure", 0):
        steps += ["Check DNS resolution, network reachability, service discovery, and upstream health."]
    if patterns.get("Application exception", 0):
        steps += ["Inspect the full stack trace and correlate the first exception with the deployment/version."]
    if not steps:
        steps = ["Correlate timestamps with monitoring and recent deployments.", "Inspect surrounding log lines and reproduce safely in a test environment."]
    steps += ["Confirm the suspected cause with metrics and service-specific checks before making changes."]
    escalation = ("Escalate to the service owner/on-call engineer if the issue is ongoing, affects customer transactions, "
                  "crosses the team's response-time target, or requires access/changes outside your permissions.")
    impact = "Potential impact depends on affected endpoints and duration. The logs alone do not establish how many users or transactions were affected."
    return {"lines": lines, "counts": counts, "errors": errors, "patterns": patterns,
            "severity": severity, "reason": reason, "likely_cause": likely,
            "steps": steps, "impact": impact, "escalation": escalation}

def make_report(result):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    errors = result["errors"][:10]
    patterns = result["patterns"]
    return f"""# Incident Analysis Report

- **Generated:** {timestamp}
- **Severity:** {result['severity']}
- **Log lines analyzed:** {len(result['lines'])}

## Severity rationale
{result['reason']}

## Key patterns
""" + ("\n".join(f"- {name}: {count} matching line(s)" for name, count in patterns.most_common()) or "- No known patterns detected.") + """

## Evidence: error lines
""" + ("\n".join(f"- `{line}`" for line in errors) or "- No ERROR/CRITICAL/FATAL lines detected.") + f"""

## Likely cause (hypothesis)
{result['likely_cause']}

## Potential impact
{result['impact']}

## Recommended next steps
""" + "\n".join(f"{i}. {step}" for i, step in enumerate(result["steps"], 1)) + f"""

## Escalation
{result['escalation']}

## Important limitation
This prototype uses transparent rule-based pattern detection. Its output is a triage aid, not proof of root cause. Validate hypotheses against monitoring, deployment history, and service-owner knowledge.
"""

st.title("🛠️ AI-Powered Incident Analyzer")
st.caption("A practical log-triage prototype for Technology Operations teams")
with st.sidebar:
    st.header("How to use")
    st.write("1. Paste logs or upload a `.log` / `.txt` file.")
    st.write("2. Select **Analyze incident**.")
    st.write("3. Review evidence, severity, and next steps.")
    st.info("Demo mode uses rule-based analysis and does not require an API key. Treat causes as hypotheses.")

uploaded = st.file_uploader("Upload a log file", type=["log", "txt"])
pasted = st.text_area("Or paste application logs here", height=220, placeholder="2026-10-27 12:00:01 ERROR Payment API timeout...")
if uploaded is not None:
    try:
        uploaded_text = uploaded.getvalue().decode("utf-8", errors="replace")
    except Exception:
        uploaded_text = ""
else:
    uploaded_text = ""
raw = pasted.strip() if pasted.strip() else uploaded_text.strip()

col1, col2 = st.columns([1, 4])
with col1:
    analyze = st.button("Analyze incident", type="primary", use_container_width=True)
with col2:
    st.caption(f"{len(raw.splitlines()) if raw else 0} log lines ready for analysis")

if analyze:
    if not raw:
        st.warning("Please paste logs or upload a file first.")
    else:
        result = deterministic_analysis(raw)
        st.session_state["last_result"] = result
        st.session_state["last_report"] = make_report(result)

if "last_result" in st.session_state:
    result = st.session_state["last_result"]
    st.divider()
    st.subheader("Incident overview")
    a, b, c, d = st.columns(4)
    a.metric("Severity", result["severity"])
    b.metric("Lines analyzed", len(result["lines"]))
    c.metric("Error lines", len(result["errors"]))
    d.metric("Patterns found", len(result["patterns"]))
    st.write("**Why this severity?**", result["reason"])
    left, right = st.columns(2)
    with left:
        st.subheader("Key patterns")
        if result["patterns"]:
            for name, count in result["patterns"].most_common():
                st.write(f"- **{name}:** {count} matching line(s)")
        else:
            st.write("No known patterns detected.")
        st.subheader("Likely cause (hypothesis)")
        st.markdown(result["likely_cause"])
        st.caption("Evidence supports a hypothesis; it does not confirm root cause.")
    with right:
        st.subheader("Evidence: error lines")
        if result["errors"]:
            for line in result["errors"][:20]:
                st.code(line, language="text")
            if len(result["errors"]) > 20:
                st.caption(f"Showing 20 of {len(result['errors'])} error lines.")
        else:
            st.write("No ERROR, CRITICAL, or FATAL lines detected.")
        st.subheader("Potential impact")
        st.write(result["impact"])
    st.subheader("Recommended troubleshooting steps")
    for i, step in enumerate(result["steps"], 1):
        st.write(f"{i}. {step}")
    st.subheader("Escalation guidance")
    st.write(result["escalation"])
    st.download_button("Download incident report (.md)", st.session_state["last_report"],
                       file_name="incident_report.md", mime="text/markdown")
    with st.expander("Show all non-empty log lines"):
        st.code("\n".join(result["lines"]), language="text")

st.divider()
st.caption("Prototype disclaimer: sample/simulated data only. Confirm recommendations with system metrics and service owners.")
