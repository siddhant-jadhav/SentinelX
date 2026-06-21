# ── Frontend Dockerfile ───────────────────────────────────────────
# SentinelX Streamlit Frontend
# Build:  docker build -t sentinelx-frontend -f frontend/Dockerfile .
# Run:    docker run -p 8503:8503 sentinelx-frontend

FROM python:3.12-slim AS base

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# ── Install system deps ──────────────────────────────────────────
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# ── Install Python deps ─────────────────────────────────────────
RUN pip install --no-cache-dir \
    streamlit \
    plotly \
    httpx

# ── Copy frontend source ────────────────────────────────────────
COPY frontend/ ./frontend/
COPY .streamlit/ ./.streamlit/

# ── Default environment ──────────────────────────────────────────
ENV BACKEND_URL="http://backend:8003"

# ── Expose port ──────────────────────────────────────────────────
EXPOSE 8503

# ── Health check ─────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8503/_stcore/health || exit 1

# ── Start Streamlit ──────────────────────────────────────────────
CMD ["streamlit", "run", "frontend/app.py", \
     "--server.port=8503", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
