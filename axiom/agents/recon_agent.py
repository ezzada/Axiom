"""Recon Agent - Performs network reconnaissance using nmap and LLM analysis."""

from typing import Optional
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from axiom.models.findings import AgentState, ReconAnalysis, Finding, Severity, NmapScanResult, HostInfo, PortInfo
from axiom.tools.nmap import NmapScanner
from axiom.config.settings import settings


class ReconAgent:
    """Reconnaissance agent that scans targets and analyzes findings with LLM."""

    def __init__(self, model: Optional[str] = None, temperature: float = 0.1):
        self.llm = ChatOpenAI(
            model=model or settings.default_model,
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
            temperature=temperature,
        )
        self.scanner = NmapScanner()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for reconnaissance."""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("validate_target", self._validate_target)
        workflow.add_node("run_nmap", self._run_nmap)
        workflow.add_node("analyze_results", self._analyze_results)

        # Set entry point
        workflow.set_entry_point("validate_target")

        # Add edges
        workflow.add_edge("validate_target", "run_nmap")
        workflow.add_edge("run_nmap", "analyze_results")
        workflow.add_edge("analyze_results", END)

        return workflow.compile()

    def _validate_target(self, state: AgentState) -> AgentState:
        """Validate and normalize the target input."""
        from axiom.models.target import Target

        try:
            target_obj = Target(value=state.target)
            state.target_obj = target_obj
            state.current_step = "target_validated"
            state.error = None
        except Exception as e:
            state.error = f"Invalid target: {str(e)}"
            state.current_step = "error"

        return state

    def _run_nmap(self, state: AgentState) -> AgentState:
        """Run nmap scan against the target."""
        if state.error:
            return state

        scan_target = state.target_obj.get_scan_target()
        state.current_step = "running_nmap"

        try:
            nmap_result = self.scanner.scan(scan_target, scan_type="default")
            state.nmap_result = nmap_result
            state.current_step = "nmap_complete"
        except Exception as e:
            state.error = f"Nmap scan failed: {str(e)}"
            state.current_step = "error"

        return state

    def _analyze_results(self, state: AgentState) -> AgentState:
        """Analyze nmap results using LLM and produce structured findings."""
        if state.error or not state.nmap_result:
            return state

        state.current_step = "analyzing"

        # Prepare summary for LLM
        scan_summary = self._create_scan_summary(state.nmap_result)

        # Create analysis prompt
        prompt = self._create_analysis_prompt(state.target, scan_summary, state.nmap_result.raw_output)

        try:
            # Use structured output
            structured_llm = self.llm.with_structured_output(ReconAnalysis)
            analysis = structured_llm.invoke(prompt)

            # Ensure target is set
            analysis.target = state.target
            state.analysis = analysis
            state.current_step = "complete"
        except Exception as e:
            state.error = f"Analysis failed: {str(e)}"
            state.current_step = "error"

        return state

    def _create_scan_summary(self, nmap_result: NmapScanResult) -> str:
        """Create a human-readable summary of scan results."""
        lines = []
        lines.append(f"Scan Target: {nmap_result.target}")
        lines.append(f"Command: {nmap_result.command}")
        lines.append(f"Hosts Up: {len(nmap_result.hosts)}")
        lines.append("")

        total_open_ports = 0
        for host in nmap_result.hosts:
            lines.append(f"Host: {host.ip}" + (f" ({host.hostname})" if host.hostname else ""))
            if host.os_info:
                lines.append(f"  OS: {host.os_info}")

            open_ports = [p for p in host.ports if p.state.value == "open"]
            total_open_ports += len(open_ports)

            if open_ports:
                lines.append(f"  Open Ports ({len(open_ports)}):")
                for port in open_ports:
                    service_info = []
                    if port.service:
                        service_info.append(port.service)
                    if port.product:
                        service_info.append(port.product)
                    if port.version:
                        service_info.append(port.version)
                    service_str = " ".join(service_info) if service_info else "unknown"

                    lines.append(f"    {port.port}/{port.protocol} - {service_str}")

                    if port.scripts:
                        for script in port.scripts[:3]:  # Limit script output
                            lines.append(f"      Script: {script}")
            else:
                lines.append("  No open ports found")
            lines.append("")

        lines.append(f"Total Open Ports: {total_open_ports}")
        return "\n".join(lines)

    def _create_analysis_prompt(self, target: str, scan_summary: str, raw_output: str) -> str:
        """Create the analysis prompt for the LLM."""
        return f"""You are a senior network security analyst. Analyze the following nmap scan results for target {target} and produce a structured security assessment.

SCAN SUMMARY:
{scan_summary}

RAW NMAP OUTPUT (for reference):
{raw_output[:5000]}

Your task:
1. Identify security findings from open ports, services, and versions
2. Assess risk severity (critical/high/medium/low/info) for each finding
3. Provide actionable recommendations
4. Give an overall risk assessment

Focus on:
- Outdated/vulnerable service versions
- Unnecessary exposed services
- Information disclosure via service banners
- Default credentials or weak configurations
- Missing security controls

Return a structured ReconAnalysis with:
- scan_summary: Brief executive summary
- hosts_scanned: Number of hosts
- total_open_ports: Total count
- findings: List of Finding objects with title, description, severity, category, evidence, port, service, cve_ids, references, remediation
- risk_assessment: Overall risk narrative
- recommendations: Prioritized list of remediation actions"""

    def run(self, target: str) -> AgentState:
        """Run the complete reconnaissance workflow."""
        initial_state = AgentState(target=target)
        return self.graph.invoke(initial_state)


# Convenience function
def run_recon(target: str, model: Optional[str] = None) -> AgentState:
    """Run reconnaissance on a target."""
    agent = ReconAgent(model=model)
    return agent.run(target)