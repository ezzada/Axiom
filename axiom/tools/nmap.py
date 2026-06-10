"""Nmap tool wrapper for executing nmap scans via subprocess."""

import subprocess
import shutil
import xml.etree.ElementTree as ET
from typing import List, Optional
from datetime import datetime

from axiom.models.findings import NmapScanResult, HostInfo, PortInfo, PortState
from axiom.config.settings import settings


class NmapScanner:
    """Wrapper for nmap port scanner."""

    def __init__(self, timeout: Optional[int] = None):
        self.timeout = timeout or settings.nmap_timeout
        self._verify_nmap()

    def _verify_nmap(self) -> None:
        """Verify nmap is available on the system."""
        if not shutil.which("nmap"):
            raise RuntimeError(
                "nmap not found. Install with: sudo apt install nmap"
            )

    def _build_command(self, target: str, scan_type: str = "default") -> List[str]:
        """Build nmap command based on scan type."""
        base_cmd = [
            "nmap",
            "-sV",           # Service version detection
            "-sC",           # Default scripts
            "--open",        # Show only open ports
            "-T4",           # Aggressive timing
            "--top-ports", "1000",  # Top 1000 ports
            "-oX", "-",      # XML output to stdout
            target
        ]

        if scan_type == "quick":
            base_cmd = [
                "nmap",
                "-F",        # Fast scan (top 100 ports)
                "-T4",
                "--open",
                "-oX", "-",
                target
            ]
        elif scan_type == "full":
            base_cmd = [
                "nmap",
                "-sV",
                "-sC",
                "-p-",       # All ports
                "-T4",
                "--open",
                "-oX", "-",
                target
            ]
        elif scan_type == "vuln":
            base_cmd = [
                "nmap",
                "-sV",
                "--script", "vuln",
                "-T4",
                "--open",
                "-oX", "-",
                target
            ]

        return base_cmd

    def scan(self, target: str, scan_type: str = "default") -> NmapScanResult:
        """
        Run nmap scan against target.

        Args:
            target: Target IP, hostname, or CIDR
            scan_type: One of "quick", "default", "full", "vuln"

        Returns:
            NmapScanResult with parsed scan data
        """
        cmd = self._build_command(target, scan_type)
        command_str = " ".join(cmd)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            raw_output = result.stdout + result.stderr

            if result.returncode not in (0, 1):  # nmap returns 1 if no hosts up
                return NmapScanResult(
                    target=target,
                    command=command_str,
                    raw_output=raw_output,
                    scan_stats={"error": f"Nmap exited with code {result.returncode}"}
                )

            # Parse XML output
            hosts = self._parse_xml_output(raw_output)

            return NmapScanResult(
                target=target,
                command=command_str,
                raw_output=raw_output,
                hosts=hosts,
                scan_stats=self._extract_stats(raw_output)
            )

        except subprocess.TimeoutExpired:
            return NmapScanResult(
                target=target,
                command=command_str,
                raw_output="",
                scan_stats={"error": f"Scan timed out after {self.timeout}s"}
            )
        except Exception as e:
            return NmapScanResult(
                target=target,
                command=command_str,
                raw_output="",
                scan_stats={"error": str(e)}
            )

    def _parse_xml_output(self, xml_output: str) -> List[HostInfo]:
        """Parse nmap XML output into structured data."""
        hosts = []

        try:
            root = ET.fromstring(xml_output)
        except ET.ParseError:
            return hosts

        for host_elem in root.findall("host"):
            # Get host status
            status_elem = host_elem.find("status")
            if status_elem is None or status_elem.get("state") != "up":
                continue

            # Get IP address
            address_elem = host_elem.find("address[@addrtype='ipv4']")
            ip = address_elem.get("addr") if address_elem is not None else "unknown"

            # Get hostname
            hostname = None
            hostnames_elem = host_elem.find("hostnames")
            if hostnames_elem is not None:
                hostname_elem = hostnames_elem.find("hostname")
                if hostname_elem is not None:
                    hostname = hostname_elem.get("name")

            # Get MAC address
            mac_address = None
            mac_elem = host_elem.find("address[@addrtype='mac']")
            if mac_elem is not None:
                mac_address = mac_elem.get("addr")

            # Get OS info
            os_info = None
            os_elem = host_elem.find("os")
            if os_elem is not None:
                osmatch = os_elem.find("osmatch")
                if osmatch is not None:
                    os_info = osmatch.get("name")

            # Get ports
            ports = []
            ports_elem = host_elem.find("ports")
            if ports_elem is not None:
                for port_elem in ports_elem.findall("port"):
                    port_id = int(port_elem.get("portid", 0))
                    protocol = port_elem.get("protocol", "tcp")

                    state_elem = port_elem.find("state")
                    state_str = state_elem.get("state", "unknown") if state_elem is not None else "unknown"
                    try:
                        state = PortState(state_str)
                    except ValueError:
                        state = PortState.OPEN  # default

                    service_elem = port_elem.find("service")
                    service = None
                    version = None
                    product = None
                    extrainfo = None
                    cpe_list = []

                    if service_elem is not None:
                        service = service_elem.get("name")
                        version = service_elem.get("version")
                        product = service_elem.get("product")
                        extrainfo = service_elem.get("extrainfo")

                        for cpe_elem in service_elem.findall("cpe"):
                            cpe_list.append(cpe_elem.text or "")

                    # Get script output
                    scripts = []
                    for script_elem in port_elem.findall("script"):
                        script_output = script_elem.get("output", "")
                        script_id = script_elem.get("id", "")
                        if script_output:
                            scripts.append(f"{script_id}: {script_output}")

                    ports.append(PortInfo(
                        port=port_id,
                        protocol=protocol,
                        state=state,
                        service=service,
                        version=version,
                        product=product,
                        extrainfo=extrainfo,
                        cpe=cpe_list,
                        scripts=scripts
                    ))

            hosts.append(HostInfo(
                ip=ip,
                hostname=hostname,
                status="up",
                ports=ports,
                os_info=os_info,
                mac_address=mac_address
            ))

        return hosts

    def _extract_stats(self, xml_output: str) -> dict:
        """Extract scan statistics from nmap output."""
        stats = {}
        try:
            root = ET.fromstring(xml_output)
            runstats = root.find("runstats")
            if runstats is not None:
                finished = runstats.find("finished")
                if finished is not None:
                    stats["elapsed"] = finished.get("elapsed")
                    stats["exit"] = finished.get("exit")
                    stats["summary"] = finished.get("summary")

                hosts = runstats.find("hosts")
                if hosts is not None:
                    stats["hosts_up"] = hosts.get("up")
                    stats["hosts_down"] = hosts.get("down")
                    stats["hosts_total"] = hosts.get("total")
        except ET.ParseError:
            pass
        return stats


# Convenience function for simple usage
def run_nmap_scan(target: str, scan_type: str = "default", timeout: Optional[int] = None) -> NmapScanResult:
    """Run a quick nmap scan and return results."""
    scanner = NmapScanner(timeout=timeout)
    return scanner.scan(target, scan_type)