"""Web Analysis Agent - Identifies technologies, detects WAFs, and scans for web vulnerabilities."""

from typing import Optional
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from axiom.models.findings import AgentState, WebAnalysis, WebScanResult, Severity
from axiom.tools.web_tools import WhatWebScanner, Wafw00fScanner, NiktoScanner
from axiom.config.settings import settings


class WebAgent:
    """Agent that performs comprehensive web application security analysis."""

    def __init__(self, model: Optional[str] = None, temperature: float = 0.1):
        self.llm = ChatOpenAI(
            model=model or settings.default_model,
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
            temperature=temperature,
        )
        self.whatweb = WhatWebScanner()
        self.wafw00f = Wafw00fScanner()
        self.nikto = NiktoScanner()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for web analysis."""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("validate_target", self._validate_target)
        workflow.add_node("identify_tech", self._identify_tech)
        workflow.add_node("detect_waf", self._detect_waf)
        workflow.add_node("vulnerability_scan", self._vulnerability_scan)
        workflow.add_node("analyze_results", self._analyze_results)

        # Set entry point
        workflow.set_entry_point("validate_target")

        # Add edges
        workflow.add_edge("validate_target", "identify_tech")
        workflow.add_edge("identify_tech", "detect_waf")
        workflow.add_edge("detect_waf", "vulnerability_scan")
        workflow.add_edge("vulnerability_scan", "analyze_results")
        workflow.add_edge("analyze_results", END)

        return workflow.compile()

    def _validate_target(self, state: AgentState) -> AgentState:
        """Validate and normalize the target input."""
        from axiom.models.target import Target

        try:
            target_obj = Target(value=state.target)
            state.target_obj = target_obj
            state.current_step = "target_validated"
            state.web_result = WebScanResult(target=state.target)
            state.error = None
        except Exception as e:
            state.error = f"Invalid target: {str(e)}"
            state.current_step = "error"

        return state

    def _identify_tech(self, state: AgentState) -> AgentState:
        """Identify web technologies using WhatWeb."""
        if state.error: return state
        
        state.current_step = "identifying_tech"
        scan_target = state.target_obj.get_scan_target()
        
        try:
            output = self.whatweb.scan(scan_target)
            state.web_result.whatweb_output = output
        except Exception as e:
            state.web_result.errors.append(f"WhatWeb failed: {str(e)}")
            
        return state

    def _detect_waf(self, state: AgentState) -> AgentState:
        """Detect Web Application Firewall using Wafw00f."""
        if state.error: return state
        
        state.current_step = "detecting_waf"
        scan_target = state.target_obj.get_scan_target()
        
        try:
            output = self.wafw00f.scan(scan_target)
            state.web_result.wafw00f_output = output
        except Exception as e:
            state.web_result.errors.append(f"Wafw00f failed: {str(e)}")
            
        return state

    def _vulnerability_scan(self, state: AgentState) -> AgentState:
        """Perform vulnerability scan using Nikto."""
        if state.error: return state
        
        state.current_step = "vulnerability_scanning"
        scan_target = state.target_obj.get_scan_target()
        
        try:
            output = self.nikto.scan(scan_target)
            state.web_result.nikto_output = output
        except Exception as e:
            state.web_result.errors.append(f"Nikto failed: {str(e)}")
            
        return state

    def _analyze_results(self, state: AgentState) -> AgentState:
        """Analyze all web scan results using LLM."""
        if state.error: return state
        
        state.current_step = "analyzing"
        
        prompt = self._create_analysis_prompt(
            state.target,
            state.web_result.whatweb_output,
            state.web_result.wafw00f_output,
            state.web_result.nikto_output
        )

        try:
            structured_llm = self.llm.with_structured_output(WebAnalysis)
            web_analysis = structured_llm.invoke(prompt)
            
            web_analysis.target = state.target
            state.web_analysis = web_analysis
            state.current_step = "complete"
        except Exception as e:
            state.error = f"Web analysis failed: {str(e)}"
            state.current_step = "error"

        return state

    def _create_analysis_prompt(self, target: str, whatweb: str, waf: str, nikto: str) -> str:
        """Create the analysis prompt for the LLM."""
        return f"""You are a senior web security expert. Analyze the following tool outputs for target {target} and produce a structured web security assessment.

WHATWEB OUTPUT (Technology Identification):
{whatweb}

WAFW00F OUTPUT (Firewall Detection):
{waf}

NIKTO OUTPUT (Vulnerability Scan):
{nikto}

Your task:
1. Identify the full technology stack (CMS, Server, Frameworks, Libraries)
2. Confirm if a WAF is present and its type
3. Identify security findings (vulnerabilities, misconfigurations, outdated versions)
4. Assess risk severity for each finding
5. Provide prioritized recommendations

Return a structured WebAnalysis object with:
- tech_stack: List of detected technologies
- waf_detected: Boolean
- waf_name: Name of WAF if found
- findings: List of Finding objects
- summary: Executive summary
- risk_assessment: Overall web security risk narrative
- recommendations: Actionable remediation steps"""

    def run(self, target: str) -> AgentState:
        """Run the complete web analysis workflow."""
        initial_state = AgentState(target=target)
        return self.graph.invoke(initial_state)


# Convenience function
def run_web_analysis(target: str, model: Optional[str] = None) -> AgentState:
    """Run web analysis on a target."""
    agent = WebAgent(model=model)
    return agent.run(target)
