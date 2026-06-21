# 🐳 SentinelX — Docker Deployment Guide

Complete guide for deploying SentinelX using Docker and Docker Compose.

---

## 📋 Prerequisites

| Tool             | Minimum Version | Check Command           |
|------------------|-----------------|-------------------------|
| Docker           | 20.10+          | `docker --version`      |
| Docker Compose   | 2.0+            | `docker compose version`|

---

## 🚀 Quick Start

### 1. Clone & Configure

```bash
cd SenitalX
cp .env.example .env
```

Edit `.env` with your values:

```bash
# Required for live OTX threat feeds
OTX_API_KEY=your_otx_api_key_here

# IMPORTANT: Change in production!
JWT_SECRET_KEY=your-strong-random-secret

# Admin credentials (applied on first DB seed)
ADMIN_PASSWORD=YourSecurePassword123
```

### 2. Build & Launch

```bash
docker compose up --build
```

### 3. Access

| Service     | URL                          |
|-------------|------------------------------|
| Frontend    | http://localhost:8503         |
| Backend API | http://localhost:8003         |
| API Docs    | http://localhost:8003/docs    |
| Health Check| http://localhost:8003/health  |

### 4. Login

| Role    | Username  | Password (default)   |
|---------|-----------|----------------------|
| Admin   | admin     | SentinelX@2024       |
| Analyst | analyst   | analyst123           |

> **Note:** Passwords are configurable via `ADMIN_PASSWORD` and `ANALYST_PASSWORD` env vars. They are only applied during the **first** database seed.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   Docker Compose                         │
│                                                          │
│  ┌──────────────┐   HTTP/REST    ┌──────────────────┐   │
│  │   Frontend   │ ─────────────► │     Backend      │   │
│  │  (Streamlit) │                │    (FastAPI)     │   │
│  │  Port 8503   │                │    Port 8003     │   │
│  └──────────────┘                └────────┬─────────┘   │
│                                           │              │
│                                  ┌────────▼─────────┐   │
│                                  │  SQLite Volume   │   │
│                                  │   /data/         │   │
│                                  └──────────────────┘   │
│                                           │              │
│                                  ┌────────▼─────────┐   │
│                                  │  AlienVault OTX  │   │
│                                  │  (External API)  │   │
│                                  └──────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

### Services

| Service    | Container              | Port | Description                     |
|------------|------------------------|------|---------------------------------|
| `backend`  | `sentinelx-backend`    | 8003 | FastAPI REST API + SQLite       |
| `frontend` | `sentinelx-frontend`   | 8503 | Streamlit web UI                |

### Networking

- Both services run on the `sentinelx-net` bridge network.
- The frontend reaches the backend at `http://backend:8003` (Docker DNS).
- The frontend **waits** for the backend's health check before starting.

---

## ⚙️ Environment Variables

### Required

| Variable          | Description                          | Default                     |
|-------------------|--------------------------------------|-----------------------------|
| `JWT_SECRET_KEY`  | JWT signing secret                   | `sentinelx-change-me-...`  |

### Recommended

| Variable          | Description                          | Default                     |
|-------------------|--------------------------------------|-----------------------------|
| `OTX_API_KEY`     | AlienVault OTX API key               | *(empty — demo mode)*      |
| `ADMIN_PASSWORD`  | Admin account password (first seed)  | `SentinelX@2024`           |

### Optional

| Variable             | Description                     | Default                    |
|----------------------|---------------------------------|----------------------------|
| `ADMIN_USERNAME`     | Admin username                  | `admin`                    |
| `ADMIN_EMAIL`        | Admin email                     | `admin@sentinelx.local`    |
| `ANALYST_PASSWORD`   | Analyst account password        | `analyst123`               |
| `ANALYST_USERNAME`   | Analyst username                | `analyst`                  |
| `BACKEND_PORT`       | Host port for backend           | `8003`                     |
| `FRONTEND_PORT`      | Host port for frontend          | `8503`                     |
| `DEBUG`              | Enable debug logging            | `false`                    |

---

## 📦 Common Operations

### Start in Background

```bash
docker compose up -d --build
```

### View Logs

```bash
# All services
docker compose logs -f

# Backend only
docker compose logs backend -f

# Frontend only
docker compose logs frontend -f
```

### Stop Services

```bash
docker compose down
```

### Stop & Remove Volumes (⚠️ deletes database)

```bash
docker compose down -v
```

### Rebuild After Code Changes

```bash
docker compose up --build
```

### Check Health

```bash
# Container status
docker compose ps

# Backend health
curl http://localhost:8003/health

# Frontend health
curl http://localhost:8503/_stcore/health
```

---

## 💾 Data Persistence

- SQLite database is stored in the **`sentinelx-data`** Docker volume.
- The volume is mounted at `/data/sentinelx.db` inside the backend container.
- Data persists across `docker compose down` and `docker compose up`.
- To **reset the database**: `docker compose down -v` (removes the volume).

### Backup Database

```bash
# Copy database from Docker volume to host
docker cp sentinelx-backend:/data/sentinelx.db ./backup_sentinelx.db
```

### Restore Database

```bash
# Copy database from host into Docker volume
docker cp ./backup_sentinelx.db sentinelx-backend:/data/sentinelx.db
docker compose restart backend
```

---

## 🔧 Custom Port Mapping

If ports 8003/8503 are in use, change them in `.env`:

```bash
BACKEND_PORT=9003
FRONTEND_PORT=9503
```

Then restart:

```bash
docker compose up -d
```

---

## 🔒 Production Checklist

- [ ] Set a **strong, unique** `JWT_SECRET_KEY`
- [ ] Set a **strong** `ADMIN_PASSWORD`
- [ ] Add your **OTX API key** for live threat feeds
- [ ] Consider a reverse proxy (Nginx/Traefik) for TLS
- [ ] Set `DEBUG=false`
- [ ] Back up the SQLite volume regularly
- [ ] Restrict Docker port exposure (`127.0.0.1:8003:8003`) if only local access is needed

---

## 🐞 Troubleshooting

| Problem                                | Solution                                                        |
|----------------------------------------|-----------------------------------------------------------------|
| Frontend shows "Unable to connect"     | Wait for backend health check: `docker compose logs backend -f` |
| Port already in use                    | Change `BACKEND_PORT` / `FRONTEND_PORT` in `.env`               |
| Database is empty after restart        | DB auto-seeds on first run. Use `docker compose down -v` to reset |
| OTX shows "demo mode"                  | Set `OTX_API_KEY` in `.env` and rebuild                         |
| Permission denied on volume            | Run `docker compose down -v && docker compose up --build`       |
