# ── Backend Dockerfile ────────────────────────────────────────────
# SentinelX FastAPI Backend
# Build:  docker build -t sentinelx-backend -f backend/Dockerfile .
# Run:    docker run -p 8003:8003 sentinelx-backend

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
COPY requirements.txt .
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    sqlalchemy \
    httpx \
    python-jose \
    passlib \
    bcrypt \
    python-dotenv \
    pydantic \
    python-multipart

# ── Copy backend source ─────────────────────────────────────────
COPY backend/ ./backend/

# ── Default environment ──────────────────────────────────────────
ENV DATABASE_URL="sqlite:////data/sentinelx.db" \
    JWT_SECRET_KEY="sentinelx-change-me-in-production" \
    OTX_API_KEY="" \
    ADMIN_PASSWORD="SentinelX@2024" \
    BACKEND_URL="http://localhost:8003"

# ── Data volume mount point ──────────────────────────────────────
RUN mkdir -p /data
VOLUME /data

# ── Expose port ──────────────────────────────────────────────────
EXPOSE 8003

# ── Health check ─────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# ── Entrypoint: seed DB then start server ────────────────────────
CMD ["sh", "-c", "python -c 'from backend.seed import seed_database; seed_database()' && uvicorn backend.main:app --host 0.0.0.0 --port 8003"]
