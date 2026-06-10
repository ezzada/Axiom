# GEMINI.md

This file provides guidance to Gemini CLI when working with code in this repository.

## Project Overview

**AXIOM** is a professional AI-powered penetration testing suite built with **CrewAI**. It orchestrates 5 specialized AI agents that use real Kali Linux security tools to perform comprehensive security assessments and generate professional PDF/Markdown reports.

**Key Architecture:**
- **5 AI Agents** (Recon, Web, Network, Exploit, Report) with specific roles and toolsets
- **16 real tool wrappers** in `axiom_tools.py` that execute actual Kali tools (nmap, nikto, whatweb, searchsploit, etc.)
- **Two interfaces**: CLI (`axiom.py`) and Streamlit Web UI (`axiom_ui.py`)
- **OpenRouter API** for free LLM models with automatic fallback chain
- **ReportLab** for professional PDF report generation

## Commands

### Development & Testing
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run test suite (validates tool registration and input sanitization)
python test_tools.py

# Run CLI mode
python axiom.py

# Run Streamlit UI (recommended)
streamlit run axiom_ui.py
```

### Required System Dependencies (Kali Linux Tools)
```bash
# Install on Debian/Ubuntu/Kali
sudo apt install -y nmap nikto whatweb wafw00f sslscan gobuster \
                    subfinder amass theharvester exploitdb wordlists \
                    dnsutils traceroute
```

### Environment Setup
```bash
# Required: OpenRouter API key (free at openrouter.ai)
export OPENROUTER_API_KEY=sk-or-v1-...
```

## Code Architecture

### Core Files

| File | Purpose |
|------|---------|
| `axiom.py` | CLI entry point - defines agents, tasks, and orchestration logic |
| `axiom_tools.py` | 16 `@tool` decorated functions wrapping real Kali security tools |
| `axiom_ui.py` | Streamlit web interface with real-time agent status and log streaming |
| `test_tools.py` | Validates tool registration and input sanitization |
| `requirements.txt` | Python dependencies |

### Agent System (in `axiom.py`)

**5 CrewAI Agents** with distinct roles and tool access:

1. **Recon Specialist** — OSINT, attack surface mapping
   - Tools: `whois_lookup`, `dns_lookup`, `nmap_scan`, `subfinder_enum`, `theharvester`, `cert_lookup`, `ping_sweep`

2. **Web Analyst** — OWASP Top 10, API security
   - Tools: `whatweb_scan`, `nikto_scan`, `http_headers`, `wafw00f_scan`, `ssl_scan`, `gobuster_scan`

3. **Network Pentester** — Ports, CVEs, lateral movement
   - Tools: `nmap_scan`, `nmap_vuln_scan`, `smb_scan`, `searchsploit`, `ping_sweep`, `traceroute`

4. **Exploit Specialist** — Attack chains, CVE analysis
   - Tools: `searchsploit`

5. **Report Writer** — Professional PDF + Markdown report
   - No tools (synthesizes findings)

**Task Flow:** Sequential (Recon → Web → Network → Exploit → Report) with context passing between agents.

### Tool Wrappers (in `axiom_tools.py`)

All 16 tools follow the same pattern:
- Decorated with `@tool("Display Name")` for CrewAI
- Use `_run(cmd_list, timeout)` for safe subprocess execution (no shell=True)
- Input validation via `_is_safe_input()` regex allowlist
- Return tool output as string or error messages

**Tool Categories:**
- **Recon (7)**: whois, dig, nmap, subfinder, amass, theHarvester, crt.sh
- **Web (6)**: whatweb, nikto, curl headers, wafw00f, sslscan, gobuster
- **Network (3)**: searchsploit, ping sweep, SMB scan
- **Utility (2)**: traceroute, certificate lookup

### LLM Configuration

**Model Fallback Chain** (in `FREE_MODELS` list):
1. `openrouter/openai/gpt-oss-120b:free`
2. `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free`
3. `openrouter/nvidia/nemotron-3-super-120b-a12b:free`
4. `openrouter/openai/gpt-oss-20b:free`
5. `openrouter/openrouter/owl-alpha:free`
6. `openrouter/openrouter/free` (ultimate fallback)

Configured via `litellm` with OpenRouter base URL.

### PDF Generation

Both `axiom.py` and `axiom_ui.py` contain `generate_pdf()` using **ReportLab**:
- Professional styling with custom colors (#e63946 accent)
- Cover page with target info and classification
- Markdown-to-PDF parsing (headers, code blocks, tables, bullet points)
- Legal disclaimer included

## Key Patterns & Conventions

### Security
- All subprocess calls use **list arguments** (no `shell=True`)
- `_is_safe_input()` validates arguments against regex `^[a-zA-Z0-9\.\-\_\:\/%\?\=\&\+]+$`
- Tools check binary availability with `shutil.which()` before execution
- Timeout protection on all tool calls (default 120s, up to 300s for heavy scans)

### Error Handling
- Tools return error strings (not exceptions) so agents can continue
- Common error prefixes: `[TOOL UNAVAILABLE]`, `[TIMEOUT]`, `[ERROR]`, `[SECURITY ERROR]`
- Graceful fallbacks (e.g., `sslscan` → nmap SSL scripts if unavailable)

### Streaming UI (axiom_ui.py)
- Background thread runs CrewAI crew
- `queue.Queue` passes log messages to main Streamlit thread
- Agent state updates (`idle`/`running`/`done`) drive progress bar
- Real-time log rendering with color-coded levels (info/success/warn/error)

## Development Notes

### Adding a New Tool
1. Add function in `axiom_tools.py` with `@tool` decorator
2. Import and add to relevant agent's `tools` list in `axiom.py` and `axiom_ui.py`
3. Run `python test_tools.py` to verify registration

### Modifying Agent Behavior
- Edit task descriptions in `build_tasks()` function in `axiom.py`
- Adjust agent `role`, `goal`, `backstory` in agent definitions
- Prompt engineering is the primary way to change agent output

### Testing Changes
```bash
# Quick validation
python test_tools.py

# Full CLI test (requires API key and Kali tools)
OPENROUTER_API_KEY=... python axiom.py

# UI test
OPENROUTER_API_KEY=... streamlit run axiom_ui.py
```

## Legal & Compliance

- **Authorized use only** — enforced via authorization checkbox in UI and confirmation prompt in CLI
- MIT License (see LICENSE)
- Legal disclaimer in DISCLAIMER.md and embedded in generated reports
- References CFAA, UK Computer Misuse Act, EU Directive 2013/40/EU

## Common Issues

| Issue | Solution |
|-------|----------|
| `[TOOL UNAVAILABLE]` errors | Install missing Kali tools via apt |
| Rate limiting on free models | Automatic fallback chain handles this |
| Timeout on heavy scans | Increase `TIMEOUT` in `axiom_tools.py` or per-tool timeout |
| PDF generation fails | Ensure ReportLab is installed (`pip install reportlab`) |
| Streamlit UI not updating | Check thread/queue communication in `run_axiom()` |
