# AXIOM — Professional AI Pentesting Suite

```
 █████╗ ██╗  ██╗██╗ ██████╗ ███╗   ███╗
██╔══██╗╚██╗██╔╝██║██╔═══██╗████╗ ████║
███████║ ╚███╔╝ ██║██║   ██║██╔████╔██║
██╔══██║ ██╔██╗ ██║██║   ██║██║╚██╔╝██║
██║  ██║██╔╝ ██╗██║╚██████╔╝██║ ╚═╝ ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚═╝
```

> ⚠️ **For authorized security testing only. Unauthorized testing is illegal.**

---

## What is Axiom?

Axiom is a multi-agent AI pentesting team built with [CrewAI](https://crewai.com). It gives **5 specialized AI agents** access to real Kali Linux security tools, orchestrates them in sequence, and produces professional pentest reports in PDF and Markdown.

Unlike AI tools that hallucinate findings, Axiom agents **actually run real tools** (`nmap`, `nikto`, `whatweb`, `searchsploit`, etc.) and analyze real output.

---

## The Team

| Agent | Role | Tools |
|---|---|---|
| 🕵️ Recon Specialist | OSINT, attack surface mapping | `whois`, `dig`, `nmap`, `subfinder`, `theHarvester`, `crt.sh` |
| 🌐 Web Analyst | OWASP Top 10, API security | `whatweb`, `nikto`, `curl`, `wafw00f`, `sslscan`, `gobuster` |
| 🔌 Network Pentester | Ports, CVEs, lateral movement | `nmap --script vuln`, `smb-vuln`, `searchsploit`, `traceroute` |
| 💥 Exploit Specialist | Attack chains, CVE analysis | `searchsploit` |
| 📝 Report Writer | Professional PDF + Markdown report | ReportLab |

---

## Installation

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/axiom.git
cd axiom

# 2. Install Python deps
pip install -r requirements.txt

# 3. Install Kali tools
sudo apt install -y nmap nikto whatweb wafw00f sslscan gobuster \
                    subfinder amass theharvester exploitdb wordlists

# 4. Set your OpenRouter API key (free at openrouter.ai)
export OPENROUTER_API_KEY=sk-or-v1-...
```

## Usage

```bash
# Streamlit UI (recommended)
streamlit run axiom_ui.py
# Opens at http://localhost:8501

# CLI
python axiom.py
```

---

## How It Works

```
Streamlit UI
    │
    ▼
CrewAI Orchestrator
    ├─▶ 🕵️ Recon Agent    ──▶ whois, dig, nmap, subfinder, theHarvester
    ├─▶ 🌐 Web Agent       ──▶ whatweb, nikto, curl, wafw00f, gobuster
    ├─▶ 🔌 Network Agent   ──▶ nmap vuln scripts, searchsploit, smb-scan
    ├─▶ 💥 Exploit Agent   ──▶ searchsploit (CVE matching on real findings)
    └─▶ 📝 Report Agent    ──▶ PDF + Markdown report
              │
              ▼
        OpenRouter API (free LLM models, auto-fallback)
```

---

## Project Structure

```
axiom/
├── axiom_ui.py        # Streamlit web UI
├── axiom_tools.py     # Real Kali Linux tool wrappers (16 tools)
├── axiom.py           # CLI entry point
├── requirements.txt   # Python dependencies
├── .gitignore
└── README.md
```

---

## LLM Models (Free, Auto-Fallback)

Axiom automatically switches models if one is rate-limited:

1. `openai/gpt-oss-120b:free`
2. `nvidia/nemotron-3-ultra-550b-a55b:free`
3. `nvidia/nemotron-3-super-120b-a12b:free`
4. `openai/gpt-oss-20b:free`
5. `openrouter/owl-alpha:free`
6. `openrouter/free` ← ultimate fallback

---

## Legal

For **authorized penetration testing only**. Always obtain explicit written authorization before testing. The authors are not responsible for misuse.

---

## License

MIT — see [LICENSE](LICENSE)
