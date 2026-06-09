"""
axiom_tools.py — Real Kali Linux tool wrappers for Axiom agents
Each function is a @tool that agents can actually call and get real output from.
"""

import subprocess
import shutil
from crewai.tools import tool

TIMEOUT = 120  # seconds per tool call


def _run(cmd: list[str], timeout: int = TIMEOUT) -> str:
    """Run a shell command and return stdout + stderr."""
    bin_path = shutil.which(cmd[0])
    if not bin_path:
        return f"[TOOL UNAVAILABLE] '{cmd[0]}' is not installed on this system. Install with: sudo apt install {cmd[0]}"
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout + result.stderr
        return output.strip() if output.strip() else "[No output returned]"
    except subprocess.TimeoutExpired:
        return f"[TIMEOUT] '{' '.join(cmd)}' exceeded {timeout}s limit."
    except Exception as e:
        return f"[ERROR] {str(e)}"


# ── RECON TOOLS ───────────────────────────────────────────────────────────────

@tool("WHOIS Lookup")
def whois_lookup(target: str) -> str:
    """
    Run a WHOIS lookup on a domain or IP address.
    Returns registrar info, nameservers, organization, and contact details.
    Input: domain name or IP (e.g. 'example.com' or '192.168.1.1')
    """
    return _run(["whois", target])


@tool("DNS Lookup")
def dns_lookup(target: str) -> str:
    """
    Run a comprehensive DNS lookup on a target domain.
    Returns A, MX, NS, TXT, AAAA, CNAME, and SOA records.
    Also checks for SPF, DKIM, and DMARC records.
    Input: domain name (e.g. 'example.com')
    """
    results = []
    for record_type in ["A", "MX", "NS", "TXT", "AAAA", "CNAME", "SOA"]:
        out = _run(["dig", "+short", f"-t{record_type}", target])
        if out and "[TOOL UNAVAILABLE]" not in out and "[No output" not in out:
            results.append(f"=== {record_type} ===\n{out}")
    # DMARC + SPF
    dmarc = _run(["dig", "+short", "TXT", f"_dmarc.{target}"])
    if dmarc and "[No output" not in dmarc:
        results.append(f"=== DMARC ===\n{dmarc}")
    return "\n\n".join(results) if results else "No DNS records found."


@tool("Nmap Port Scanner")
def nmap_scan(target: str) -> str:
    """
    Run an nmap scan against a target IP or hostname.
    Performs SYN scan on top 1000 ports with service/version detection.
    Also runs default NSE scripts for extra info.
    Input: IP address or hostname (e.g. '192.168.1.1' or 'example.com')
    """
    return _run([
        "nmap",
        "-sV",          # service version detection
        "-sC",          # default scripts
        "--open",       # only show open ports
        "-T4",          # aggressive timing
        "--top-ports", "1000",
        target
    ], timeout=180)


@tool("Nmap Vulnerability Scan")
def nmap_vuln_scan(target: str) -> str:
    """
    Run nmap with vulnerability detection scripts against a target.
    Uses --script vuln to check for known CVEs and vulnerabilities.
    Input: IP address or hostname
    """
    return _run([
        "nmap",
        "-sV",
        "--script", "vuln",
        "-T4",
        target
    ], timeout=300)


@tool("Subfinder Subdomain Enumeration")
def subfinder_enum(domain: str) -> str:
    """
    Enumerate subdomains of a target domain using subfinder.
    Performs passive subdomain discovery from various sources.
    Input: base domain (e.g. 'example.com')
    """
    return _run(["subfinder", "-d", domain, "-silent"], timeout=120)


@tool("Amass Subdomain Enumeration")
def amass_enum(domain: str) -> str:
    """
    Enumerate subdomains using amass (passive mode).
    Input: base domain (e.g. 'example.com')
    """
    return _run(["amass", "enum", "-passive", "-d", domain], timeout=180)


# ── WEB TOOLS ─────────────────────────────────────────────────────────────────

@tool("WhatWeb Technology Fingerprinter")
def whatweb_scan(target: str) -> str:
    """
    Fingerprint web technologies used by a target website.
    Detects CMS, frameworks, server software, plugins, analytics, and more.
    Input: URL (e.g. 'https://example.com')
    """
    return _run(["whatweb", "-a", "3", target])


@tool("Nikto Web Vulnerability Scanner")
def nikto_scan(target: str) -> str:
    """
    Run a Nikto web server vulnerability scan against a target.
    Checks for dangerous files, outdated software, misconfigurations.
    Input: URL or IP (e.g. 'https://example.com' or '192.168.1.1')
    """
    return _run(["nikto", "-h", target, "-nointeractive"], timeout=300)


@tool("HTTP Header Analyzer")
def http_headers(target: str) -> str:
    """
    Retrieve and analyze HTTP response headers from a target URL.
    Checks for security headers: CSP, HSTS, X-Frame-Options, Referrer-Policy,
    Permissions-Policy, X-Content-Type-Options, Set-Cookie flags.
    Input: URL (e.g. 'https://example.com')
    """
    raw = _run([
        "curl", "-s", "-I",
        "--max-time", "15",
        "--location",
        "-A", "Mozilla/5.0 (compatible; Axiom-Scanner/1.0)",
        target
    ])

    # Analyze security headers
    headers_lower = raw.lower()
    analysis = ["\n=== SECURITY HEADER ANALYSIS ==="]

    checks = [
        ("content-security-policy", "CSP"),
        ("strict-transport-security", "HSTS"),
        ("x-frame-options", "X-Frame-Options"),
        ("x-content-type-options", "X-Content-Type-Options"),
        ("referrer-policy", "Referrer-Policy"),
        ("permissions-policy", "Permissions-Policy"),
    ]
    for header, name in checks:
        status = "✅ PRESENT" if header in headers_lower else "❌ MISSING"
        analysis.append(f"{status}: {name}")

    if "httponly" in headers_lower:
        analysis.append("✅ PRESENT: HttpOnly cookie flag")
    else:
        analysis.append("❌ MISSING: HttpOnly cookie flag")

    if "samesite" in headers_lower:
        analysis.append("✅ PRESENT: SameSite cookie flag")
    else:
        analysis.append("❌ MISSING: SameSite cookie flag")

    return raw + "\n".join(analysis)


@tool("WAF Detector")
def wafw00f_scan(target: str) -> str:
    """
    Detect Web Application Firewalls (WAF) protecting a target website.
    Input: URL (e.g. 'https://example.com')
    """
    return _run(["wafw00f", target])


@tool("SSL/TLS Scanner")
def ssl_scan(target: str) -> str:
    """
    Analyze SSL/TLS configuration of a target.
    Detects weak ciphers, protocol versions, certificate issues.
    Input: hostname or IP (e.g. 'example.com' or '192.168.1.1')
    """
    out = _run(["sslscan", "--no-colour", target])
    if "[TOOL UNAVAILABLE]" in out:
        # Fallback to nmap ssl scripts
        out = _run([
            "nmap", "--script",
            "ssl-enum-ciphers,ssl-cert,ssl-heartbleed,ssl-poodle",
            "-p", "443,8443",
            target
        ])
    return out


@tool("Gobuster Directory Brute Force")
def gobuster_scan(target: str) -> str:
    """
    Brute-force hidden directories and files on a web server.
    Uses a common wordlist to find exposed endpoints, admin panels, backup files.
    Input: URL (e.g. 'https://example.com')
    """
    wordlist = "/usr/share/wordlists/dirb/common.txt"
    import os
    if not os.path.exists(wordlist):
        wordlist = "/usr/share/wordlists/dirbuster/directory-list-2.3-small.txt"
    if not os.path.exists(wordlist):
        return "[ERROR] No wordlist found. Install: sudo apt install wordlists && gunzip /usr/share/wordlists/rockyou.txt.gz"

    return _run([
        "gobuster", "dir",
        "-u", target,
        "-w", wordlist,
        "-q",          # quiet mode
        "-t", "20",    # 20 threads
        "--timeout", "10s",
        "-b", "404,403",  # ignore these status codes
    ], timeout=300)


# ── NETWORK TOOLS ─────────────────────────────────────────────────────────────

@tool("SearchSploit CVE Lookup")
def searchsploit(query: str) -> str:
    """
    Search ExploitDB for known exploits matching a service, software, or CVE.
    Input: search query (e.g. 'Apache 2.4.49' or 'WordPress 5.8' or 'CVE-2021-44228')
    """
    return _run(["searchsploit", "--colour", query])


@tool("Ping Sweep")
def ping_sweep(cidr: str) -> str:
    """
    Perform a ping sweep to discover live hosts on a network range.
    Input: CIDR range (e.g. '192.168.1.0/24') or single IP
    """
    return _run([
        "nmap", "-sn",   # ping scan only
        "-T4",
        cidr
    ], timeout=120)


@tool("SMB Scanner")
def smb_scan(target: str) -> str:
    """
    Scan SMB service for vulnerabilities, null sessions, and share enumeration.
    Checks for EternalBlue (MS17-010), SMBv1, and unauthenticated shares.
    Input: IP address or hostname
    """
    return _run([
        "nmap", "-p", "445,139",
        "--script",
        "smb-vuln-ms17-010,smb-vuln-ms08-067,smb-security-mode,smb-enum-shares",
        target
    ], timeout=120)


@tool("Traceroute")
def traceroute(target: str) -> str:
    """
    Trace the network path to a target and identify network hops.
    Input: IP address or hostname
    """
    out = _run(["traceroute", "-m", "20", target], timeout=60)
    if "[TOOL UNAVAILABLE]" in out:
        out = _run(["nmap", "--traceroute", "-sn", target], timeout=60)
    return out


# ── OSINT TOOLS ───────────────────────────────────────────────────────────────

@tool("TheHarvester OSINT")
def theharvester(domain: str) -> str:
    """
    Gather emails, subdomains, IPs, and URLs using theHarvester.
    Uses multiple data sources: Google, Bing, DNSdumpster, etc.
    Input: domain name (e.g. 'example.com')
    """
    return _run([
        "theHarvester",
        "-d", domain,
        "-b", "google,bing,duckduckgo,dnsdumpster",
        "-l", "200"
    ], timeout=120)


@tool("Certificate Transparency Lookup")
def cert_lookup(domain: str) -> str:
    """
    Search certificate transparency logs for subdomains of a target domain.
    Uses crt.sh to find all certificates ever issued for a domain.
    Input: domain name (e.g. 'example.com')
    """
    return _run([
        "curl", "-s",
        f"https://crt.sh/?q=%.{domain}&output=json",
        "--max-time", "20"
    ], timeout=30)
