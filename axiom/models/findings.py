"""Data models for structured scan findings and analysis results."""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal, TYPE_CHECKING
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from axiom.models.target import Target


class Severity(str, Enum):
    """Finding severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class PortState(str, Enum):
    """Nmap port states."""
    OPEN = "open"
    CLOSED = "closed"
    FILTERED = "filtered"
    UNFILTERED = "unfiltered"
    OPEN_FILTERED = "open|filtered"
    CLOSED_FILTERED = "closed|filtered"


class PortInfo(BaseModel):
    """Information about a scanned port."""
    port: int
    protocol: str = "tcp"
    state: PortState
    service: Optional[str] = None
    version: Optional[str] = None
    product: Optional[str] = None
    extrainfo: Optional[str] = None
    cpe: List[str] = Field(default_factory=list)
    scripts: List[str] = Field(default_factory=list)


class HostInfo(BaseModel):
    """Information about a scanned host."""
    ip: str
    hostname: Optional[str] = None
    status: str = "up"
    ports: List[PortInfo] = Field(default_factory=list)
    os_info: Optional[str] = None
    mac_address: Optional[str] = None


class NmapScanResult(BaseModel):
    """Complete nmap scan result."""
    target: str
    scan_time: datetime = Field(default_factory=datetime.now)
    command: str
    raw_output: str
    hosts: List[HostInfo] = Field(default_factory=list)
    scan_stats: dict = Field(default_factory=dict)


class Finding(BaseModel):
    """A security finding from analysis."""
    title: str
    description: str
    severity: Severity
    category: str
    evidence: str
    port: Optional[int] = None
    service: Optional[str] = None
    cve_ids: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    remediation: Optional[str] = None


class ReconAnalysis(BaseModel):
    """Structured analysis output from the Recon agent."""
    target: str
    scan_summary: str
    hosts_scanned: int
    total_open_ports: int
    findings: List[Finding] = Field(default_factory=list)
    risk_assessment: str = ""
    recommendations: List[str] = Field(default_factory=list)
    analyzed_at: datetime = Field(default_factory=datetime.now)


class WebScanResult(BaseModel):
    """Result of various web scanning tools."""
    target: str
    scan_time: datetime = Field(default_factory=datetime.now)
    whatweb_output: Optional[str] = None
    wafw00f_output: Optional[str] = None
    nikto_output: Optional[str] = None
    errors: List[str] = Field(default_factory=list)


class WebAnalysis(BaseModel):
    """Structured analysis output from the Web agent."""
    target: str
    tech_stack: List[str] = Field(default_factory=list, description="List of detected technologies (CMS, Server, Frameworks)")
    waf_detected: bool = False
    waf_name: Optional[str] = None
    findings: List[Finding] = Field(default_factory=list)
    summary: str = ""
    risk_assessment: str = ""
    recommendations: List[str] = Field(default_factory=list)
    analyzed_at: datetime = Field(default_factory=datetime.now)


class ExploitResult(BaseModel):
    """Result of exploit research (searchsploit)."""
    service: str
    version: Optional[str] = None
    search_output: str
    exploits_found: int = 0


class ExploitAnalysis(BaseModel):
    """Structured analysis output from the Exploit agent."""
    target: str
    vulnerabilities_analyzed: int
    potential_exploits: List[Finding] = Field(default_factory=list)
    attack_vectors: List[str] = Field(default_factory=list)
    risk_assessment: str = ""
    recommendations: List[str] = Field(default_factory=list)
    analyzed_at: datetime = Field(default_factory=datetime.now)


class ReportAnalysis(BaseModel):
    """Synthesized security report analysis."""
    target: str
    executive_summary: str
    key_findings_summary: str
    total_vulnerabilities: int
    severity_counts: dict = Field(default_factory=dict)
    technical_details: str
    remediation_roadmap: List[str] = Field(default_factory=list)
    legal_disclaimer: str = "This report is for authorized use only. The findings are based on point-in-time testing."
    generated_at: datetime = Field(default_factory=datetime.now)


class AgentState(BaseModel):
    """State passed between agents in the graph."""
    target: str
    target_obj: Optional["Target"] = None
    # Recon fields
    nmap_result: Optional[NmapScanResult] = None
    analysis: Optional[ReconAnalysis] = None
    # Web fields
    web_result: Optional[WebScanResult] = None
    web_analysis: Optional[WebAnalysis] = None
    # Exploit fields
    exploit_results: List[ExploitResult] = Field(default_factory=list)
    exploit_analysis: Optional[ExploitAnalysis] = None
    # Report fields
    report_analysis: Optional[ReportAnalysis] = None
    
    error: Optional[str] = None
    current_step: str = "initialized"


# Forward reference resolution
from axiom.models.target import Target
AgentState.model_rebuild()