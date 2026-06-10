"""Report Agent - Synthesizes all findings into a professional security report."""

from typing import Optional, List, Dict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from axiom.models.findings import AgentState, ReportAnalysis, Finding, Severity
from axiom.config.settings import settings


class ReportAgent:
    """Agent that synthesizes technical findings into executive-level reports."""

    def __init__(self, model: Optional[str] = None, temperature: float = 0.2):
        self.llm = ChatOpenAI(
            model=model or settings.default_model,
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
            temperature=temperature,
        )
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for reporting."""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("synthesize_findings", self._synthesize_findings)

        # Set entry point
        workflow.set_entry_point("synthesize_findings")

        # Add edges
        workflow.add_edge("synthesize_findings", END)

        return workflow.compile()

    def _synthesize_findings(self, state: AgentState) -> AgentState:
        """Synthesize all technical data into a professional report."""
        state.current_step = "synthesizing_report"
        
        # Consolidate findings
        all_findings = []
        if state.analysis: all_findings.extend(state.analysis.findings)
        if state.web_analysis: all_findings.extend(state.web_analysis.findings)
        if state.exploit_analysis: all_findings.extend(state.exploit_analysis.potential_exploits)
        
        severity_counts = self._count_severities(all_findings)
        
        prompt = self._create_synthesis_prompt(state, all_findings, severity_counts)

        try:
            structured_llm = self.llm.with_structured_output(ReportAnalysis)
            report = structured_llm.invoke(prompt)
            
            report.target = state.target
            report.total_vulnerabilities = len(all_findings)
            report.severity_counts = severity_counts
            
            state.report_analysis = report
            state.current_step = "complete"
        except Exception as e:
            state.error = f"Report synthesis failed: {str(e)}"
            state.current_step = "error"

        return state

    def _count_severities(self, findings: List[Finding]) -> Dict[str, int]:
        """Count findings by severity."""
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for f in findings:
            counts[f.severity.value] += 1
        return counts

    def _create_synthesis_prompt(self, state: AgentState, findings: List[Finding], counts: Dict[str, int]) -> str:
        """Create the final synthesis prompt for the LLM."""
        findings_text = "\n".join([f"- {f.title} ({f.severity.value}): {f.description[:200]}..." for f in findings])
        
        recon_info = state.analysis.scan_summary if state.analysis else "N/A"
        web_info = state.web_analysis.summary if state.web_analysis else "N/A"
        exploit_info = state.exploit_analysis.risk_assessment if state.exploit_analysis else "N/A"

        return f"""You are a senior security consultant. Synthesize the following technical security findings for target {state.target} into a professional executive-level report.

TECHNICAL CONTEXT:
- Network Recon: {recon_info}
- Web Analysis: {web_info}
- Exploit Research: {exploit_info}

SEVERITY SUMMARY:
{counts}

DETAILED FINDINGS LIST:
{findings_text}

Your task:
1. Write a professional Executive Summary (business impact focused)
2. Summarize key findings in a cohesive narrative
3. Write a Technical Details section summarizing the attack surface and vulnerabilities
4. Create a prioritized Remediation Roadmap

Return a structured ReportAnalysis object with:
- executive_summary: Professional overview for stakeholders
- key_findings_summary: Narrative of most critical issues
- technical_details: Summary of technical assessment results
- remediation_roadmap: Ordered list of strategic remediation steps"""

    def run(self, state: AgentState) -> AgentState:
        """Run the reporting workflow on a completed state."""
        return self.graph.invoke(state)
