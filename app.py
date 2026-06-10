import streamlit as st
import asyncio
import os
import tempfile
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from axiom.agents.recon_agent import ReconAgent
from axiom.agents.web_agent import WebAgent
from axiom.agents.exploit_agent import ExploitAgent
from axiom.agents.report_agent import ReportAgent
from axiom.models.findings import AgentState, ReconAnalysis, WebAnalysis, ExploitAnalysis, ReportAnalysis, Finding, Severity
from axiom.utils.report_gen import PDFGenerator, MarkdownGenerator

# Page configuration
st.set_page_config(
    page_title="Axiom | AI Security Pentest",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

def display_findings(findings: List[Finding]):
    """Helper to display findings in a consistent card format."""
    if not findings:
        st.success("No security findings identified.")
        return

    for f in findings:
        severity_class = f"severity-{f.severity.value}"
        with st.container():
            st.markdown(f"""
                <div class="finding-card {severity_class}">
                    <h4>{f.title} ({f.severity.value.upper()})</h4>
                    <p><strong>Category:</strong> {f.category} | <strong>Port:</strong> {f.port or 'N/A'}</p>
                    <p>{f.description}</p>
                </div>
            """, unsafe_allow_html=True)
            with st.expander("Show Evidence & Remediation"):
                st.text_area("Evidence", f.evidence, height=100, disabled=True)
                st.info(f"**Remediation:** {f.remediation}")
                if f.cve_ids:
                    st.write(f"**CVEs:** {', '.join(f.cve_ids)}")

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stMetric {
        background-color: #1e2128;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    .finding-card {
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid;
        margin-bottom: 15px;
        background-color: #1e2128;
    }
    .severity-critical { border-left-color: #ff4b4b; }
    .severity-high { border-left-color: #ff8c00; }
    .severity-medium { border-left-color: #ffcc00; }
    .severity-low { border-left-color: #2ecc71; }
    .severity-info { border-left-color: #3498db; }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=80)
    st.title("Axiom AI Suite")
    st.markdown("---")
    
    st.subheader("Configuration")
    api_key = st.text_input("OpenRouter API Key", 
                           value=os.getenv("OPENROUTER_API_KEY", ""), 
                           type="password")
    
    model = st.selectbox("LLM Model", 
                        options=[
                            "openrouter/openai/gpt-oss-120b:free",
                            "openrouter/google/gemini-2.0-flash-001",
                            "openrouter/anthropic/claude-3.5-sonnet",
                            "openrouter/meta-llama/llama-3.1-405b-instruct"
                        ],
                        index=0)
    
    st.markdown("---")
    st.info("Phase 4: Full Audit & Reporting active.")

# Main UI
st.title("🛡️ Axiom AI Security Suite")
st.markdown("Professional-grade AI-powered penetration testing and automated reporting.")

col_target, col_mode = st.columns([3, 1])
with col_target:
    target = st.text_input("Target (Domain or IP)", placeholder="e.g., scanme.nmap.org")
with col_mode:
    mode = st.selectbox("Scan Mode", options=["Full Audit", "Network Recon", "Web Analysis", "Exploit Research"])

if st.button(f"🚀 Start {mode}", use_container_width=True):
    if not api_key:
        st.error("Please provide an OpenRouter API Key in the sidebar.")
    elif not target:
        st.warning("Please enter a target to scan.")
    else:
        # Update environment variable for the agent
        os.environ["OPENROUTER_API_KEY"] = api_key
        
        with st.status(f"🛠️ Running {mode} Workflow...", expanded=True) as status:
            try:
                state = AgentState(target=target)
                recon_agent = ReconAgent(model=model)
                web_agent = WebAgent(model=model)
                exploit_agent = ExploitAgent(model=model)
                report_agent = ReportAgent(model=model)

                # --- 1. Network Recon (Base for all except Web Analysis) ---
                if mode in ["Full Audit", "Network Recon", "Exploit Research"]:
                    st.write("🔍 Phase: Network Reconnaissance...")
                    state = recon_agent._validate_target(state)
                    state = recon_agent._run_nmap(state)
                    state = recon_agent._analyze_results(state)
                    if state.error:
                        st.error(f"Recon Error: {state.error}")
                
                # --- 2. Web Analysis ---
                if mode in ["Full Audit", "Web Analysis"]:
                    st.write("🌐 Phase: Web Analysis...")
                    if mode == "Web Analysis": 
                        state = web_agent._validate_target(state)
                    state = web_agent._identify_tech(state)
                    state = web_agent._detect_waf(state)
                    state = web_agent._vulnerability_scan(state)
                    state = web_agent._analyze_results(state)
                    if state.error:
                        st.error(f"Web Error: {state.error}")

                # --- 3. Exploit Research ---
                if mode in ["Full Audit", "Exploit Research"]:
                    st.write("💣 Phase: Exploit Research...")
                    state = exploit_agent._identify_targets(state)
                    state = exploit_agent._search_exploits(state)
                    state = exploit_agent._analyze_vectors(state)
                    if state.error:
                        st.error(f"Exploit Error: {state.error}")

                # --- 4. Report Generation (Only for Full Audit) ---
                if mode == "Full Audit":
                    st.write("📝 Phase: Automated Reporting...")
                    state = report_agent._synthesize_findings(state)
                    if state.error:
                        st.error(f"Report Error: {state.error}")

                status.update(label=f"✅ {mode} Successful", state="complete", expanded=False)

                # --- UI Rendering of Results ---
                st.divider()

                if mode == "Full Audit":
                    report: ReportAnalysis = state.report_analysis
                    st.header("📊 Executive Security Report")
                    
                    # High level metrics
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Critical", report.severity_counts.get("critical", 0))
                    m2.metric("High", report.severity_counts.get("high", 0))
                    m3.metric("Medium", report.severity_counts.get("medium", 0))
                    m4.metric("Total Findings", report.total_vulnerabilities)

                    tab1, tab2, tab3, tab4 = st.tabs(["📋 Executive Summary", "🔍 Findings Detail", "🛣️ Remediation", "📦 Export"])
                    
                    with tab1:
                        st.subheader("Executive Summary")
                        st.write(report.executive_summary)
                        st.subheader("Key Findings")
                        st.write(report.key_findings_summary)
                        st.subheader("Technical Assessment Overview")
                        st.write(report.technical_details)
                    
                    with tab2:
                        all_findings = []
                        if state.analysis: all_findings.extend(state.analysis.findings)
                        if state.web_analysis: all_findings.extend(state.web_analysis.findings)
                        if state.exploit_analysis: all_findings.extend(state.exploit_analysis.potential_exploits)
                        display_findings(all_findings)
                    
                    with tab3:
                        st.subheader("Remediation Roadmap")
                        for i, step in enumerate(report.remediation_roadmap):
                            st.markdown(f"**{i+1}.** {step}")
                    
                    with tab4:
                        st.subheader("Download Reports")
                        col_pdf, col_md = st.columns(2)
                        
                        # Generate reports in temp files
                        with col_pdf:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                                PDFGenerator(state).generate(tmp.name)
                                with open(tmp.name, "rb") as f:
                                    st.download_button(
                                        "📥 Download PDF Report",
                                        f,
                                        file_name=f"Axiom_Report_{target}.pdf",
                                        mime="application/pdf"
                                    )
                                os.unlink(tmp.name)
                        
                        with col_md:
                            md_content = MarkdownGenerator(state).generate()
                            st.download_button(
                                "📥 Download Markdown Report",
                                md_content,
                                file_name=f"Axiom_Report_{target}.md",
                                mime="text/markdown"
                            )

                elif mode == "Network Recon":
                    # Display Recon Results (Reuse Phase 1 logic)
                    analysis: ReconAnalysis = state.analysis
                    st.header("🔍 Network Reconnaissance Results")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Hosts", analysis.hosts_scanned)
                    col2.metric("Open Ports", analysis.total_open_ports)
                    risky = len([f for f in analysis.findings if f.severity in [Severity.CRITICAL, Severity.HIGH]])
                    col3.metric("High/Crit", risky)
                    display_findings(analysis.findings)

                elif mode == "Web Analysis":
                    # Display Web Results (Reuse Phase 2 logic)
                    st.header("🌐 Web Analysis Results")
                    web_analysis: WebAnalysis = state.web_analysis
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Techs", len(web_analysis.tech_stack))
                    col2.metric("WAF", web_analysis.waf_name if web_analysis.waf_detected else "None")
                    risky = len([f for f in web_analysis.findings if f.severity in [Severity.CRITICAL, Severity.HIGH]])
                    col3.metric("High/Crit", risky)
                    display_findings(web_analysis.findings)

                elif mode == "Exploit Research":
                    # Display Exploit Results (Reuse Phase 3 logic)
                    st.header("💣 Exploit Research Results")
                    exploit_analysis: ExploitAnalysis = state.exploit_analysis
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Checked", exploit_analysis.vulnerabilities_analyzed)
                    col2.metric("Exploits", len(exploit_analysis.potential_exploits))
                    col3.metric("Vectors", len(exploit_analysis.attack_vectors))
                    display_findings(exploit_analysis.potential_exploits)

            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
                status.update(label="💥 Execution Crashed", state="error")

# Footer
st.markdown("---")
st.markdown("Axiom AI Security Suite - Authorized Use Only. Clean Architecture Rebuild.")
