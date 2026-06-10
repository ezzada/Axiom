# Use an official Python runtime as a parent image
FROM python:3.11-slim

# ── Environment ───────────────────────────────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
# Ensure tools installed to /usr/local/bin are always on PATH
ENV PATH="/usr/local/bin:$PATH"

# ── Working directory ─────────────────────────────────────────────────────────
WORKDIR /app

# ── System dependencies ───────────────────────────────────────────────────────
# ruby  → required by whatweb
# perl  → required by nikto
# git   → required to clone nikto & exploitdb
# curl  → healthcheck + general use
# gcc / python3-dev → compile any C-extension Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap \
    whatweb \
    gcc \
    python3-dev \
    ruby \
    git \
    perl \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Nikto (no Debian package in trixie) ──────────────────────────────────────
RUN git clone --depth 1 --single-branch \
    https://github.com/sullo/nikto.git /opt/nikto \
    && chmod +x /opt/nikto/program/nikto.pl \
    && ln -s /opt/nikto/program/nikto.pl /usr/local/bin/nikto \
    # remove git history to keep the image lean
    && rm -rf /opt/nikto/.git

# ── ExploitDB / searchsploit (not on PyPI) ────────────────────────────────────
RUN git clone --depth 1 --single-branch \
    https://gitlab.com/exploit-database/exploitdb.git /opt/exploitdb \
    && chmod +x /opt/exploitdb/searchsploit \
    && ln -s /opt/exploitdb/searchsploit /usr/local/bin/searchsploit \
    # write rc file so searchsploit knows where its database lives
    && printf '[Tools]\nEDB=/opt/exploitdb\n\n[exploitdb]\npath=/opt/exploitdb\n' \
       > /root/.searchsploit_rc \
    && rm -rf /opt/exploitdb/.git

# ── Python dependencies ───────────────────────────────────────────────────────
# Copy requirements first to leverage Docker layer cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt wafw00f

# ── Application source ────────────────────────────────────────────────────────
COPY . .

# ── Network ───────────────────────────────────────────────────────────────────
EXPOSE 8501

# ── Healthcheck ───────────────────────────────────────────────────────────────
# --start-period gives Streamlit time to boot before checks begin
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# ── Entrypoint ────────────────────────────────────────────────────────────────
ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.port=8501", \
            "--server.address=0.0.0.0"]
