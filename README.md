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

## Overview

Axiom is a professional-grade multi-agent AI pentesting team built with a clean, scalable architecture using [LangGraph](https://langchain-ai.github.io/langgraph/). It orchestrates specialized AI agents that use real security tools to perform comprehensive security assessments and generate professional PDF/Markdown reports.

### Key Features
- **Real Tool Execution**: Unlike LLMs that hallucinate, Axiom runs actual tools (`nmap`, `nikto`, `whatweb`, `wafw00f`, `searchsploit`) and analyzes their raw outputs.
- **Clean Architecture**: Rebuilt from the ground up for modularity, robustness, and ease of expansion.
- **LangGraph Orchestration**: Uses state-of-the-art agentic workflows for precise control over the assessment lifecycle.
- **Professional Reporting**: Generates branded PDF and Markdown reports suitable for stakeholders.
- **Docker Ready**: Easy deployment with all system dependencies pre-configured.

---

## Agent Capabilities

| Agent | Focus | Tools |
|---|---|---|
| 🕵️ **Recon Agent** | Network Recon & Discovery | `nmap` (Service & Version Detection) |
| 🌐 **Web Agent** | Application Security | `whatweb`, `wafw00f`, `nikto` |
| 💥 **Exploit Agent** | Vulnerability & Exploit Research | `searchsploit` (ExploitDB integration) |
| 📝 **Report Agent** | Synthesis & Remediation | `ReportLab` (PDF/Markdown Generation) |

---

## Prerequisites

- **Python 3.11+**
- **OpenRouter API Key** (Get one at [openrouter.ai](https://openrouter.ai/))
- **Security Tools** (for local installation):
  - `nmap`, `nikto`, `whatweb`, `wafw00f`, `exploitdb`

---

## Installation

### Option 1: Docker (Recommended)
Docker is the easiest way to run Axiom as it bundles all the required Kali Linux security tools.

```bash
# 1. Clone the repository
git clone https://github.com/ezzada/axiom.git
cd axiom

# 2. Create environment file
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY

# 3. Build and Run
docker build -t axiom-suite .
docker run -p 8501:8501 --env-file .env axiom-suite
```

### Option 2: Local Installation

```bash
# 1. Install System Dependencies (Debian/Ubuntu/Kali)
sudo apt update && sudo apt install -y nmap nikto whatweb wafw00f exploitdb curl

# 2. Install Python Dependencies
pip install -r requirements.txt

# 3. Configure Environment
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

---

## Usage

### Starting the Dashboard
Run the Streamlit UI to access the main assessment dashboard:

```bash
streamlit run app.py
```

### Assessment Modes
- **Full Audit**: The automated "one-click" mode. Runs Recon -> Web Analysis -> Exploit Research -> Reporting.
- **Network Recon**: Focuses on discovering hosts, services, and open ports.
- **Web Analysis**: Deep-dive into a web application's tech stack, WAF, and vulnerabilities.
- **Exploit Research**: Cross-references discovered services against ExploitDB to find viable attack vectors.

---

## Project Structure

```
axiom/
├── agents/        # LangGraph agent definitions
├── models/        # Pydantic v2 data models & state management
├── tools/         # Robust subprocess tool wrappers
├── utils/         # Reporting and helper utilities
├── config/        # Pydantic Settings & environment config
app.py             # Streamlit Dashboard UI
Dockerfile         # Container configuration
.env.example       # Environment template
```

---

## Legal & Compliance

This tool is for **authorized penetration testing only**. Always obtain explicit written authorization before testing. The authors and contributors are not responsible for misuse or damage caused by this tool.

---

## License

MIT — see [LICENSE](LICENSE)
