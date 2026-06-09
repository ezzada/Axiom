"""
AXIOM — Streamlit UI
Run with: streamlit run axiom_ui.py
"""

import os
import sys
import time
import queue
import threading
from datetime import datetime
import streamlit as st

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AXIOM — Pentest Suite",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500&family=Orbitron:wght@700;900&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace !important;
    background-color: #080a0c !important;
    color: #c9d1d9 !important;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid rgba(230,57,70,0.2) !important;
}
[data-testid="stSidebar"] * { color: #c9d1d9 !important; }

/* Inputs */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: #0d1117 !important;
    border: 1px solid rgba(230,57,70,0.25) !important;
    color: #c9d1d9 !important;
    font-family: 'JetBrains Mono', monospace !important;
    border-radius: 3px !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #e63946 !important;
    box-shadow: 0 0 0 2px rgba(230,57,70,0.2) !important;
}

/* Buttons */
[data-testid="stButton"] button {
    background: transparent !important;
    border: 1px solid #e63946 !important;
    color: #e63946 !important;
    font-family: 'Orbitron', monospace !important;
    font-weight: 700 !important;
    letter-spacing: 0.2em !important;
    transition: all 0.2s !important;
    border-radius: 3px !important;
}
[data-testid="stButton"] button:hover {
    background: #e63946 !important;
    color: white !important;
}

/* Download button */
[data-testid="stDownloadButton"] button {
    background: #e63946 !important;
    border: none !important;
    color: white !important;
    font-family: 'JetBrains Mono', monospace !important;
    border-radius: 3px !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: #c1121f !important;
    color: white !important;
}

/* Checkbox */
[data-testid="stCheckbox"] {
    background: rgba(230,57,70,0.05) !important;
    border: 1px solid rgba(230,57,70,0.2) !important;
    padding: 0.5rem !important;
    border-radius: 3px !important;
}

/* Progress bar */
[data-testid="stProgress"] > div > div {
    background: #e63946 !important;
}

/* Selectbox */
[data-testid="stSelectbox"] select,
[data-testid="stSelectbox"] > div > div {
    background: #0d1117 !important;
    border-color: rgba(230,57,70,0.25) !important;
    color: #c9d1d9 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* Expander */
[data-testid="stExpander"] {
    border: 1px solid rgba(230,57,70,0.2) !important;
    background: #0d1117 !important;
}

/* Divider */
hr { border-color: rgba(230,57,70,0.2) !important; }

/* Metric */
[data-testid="stMetric"] {
    background: #0d1117;
    border: 1px solid rgba(230,57,70,0.2);
    padding: 0.8rem;
    border-radius: 3px;
}
[data-testid="stMetricLabel"] { color: #6e7681 !important; font-size: 0.7rem !important; }
[data-testid="stMetricValue"] { color: #e63946 !important; }

/* Code block (used for terminal) */
.stCodeBlock { background: #0d1117 !important; border: 1px solid rgba(230,57,70,0.15) !important; }

.axiom-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 2.2rem;
    font-weight: 900;
    color: #e63946;
    letter-spacing: 0.3em;
    text-shadow: 0 0 30px rgba(230,57,70,0.4);
    margin-bottom: 0;
}
.axiom-sub {
    color: #6e7681;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 0;
}
.section-label {
    font-size: 0.62rem;
    color: #e63946;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
    font-family: 'Orbitron', sans-serif;
}
.agent-row {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.4rem 0.6rem;
    border-radius: 3px;
    margin-bottom: 0.3rem;
    font-size: 0.78rem;
    border: 1px solid rgba(230,57,70,0.1);
    background: rgba(13,17,23,0.8);
}
.agent-idle { color: #6e7681; }
.agent-running { color: #e63946; background: rgba(230,57,70,0.08); border-color: rgba(230,57,70,0.3); }
.agent-done { color: #39d353; background: rgba(57,211,83,0.05); border-color: rgba(57,211,83,0.2); }
.log-container {
    background: #0d1117;
    border: 1px solid rgba(230,57,70,0.2);
    border-radius: 3px;
    padding: 1rem;
    height: 420px;
    overflow-y: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.76rem;
    line-height: 1.7;
}
.log-info { color: #c9d1d9; }
.log-success { color: #39d353; }
.log-error { color: #e63946; }
.log-warn { color: #e3b341; }
.log-time { color: #6e7681; margin-right: 0.5rem; }
.warning-box {
    background: rgba(230,57,70,0.08);
    border: 1px solid rgba(230,57,70,0.3);
    border-radius: 3px;
    padding: 0.7rem;
    font-size: 0.72rem;
    color: #e63946;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)


# ── SESSION STATE ─────────────────────────────────────────────────────────────

if "running" not in st.session_state:
    st.session_state.running = False
if "logs" not in st.session_state:
    st.session_state.logs = []
if "agents" not in st.session_state:
    st.session_state.agents = {
        "recon": "idle", "web": "idle", "network": "idle",
        "exploit": "idle", "report": "idle"
    }
if "result" not in st.session_state:
    st.session_state.result = None
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None
if "progress" not in st.session_state:
    st.session_state.progress = 0
if "done" not in st.session_state:
    st.session_state.done = False


# ── HELPERS ───────────────────────────────────────────────────────────────────

AGENT_INFO = {
    "recon":   ("🕵️", "Recon Specialist"),
    "web":     ("🌐", "Web Analyst"),
    "network": ("🔌", "Network Pentester"),
    "exploit": ("💥", "Exploit Specialist"),
    "report":  ("📝", "Report Writer"),
}

SCOPE_PRESETS = {
    "Custom": "",
    "Full scope": "Full scope — web, network, APIs, no data deletion, no DoS",
    "Web only": "Web application only — OWASP Top 10, APIs, auth testing, no network scanning",
    "Network only": "Network only — ports, services, CVEs, lateral movement, no web testing",
    "OSINT only": "Passive OSINT only — no active scanning, no intrusive testing",
    "Black-box": "Black-box assessment — no prior knowledge, standard professional pentesting rules",
}

FREE_MODELS = [
    "openrouter/openai/gpt-oss-120b:free",
    "openrouter/nvidia/nemotron-3-ultra-550b-a55b:free",
    "openrouter/nvidia/nemotron-3-super-120b-a12b:free",
    "openrouter/openai/gpt-oss-20b:free",
    "openrouter/openrouter/owl-alpha:free",
    "openrouter/openrouter/free",
]


def render_agents(agents: dict):
    html = ""
    for key, (icon, name) in AGENT_INFO.items():
        state = agents.get(key, "idle")
        if state == "running":
            badge = "⚙ RUNNING"
            cls = "agent-running"
        elif state == "done":
            badge = "✓ DONE"
            cls = "agent-done"
        else:
            badge = "IDLE"
            cls = "agent-idle"
        html += f'<div class="agent-row {cls}">{icon} <span style="flex:1">{name}</span><span style="font-size:0.62rem;letter-spacing:0.1em">{badge}</span></div>'
    return html


def render_logs(logs: list) -> str:
    lines = ""
    for entry in logs[-200:]:  # keep last 200 lines
        t = entry.get("time", "")
        m = entry.get("msg", "").replace("<", "&lt;").replace(">", "&gt;")
        lvl = entry.get("level", "info")
        lines += f'<span class="log-time">[{t}]</span><span class="log-{lvl}">{m}</span><br>'
    return lines


def generate_pdf(content: str, target: str) -> bytes:
    import io
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
        Table, TableStyle, HRFlowable, PageBreak)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        rightMargin=0.75*inch, leftMargin=0.75*inch,
        topMargin=1*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()

    title_s = ParagraphStyle("T", parent=styles["Title"], fontSize=26,
        textColor=colors.HexColor("#e63946"), spaceAfter=6, fontName="Helvetica-Bold")
    sub_s = ParagraphStyle("S", parent=styles["Normal"], fontSize=11,
        textColor=colors.HexColor("#555555"), spaceAfter=4)
    h1_s = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=15,
        textColor=colors.HexColor("#e63946"), spaceAfter=8, spaceBefore=16, fontName="Helvetica-Bold")
    h3_s = ParagraphStyle("H3", parent=styles["Heading3"], fontSize=11,
        textColor=colors.HexColor("#333333"), spaceAfter=4, spaceBefore=8, fontName="Helvetica-Bold")
    body_s = ParagraphStyle("B", parent=styles["Normal"], fontSize=10, leading=14, spaceAfter=6)
    code_s = ParagraphStyle("C", parent=styles["Code"], fontSize=8,
        backColor=colors.HexColor("#f1f1f1"), borderColor=colors.HexColor("#cccccc"),
        borderWidth=1, borderPad=6, fontName="Courier", spaceAfter=8)
    warn_s = ParagraphStyle("W", parent=styles["Normal"], fontSize=9,
        textColor=colors.HexColor("#7f0000"), backColor=colors.HexColor("#fff3f3"),
        borderColor=colors.HexColor("#e63946"), borderWidth=1, borderPad=6, spaceAfter=12)
    bullet_s = ParagraphStyle("BU", parent=styles["Normal"], fontSize=10,
        leading=14, spaceAfter=4, leftIndent=12)

    story = []
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("AXIOM", title_s))
    story.append(Paragraph("Professional Security Assessment Report", sub_s))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#e63946")))
    story.append(Spacer(1, 0.3*inch))

    cover = [["Target", target],
             ["Date", datetime.now().strftime("%B %d, %Y")],
             ["Classification", "CONFIDENTIAL"],
             ["Team", "Axiom Security"]]
    ct = Table(cover, colWidths=[1.5*inch, 4*inch])
    ct.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#1d3557")),
        ("TEXTCOLOR", (0,0), (0,-1), colors.white),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 10), ("PADDING", (0,0), (-1,-1), 8),
        ("ROWBACKGROUNDS", (1,0), (1,-1), [colors.HexColor("#f8f8f8"), colors.white]),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
    ]))
    story.append(ct)
    story.append(Spacer(1, 0.4*inch))
    story.append(Paragraph(
        "LEGAL DISCLAIMER: This report is confidential and prepared exclusively for authorized use. "
        "All testing was conducted with explicit written permission.", warn_s))
    story.append(PageBreak())

    in_code = False
    code_buf = []
    for line in content.split("\n"):
        s = line.strip()
        if s.startswith("```"):
            if in_code:
                if code_buf:
                    story.append(Paragraph("<br/>".join(
                        l.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                        for l in code_buf), code_s))
                code_buf = []; in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_buf.append(line); continue
        if s.startswith("## "): story.append(Paragraph(s[3:], h1_s)); story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e63946")))
        elif s.startswith("### "): story.append(Paragraph(s[4:], h3_s))
        elif s.startswith("# "): story.append(Paragraph(s[2:], h1_s))
        elif s.startswith("- ") or s.startswith("* "): story.append(Paragraph(f"• {s[2:]}", bullet_s))
        elif s.startswith("---"): story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
        elif s: story.append(Paragraph(s, body_s))
        else: story.append(Spacer(1, 6))

    doc.build(story)
    return buf.getvalue()


def run_axiom(target: str, scope: str, api_key: str, log_q: queue.Queue):
    """Run the full Axiom crew and push logs to the queue."""

    def emit(msg, level="info"):
        log_q.put({"msg": msg, "level": level, "time": datetime.now().strftime("%H:%M:%S")})

    try:
        os.environ["OPENROUTER_API_KEY"] = api_key

        import litellm
        from crewai import Agent, Task, Crew, Process, LLM
        from axiom_tools import (
            whois_lookup, dns_lookup, nmap_scan, nmap_vuln_scan,
            subfinder_enum, whatweb_scan, nikto_scan, http_headers,
            wafw00f_scan, ssl_scan, gobuster_scan, searchsploit,
            ping_sweep, smb_scan, theharvester, cert_lookup, traceroute,
        )

        litellm.set_verbose = False
        litellm.num_retries = 3

        emit("🔧 Initializing LLM with fallback router...")

        llm = LLM(
            model=FREE_MODELS[0],
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            temperature=0.2,
        )
        emit(f"✅ LLM ready — {FREE_MODELS[0]}")
        emit("🔧 Loading Kali Linux tools...")

        # Check which tools are available
        import shutil
        kali_tools = {
            "nmap": nmap_scan, "nikto": nikto_scan, "whatweb": whatweb_scan,
            "subfinder": subfinder_enum, "wafw00f": wafw00f_scan,
            "gobuster": gobuster_scan, "searchsploit": searchsploit,
            "theHarvester": theharvester, "sslscan": ssl_scan,
        }
        available = [t for t in kali_tools if shutil.which(t)]
        missing   = [t for t in kali_tools if not shutil.which(t)]
        emit(f"  ✅ Available: {', '.join(available) if available else 'none'}")
        if missing:
            emit(f"  ⚠️  Missing: {', '.join(missing)} — install with: sudo apt install {' '.join(missing)}", "warn")
        emit("━" * 48)

        # ── AGENTS ──
        emit("🤖 Spawning Axiom agents...")

        recon_agent = Agent(
            role="Reconnaissance Specialist",
            goal="Perform thorough passive and active reconnaissance on the target using REAL tools. Map the full attack surface with actual data.",
            backstory="Veteran OSINT operator with 10+ years in red team engagements. You MUST use your tools to gather real data. Never guess — always run the tool first.",
            llm=llm, verbose=False, allow_delegation=False,
            tools=[whois_lookup, dns_lookup, nmap_scan, subfinder_enum,
                   theharvester, cert_lookup, ping_sweep],
        )
        log_q.put({"agent": "recon", "state": "ready"})
        emit("  ✓ Recon Specialist ready")

        web_agent = Agent(
            role="Web Application Security Analyst",
            goal="Analyze the target's web applications for vulnerabilities using REAL scanning tools. Cover full OWASP Top 10 with actual scan data.",
            backstory="Certified web pentester (OSCP, BSCP). You always run your tools first, then analyze the real output. Never fabricate findings.",
            llm=llm, verbose=False, allow_delegation=False,
            tools=[whatweb_scan, nikto_scan, http_headers, wafw00f_scan,
                   ssl_scan, gobuster_scan],
        )
        log_q.put({"agent": "web", "state": "ready"})
        emit("  ✓ Web Analyst ready")

        network_agent = Agent(
            role="Network Penetration Tester",
            goal="Analyze the target's network for real vulnerabilities using nmap and other tools. Find actual open ports, services, and CVEs.",
            backstory="Network security expert. You run tools and analyze real results. Deep knowledge of TCP/IP, AD attacks, and enterprise infrastructure.",
            llm=llm, verbose=False, allow_delegation=False,
            tools=[nmap_scan, nmap_vuln_scan, smb_scan, searchsploit,
                   ping_sweep, traceroute],
        )
        log_q.put({"agent": "network", "state": "ready"})
        emit("  ✓ Network Pentester ready")

        exploit_agent = Agent(
            role="Exploitation Specialist",
            goal="Based on REAL scan results, build a prioritized attack plan with chained exploitation paths and actual CVEs found.",
            backstory="Elite offensive security engineer. You analyze real tool output and build realistic attack chains from actual findings.",
            llm=llm, verbose=False, allow_delegation=False,
            tools=[searchsploit],
        )
        log_q.put({"agent": "exploit", "state": "ready"})
        emit("  ✓ Exploit Specialist ready")

        report_agent = Agent(
            role="Senior Security Report Writer",
            goal="Compile REAL scan findings into a professional pentest report with CVSS scores and remediation.",
            backstory="Senior consultant who turns real tool output into actionable pentest reports for Fortune 500 companies.",
            llm=llm, verbose=False, allow_delegation=False,
        )
        log_q.put({"agent": "report", "state": "ready"})
        emit("  ✓ Report Writer ready")
        emit("━" * 48)

        # ── TASKS ──
        recon_task = Task(
            description=f"""
Perform comprehensive reconnaissance on the target.
TARGET: {target}
SCOPE: {scope}

PASSIVE RECON: WHOIS/DNS records, subdomain enumeration strategy, CT logs,
ASN/IP range mapping, Google dorks, Shodan/Censys queries, LinkedIn/social media,
GitHub leaks search, Wayback Machine historical data.

ACTIVE RECON: Port scanning methodology, service version detection,
web technology fingerprinting, WAF/CDN detection.

Include specific commands, tools, and queries for each technique.
""",
            agent=recon_agent,
            expected_output="Detailed recon report covering all attack surface elements.",
        )

        web_task = Task(
            description=f"""
Perform web application penetration test analysis.
TARGET: {target} | SCOPE: {scope}

Cover full OWASP Top 10:
A01 Broken Access Control, A02 Cryptographic Failures, A03 Injection (SQLi/XSS/XXE/SSTI/CMDi),
A04 Insecure Design, A05 Security Misconfiguration, A06 Vulnerable Components,
A07 Auth Failures, A08 Integrity Failures, A09 Logging Failures, A10 SSRF.

Also: API security, OAuth/SSO misconfigs, file upload vulns, CORS misconfigs,
subdomain takeover, HTTP header security, cookie flags.

For each finding: description, attack vector, payload examples, business impact.
""",
            agent=web_agent,
            expected_output="Complete web vulnerability analysis with findings, payloads, and impact.",
            context=[recon_task],
        )

        network_task = Task(
            description=f"""
Perform network penetration test analysis.
TARGET: {target} | SCOPE: {scope}

EXTERNAL: Open ports, CVEs in services, VPN/firewall misconfigs, exposed management
interfaces (RDP/SSH/SNMP/WinRM), email security (SPF/DKIM/DMARC), SSL/TLS vulns.

INTERNAL (if in scope): AD attack vectors (Kerberoasting, AS-REP Roasting, Pass-the-Hash),
SMB vulns, LLMNR/NBT-NS poisoning, lateral movement paths.

CLOUD: Misconfigured S3/Azure blobs, cloud metadata endpoints, IAM escalation.

Include CVE numbers, CVSS scores, and exploitation methods for each finding.
""",
            agent=network_agent,
            expected_output="Complete network vulnerability analysis with CVEs and lateral movement paths.",
            context=[recon_task],
        )

        exploit_task = Task(
            description=f"""
Build a comprehensive attack plan based on all discovered vulnerabilities.
TARGET: {target}

1. ATTACK CHAIN ANALYSIS — Most realistic path from initial access to full compromise
2. PRIORITIZED ATTACK SCENARIOS (3-5) with:
   - Entry point and trigger condition
   - Step-by-step exploitation sequence with tools/commands
   - Expected outcome and blast radius
   - Detection likelihood
3. PRIVILEGE ESCALATION PATHS — Low-privilege to admin/root/domain compromise
4. PERSISTENCE MECHANISMS — How attacker maintains long-term access
5. DATA EXFILTRATION PATHS — What data is accessible and how to exfiltrate

Rate each scenario by Likelihood (High/Med/Low) and Impact (Critical/High/Med/Low).
""",
            agent=exploit_agent,
            expected_output="Detailed attack plan with chained paths, step-by-step sequences, risk ratings.",
            context=[recon_task, web_task, network_task],
        )

        report_task = Task(
            description=f"""
Write a professional penetration test report.
TARGET: {target} | DATE: {datetime.now().strftime("%B %d, %Y")} | TEAM: Axiom Security

## EXECUTIVE SUMMARY
- Overall risk rating, key findings (non-technical), business impact, immediate actions

## SCOPE & METHODOLOGY

## FINDINGS SUMMARY TABLE
ID | Title | Category | CVSS Score | Severity | Status

## DETAILED FINDINGS
For each finding:
### [SEVERITY] FINDING-XXX: Title
- CVSS Score (with vector string)
- Category, Description, Evidence, Impact, Remediation, References

## ATTACK NARRATIVES (summarize main attack chains)

## REMEDIATION ROADMAP
- Immediate (0-7 days)
- Short-term (1 month)
- Long-term (3 months)

## CONCLUSION

Use CVSS v3.1 scoring throughout. Be thorough, technical, and precise.
""",
            agent=report_agent,
            expected_output="Complete professional pentest report with all sections, CVSS scores, remediation.",
            context=[recon_task, web_task, network_task, exploit_task],
        )

        # ── RUN CREW ──
        emit("📡 Phase 1/5 — Reconnaissance...")
        log_q.put({"agent": "recon", "state": "running"})

        crew = Crew(
            agents=[recon_agent, web_agent, network_agent, exploit_agent, report_agent],
            tasks=[recon_task, web_task, network_task, exploit_task, report_task],
            process=Process.sequential,
            verbose=False,
        )

        # Push phase updates while crew runs (approximate)
        def phase_updater():
            phases = [
                (8,  "recon",   "done",    "web",     "running", "🌐 Phase 2/5 — Web application analysis..."),
                (16, "web",     "done",    "network", "running", "🔌 Phase 3/5 — Network penetration testing..."),
                (24, "network", "done",    "exploit", "running", "💥 Phase 4/5 — Building attack chains..."),
                (32, "exploit", "done",    "report",  "running", "📝 Phase 5/5 — Compiling report..."),
            ]
            for delay, prev, prev_state, curr, curr_state, msg in phases:
                time.sleep(delay)
                log_q.put({"agent": prev, "state": prev_state})
                log_q.put({"agent": curr, "state": curr_state})
                emit(msg)

        updater = threading.Thread(target=phase_updater, daemon=True)
        updater.start()

        result = crew.kickoff()

        emit("━" * 48)
        emit("✅ All agents complete!", "success")

        log_q.put({"agent": "report", "state": "done"})
        log_q.put({"result": str(result)})
        emit("💾 Generating PDF report...", "info")
        log_q.put({"done": True, "result": str(result)})

    except Exception as e:
        emit(f"❌ Error: {str(e)}", "error")
        log_q.put({"error": str(e), "done": True})


# ── LAYOUT ────────────────────────────────────────────────────────────────────

# SIDEBAR
with st.sidebar:
    st.markdown('<p class="axiom-title">AXIOM</p>', unsafe_allow_html=True)
    st.markdown('<p class="axiom-sub">Professional Pentest Suite</p>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<p class="section-label">🔑 API Configuration</p>', unsafe_allow_html=True)
    api_key = st.text_input("OpenRouter API Key", type="password",
        placeholder="sk-or-v1-...", help="Get a free key at openrouter.ai")

    st.markdown("---")
    st.markdown('<p class="section-label">🎯 Target</p>', unsafe_allow_html=True)
    target = st.text_input("Target", placeholder="192.168.1.1 or https://example.com")

    st.markdown('<p class="section-label">📋 Scope</p>', unsafe_allow_html=True)
    preset = st.selectbox("Quick presets", list(SCOPE_PRESETS.keys()))
    scope = st.text_area("Scope definition",
        value=SCOPE_PRESETS[preset],
        placeholder="Describe what is in/out of scope...",
        height=80)

    st.markdown("---")
    authorized = st.checkbox(
        "⚠️ I confirm I have explicit written authorization to test this target. Unauthorized testing is illegal.",
        value=False
    )

    st.markdown("---")
    launch = st.button("⚡ LAUNCH AXIOM", use_container_width=True,
        disabled=st.session_state.running)

    if st.session_state.done and not st.session_state.running:
        st.markdown("---")
        st.markdown('<p class="section-label">📁 Download Reports</p>', unsafe_allow_html=True)
        if st.session_state.result:
            st.download_button(
                "📄 Download PDF Report",
                data=generate_pdf(st.session_state.result, st.session_state.get("target_used", "target")),
                file_name=f"axiom_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
            st.download_button(
                "📝 Download Attack Plan (.md)",
                data=st.session_state.result.encode(),
                file_name=f"axiom_attack_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True,
            )

# MAIN AREA
col1, col2 = st.columns([3, 2])

with col1:
    # Terminal header
    status_color = "#39d353" if st.session_state.done else ("#e63946" if st.session_state.running else "#6e7681")
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.7rem;padding:0.5rem 0.8rem;
        background:#0d1117;border:1px solid rgba(230,57,70,0.2);border-radius:3px;margin-bottom:0.5rem;">
      <span style="background:#ff5f57;width:10px;height:10px;border-radius:50%;display:inline-block"></span>
      <span style="background:#febc2e;width:10px;height:10px;border-radius:50%;display:inline-block"></span>
      <span style="background:#28c840;width:10px;height:10px;border-radius:50%;display:inline-block"></span>
      <span style="color:#6e7681;font-size:0.7rem;margin-left:0.3rem">axiom@pentest ~ %</span>
      <span style="margin-left:auto;width:8px;height:8px;border-radius:50%;
        background:{status_color};display:inline-block"></span>
    </div>
    """, unsafe_allow_html=True)

    # Progress bar
    if st.session_state.running or st.session_state.done:
        st.progress(st.session_state.progress / 100)

    # Terminal output
    log_placeholder = st.empty()

    if not st.session_state.logs:
        log_placeholder.markdown("""
<div class="log-container" style="display:flex;align-items:center;justify-content:center;flex-direction:column;gap:1rem;">
  <pre style="color:#7a1a20;font-size:0.6rem;line-height:1.3;text-align:center">
 █████╗ ██╗  ██╗██╗ ██████╗ ███╗   ███╗
██╔══██╗╚██╗██╔╝██║██╔═══██╗████╗ ████║
███████║ ╚███╔╝ ██║██║   ██║██╔████╔██║
██╔══██║ ██╔██╗ ██║██║   ██║██║╚██╔╝██║
██║  ██║██╔╝ ██╗██║╚██████╔╝██║ ╚═╝ ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚═╝</pre>
  <span style="color:#6e7681;font-size:0.72rem;letter-spacing:0.15em">Configure target and launch crew</span>
  <span style="color:#7a1a20;font-size:0.65rem">⚠ Authorized use only</span>
</div>
""", unsafe_allow_html=True)
    else:
        log_placeholder.markdown(
            f'<div class="log-container">{render_logs(st.session_state.logs)}</div>',
            unsafe_allow_html=True
        )

with col2:
    st.markdown('<p class="section-label">🤖 Agent Status</p>', unsafe_allow_html=True)
    agent_placeholder = st.empty()
    agent_placeholder.markdown(render_agents(st.session_state.agents), unsafe_allow_html=True)

    if st.session_state.done and st.session_state.result:
        st.markdown("---")
        st.markdown('<p class="section-label">📊 Report Preview</p>', unsafe_allow_html=True)
        with st.expander("View findings", expanded=True):
            preview = st.session_state.result[:2000] + "\n\n*[truncated — download full report above]*"
            st.markdown(preview)


# ── LAUNCH HANDLER ────────────────────────────────────────────────────────────

if launch:
    if not api_key:
        st.sidebar.error("❌ OpenRouter API key is required")
    elif not target:
        st.sidebar.error("❌ Target is required")
    elif not authorized:
        st.sidebar.error("❌ You must confirm authorization")
    else:
        # Reset state
        st.session_state.running = True
        st.session_state.done = False
        st.session_state.logs = []
        st.session_state.result = None
        st.session_state.pdf_bytes = None
        st.session_state.progress = 0
        st.session_state.agents = {k: "idle" for k in AGENT_INFO}
        st.session_state.target_used = target

        log_q = queue.Queue()

        thread = threading.Thread(
            target=run_axiom,
            args=(target, scope, api_key, log_q),
            daemon=True
        )
        thread.start()

        progress_steps = {
            "recon_running": 10, "web_running": 35,
            "network_running": 55, "exploit_running": 75,
            "report_running": 90,
        }

        # Stream logs in real time
        while True:
            try:
                item = log_q.get(timeout=60)
            except queue.Empty:
                break

            # Agent state update
            if "agent" in item and "state" in item:
                st.session_state.agents[item["agent"]] = item["state"]
                key = f"{item['agent']}_{item['state']}"
                if key in progress_steps:
                    st.session_state.progress = progress_steps[key]
                agent_placeholder.markdown(render_agents(st.session_state.agents), unsafe_allow_html=True)
                continue

            # Done signal
            if item.get("done"):
                if item.get("result"):
                    st.session_state.result = item["result"]
                if item.get("error"):
                    st.session_state.logs.append({"msg": f"❌ {item['error']}", "level": "error", "time": datetime.now().strftime("%H:%M:%S")})
                st.session_state.progress = 100
                st.session_state.running = False
                st.session_state.done = True
                break

            # Regular log line
            if "msg" in item:
                st.session_state.logs.append(item)
                log_placeholder.markdown(
                    f'<div class="log-container">{render_logs(st.session_state.logs)}</div>',
                    unsafe_allow_html=True
                )

        st.rerun()
