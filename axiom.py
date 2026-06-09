"""
 █████╗ ██╗  ██╗██╗ ██████╗ ███╗   ███╗
██╔══██╗╚██╗██╔╝██║██╔═══██╗████╗ ████║
███████║ ╚███╔╝ ██║██║   ██║██╔████╔██║
██╔══██║ ██╔██╗ ██║██║   ██║██║╚██╔╝██║
██║  ██║██╔╝ ██╗██║╚██████╔╝██║ ╚═╝ ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚═╝
Professional Pentesting AI Team — CLI Mode
⚠️  For authorized security testing only ⚠️
"""

import os, sys, io
from datetime import datetime
import litellm
from crewai import Agent, Task, Crew, Process, LLM
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable, PageBreak)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from axiom_tools import (
    whois_lookup, dns_lookup, nmap_scan, nmap_vuln_scan,
    subfinder_enum, whatweb_scan, nikto_scan, http_headers,
    wafw00f_scan, ssl_scan, gobuster_scan, searchsploit,
    ping_sweep, smb_scan, theharvester, cert_lookup, traceroute,
)

# ── CONFIG ────────────────────────────────────────────────────────────────────

API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    print("❌ Set OPENROUTER_API_KEY environment variable first.")
    sys.exit(1)

litellm.set_verbose = False
litellm.num_retries = 3

FREE_MODELS = [
    "openrouter/openai/gpt-oss-120b:free",
    "openrouter/nvidia/nemotron-3-ultra-550b-a55b:free",
    "openrouter/nvidia/nemotron-3-super-120b-a12b:free",
    "openrouter/openai/gpt-oss-20b:free",
    "openrouter/openrouter/owl-alpha:free",
    "openrouter/openrouter/free",
]

llm = LLM(
    model=FREE_MODELS[0],
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
    temperature=0.2,
)

# ── AGENTS ────────────────────────────────────────────────────────────────────

recon_agent = Agent(
    role="Reconnaissance Specialist",
    goal="Perform thorough reconnaissance using REAL tools. Map the full attack surface with actual data.",
    backstory="Veteran OSINT operator. You MUST use your tools — never guess.",
    llm=llm, verbose=True, allow_delegation=False,
    tools=[whois_lookup, dns_lookup, nmap_scan, subfinder_enum,
           theharvester, cert_lookup, ping_sweep],
)

web_agent = Agent(
    role="Web Application Security Analyst",
    goal="Find web vulnerabilities using REAL scanning tools. Cover OWASP Top 10 with actual scan data.",
    backstory="Certified web pentester. Run tools first, analyze real output.",
    llm=llm, verbose=True, allow_delegation=False,
    tools=[whatweb_scan, nikto_scan, http_headers, wafw00f_scan, ssl_scan, gobuster_scan],
)

network_agent = Agent(
    role="Network Penetration Tester",
    goal="Find real network vulnerabilities with nmap and other tools. Report actual open ports, services, CVEs.",
    backstory="Network security expert. You run tools and analyze real results.",
    llm=llm, verbose=True, allow_delegation=False,
    tools=[nmap_scan, nmap_vuln_scan, smb_scan, searchsploit, ping_sweep, traceroute],
)

exploit_agent = Agent(
    role="Exploitation Specialist",
    goal="Based on REAL scan results, build a prioritized attack plan with actual CVEs found.",
    backstory="Elite offensive security engineer. Build realistic attack chains from real findings.",
    llm=llm, verbose=True, allow_delegation=False,
    tools=[searchsploit],
)

report_agent = Agent(
    role="Senior Security Report Writer",
    goal="Compile REAL scan findings into a professional pentest report with CVSS scores.",
    backstory="Senior consultant who turns real tool output into actionable reports.",
    llm=llm, verbose=True, allow_delegation=False,
)

# ── TASKS ─────────────────────────────────────────────────────────────────────

def build_tasks(target: str, scope: str):
    recon_task = Task(
        description=f"""
Perform comprehensive reconnaissance on the target.
TARGET: {target} | SCOPE: {scope}

Use your tools in this order:
1. whois_lookup — get registrar, org, nameservers
2. dns_lookup — get all DNS records (A, MX, NS, TXT, SPF, DMARC)
3. ping_sweep — if target is a CIDR, discover live hosts
4. nmap_scan — identify open ports and services
5. subfinder_enum — enumerate subdomains (if domain target)
6. theharvester — gather emails and additional subdomains
7. cert_lookup — check certificate transparency logs

Run ALL tools and document every finding. Never skip a tool.
""",
        agent=recon_agent,
        expected_output="Detailed recon report with real tool output and findings.",
    )

    web_task = Task(
        description=f"""
Perform web application penetration testing on the target.
TARGET: {target} | SCOPE: {scope}

Use your tools in this order:
1. http_headers — analyze security headers, cookie flags
2. whatweb_scan — fingerprint technologies, CMS, frameworks
3. wafw00f_scan — detect WAF/CDN protecting the target
4. ssl_scan — check TLS version and cipher strength
5. nikto_scan — scan for web vulnerabilities and misconfigurations
6. gobuster_scan — brute-force hidden directories and endpoints

Analyze ALL real output. Identify OWASP Top 10 issues, misconfigs, and weak headers.
""",
        agent=web_agent,
        expected_output="Web vulnerability findings from real tool output.",
        context=[recon_task],
    )

    network_task = Task(
        description=f"""
Perform network penetration testing on the target.
TARGET: {target} | SCOPE: {scope}

Use your tools in this order:
1. nmap_scan — detailed port + service version scan
2. nmap_vuln_scan — run NSE vulnerability scripts
3. smb_scan — check SMB for EternalBlue and null sessions (if port 445 open)
4. searchsploit — look up CVEs for any services/versions found
5. traceroute — map network path to target

Document every real finding with port, service, version, and CVE if applicable.
""",
        agent=network_agent,
        expected_output="Network vulnerability findings from real scans with CVEs.",
        context=[recon_task],
    )

    exploit_task = Task(
        description=f"""
Build a comprehensive attack plan from the REAL findings.
TARGET: {target}

1. Review all real scan results from previous agents
2. For each vulnerable service found, run searchsploit to find real exploits
3. Build attack chains from actual vulnerabilities — no hypotheticals
4. Prioritize by exploitability and business impact
5. Document step-by-step attack paths using real CVEs and tools

Rate each scenario: Likelihood (High/Med/Low) × Impact (Critical/High/Med/Low)
""",
        agent=exploit_agent,
        expected_output="Attack plan based on real findings with actual CVEs and exploitation steps.",
        context=[recon_task, web_task, network_task],
    )

    report_task = Task(
        description=f"""
Write a professional penetration test report from ALL real findings.
TARGET: {target} | DATE: {datetime.now().strftime("%B %d, %Y")} | TEAM: Axiom Security

## EXECUTIVE SUMMARY (overall risk, top 5 findings, business impact, immediate actions)
## SCOPE & METHODOLOGY
## FINDINGS SUMMARY TABLE (ID | Title | Category | CVSS | Severity | Status)
## DETAILED FINDINGS
For each finding:
### [SEVERITY] FINDING-XXX: Title
- CVSS Score (v3.1 vector)
- Category, Description, Evidence (real tool output), Impact, Remediation, References
## ATTACK NARRATIVES (real attack chains from findings)
## REMEDIATION ROADMAP (Immediate 0-7d / Short-term 1mo / Long-term 3mo)
## CONCLUSION

Base everything on REAL tool output only. Use CVSS v3.1 scoring.
""",
        agent=report_agent,
        expected_output="Complete professional pentest report based on real findings.",
        context=[recon_task, web_task, network_task, exploit_task],
    )

    return [recon_task, web_task, network_task, exploit_task, report_task]


# ── PDF GENERATOR ─────────────────────────────────────────────────────────────

def generate_pdf(content: str, target: str, output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=A4,
        rightMargin=0.75*inch, leftMargin=0.75*inch,
        topMargin=1*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=16,
        textColor=colors.HexColor("#e63946"), spaceAfter=8, spaceBefore=16, fontName="Helvetica-Bold")
    h3 = ParagraphStyle("H3", parent=styles["Heading3"], fontSize=11,
        textColor=colors.HexColor("#333333"), spaceAfter=4, spaceBefore=8, fontName="Helvetica-Bold")
    body = ParagraphStyle("B", parent=styles["Normal"], fontSize=10, leading=14, spaceAfter=6)
    code_s = ParagraphStyle("C", parent=styles["Code"], fontSize=8,
        backColor=colors.HexColor("#f1f1f1"), borderWidth=1,
        borderColor=colors.HexColor("#cccccc"), borderPad=6,
        fontName="Courier", spaceAfter=8)
    warn = ParagraphStyle("W", parent=styles["Normal"], fontSize=9,
        textColor=colors.HexColor("#7f0000"), backColor=colors.HexColor("#fff3f3"),
        borderColor=colors.HexColor("#e63946"), borderWidth=1, borderPad=6, spaceAfter=12)
    bullet = ParagraphStyle("BU", parent=styles["Normal"], fontSize=10, leading=14,
        spaceAfter=4, leftIndent=12)

    story = [Spacer(1, 0.5*inch)]
    story.append(Paragraph("AXIOM", ParagraphStyle("T", parent=styles["Title"],
        fontSize=26, textColor=colors.HexColor("#e63946"), fontName="Helvetica-Bold")))
    story.append(Paragraph("Professional Security Assessment", ParagraphStyle("S",
        parent=styles["Normal"], fontSize=11, textColor=colors.HexColor("#555555"))))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#e63946")))
    story.append(Spacer(1, 0.3*inch))

    ct = Table([
        ["Target", target],
        ["Date", datetime.now().strftime("%B %d, %Y")],
        ["Classification", "CONFIDENTIAL"],
        ["Team", "Axiom Security"],
    ], colWidths=[1.5*inch, 4*inch])
    ct.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#1d3557")),
        ("TEXTCOLOR", (0,0), (0,-1), colors.white),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 10), ("PADDING", (0,0), (-1,-1), 8),
        ("ROWBACKGROUNDS", (1,0), (1,-1), [colors.HexColor("#f8f8f8"), colors.white]),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
    ]))
    story += [ct, Spacer(1, 0.4*inch),
        Paragraph("LEGAL DISCLAIMER: Confidential. Authorized use only.", warn),
        PageBreak()]

    in_code, code_buf = False, []
    for line in content.split("\n"):
        s = line.strip()
        if s.startswith("```"):
            if in_code:
                story.append(Paragraph("<br/>".join(
                    l.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                    for l in code_buf), code_s))
                code_buf = []; in_code = False
            else:
                in_code = True
            continue
        if in_code: code_buf.append(line); continue
        if s.startswith("## "): story += [Paragraph(s[3:], h1), HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e63946"))]
        elif s.startswith("### "): story.append(Paragraph(s[4:], h3))
        elif s.startswith("# "): story.append(Paragraph(s[2:], h1))
        elif s.startswith("- ") or s.startswith("* "): story.append(Paragraph(f"• {s[2:]}", bullet))
        elif s.startswith("---"): story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
        elif s: story.append(Paragraph(s, body))
        else: story.append(Spacer(1, 6))
    doc.build(story)
    print(f"✅ PDF saved: {output_path}")


# ── MAIN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  AXIOM — Professional Pentesting Team (CLI)")
    print("  ⚠️  Authorized use only.")
    print("=" * 60)

    target = input("\n🎯 Target (IP or URL): ").strip()
    if not target: sys.exit("No target provided.")

    scope = input("📋 Scope (or Enter for default): ").strip()
    if not scope:
        scope = f"Target: {target} — Standard black-box, no destructive testing"

    if input(f"\n⚠️  Confirm authorization to test '{target}'? (yes/no): ").strip().lower() != "yes":
        sys.exit("Authorization not confirmed.")

    tasks = build_tasks(target, scope)
    crew = Crew(
        agents=[recon_agent, web_agent, network_agent, exploit_agent, report_agent],
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )

    print("\n🚀 Launching Axiom crew...\n")
    result = crew.kickoff()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = target.replace("https://","").replace("http://","").replace("/","_").replace(".","_")

    md_path = f"axiom_{safe}_{timestamp}_attack_plan.md"
    pdf_path = f"axiom_{safe}_{timestamp}_report.pdf"

    with open(md_path, "w") as f:
        f.write(f"# Axiom Security Assessment\n**Target:** {target}\n**Date:** {datetime.now().strftime('%B %d, %Y')}\n\n---\n\n")
        f.write(str(result))
    print(f"✅ Attack plan: {md_path}")

    generate_pdf(str(result), target, pdf_path)
