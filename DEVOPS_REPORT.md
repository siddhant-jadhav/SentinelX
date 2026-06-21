# SentinelX — DevOps Implementation Report

**Project:** Cyber Threat Intelligence Sharing Platform
**Course:** B.Tech CSE 2024-28 | DevOps | Semester IV
**University:** ITM Skills University
**Student:** Siddhant Jadhav
**GitHub:** https://github.com/siddhant-jadhav/SentinelX

---

## 1. Problem Statement

> The platform operates in a highly sensitive environment requiring extreme reliability, regulatory compliance, secure data sharing, and rapid incident response. Existing infrastructure faces challenges related to **scalability**, **observability**, **deployment automation**, and **disaster recovery**.

## 2. Solution Overview

SentinelX uses a complete DevOps pipeline to solve these challenges:

| Challenge | Tool Used | How It Solves It |
|-----------|-----------|-----------------|
| Packaging & Consistency | **Docker** | Containers ensure the app runs identically everywhere |
| Scalability & Reliability | **Kubernetes** | Auto-restart, scaling, and zero-downtime deployments |
| Deployment Automation | **Jenkins** | Automated CI/CD pipeline from code push to deployment |
| Infrastructure Management | **Terraform** | Infrastructure as Code — recreate servers with one command |
| Observability | **Prometheus + Grafana** | Real-time monitoring of requests, CPU, RAM, and uptime |

---

## 3. Application Architecture

SentinelX is a two-tier web application:

- **Backend:** FastAPI (Python) — REST API with JWT authentication, OTX threat intelligence integration, SQLite database
- **Frontend:** Streamlit (Python) — Interactive dashboard for threat analysis and visualization

```
┌──────────────┐     HTTP      ┌──────────────┐     SQL      ┌──────────┐
│   Streamlit  │ ────────────→ │   FastAPI     │ ──────────→ │  SQLite  │
│   Frontend   │    :8503      │   Backend     │    :8003     │    DB    │
└──────────────┘               └──────┬───────┘              └──────────┘
                                      │
                                      │ API
                                      ▼
                               ┌──────────────┐
                               │  AlienVault  │
                               │   OTX API    │
                               └──────────────┘
```

> **📸 Screenshot: SentinelX Dashboard (Home Page)**
>
> `[INSERT SCREENSHOT OF SENTINELX DASHBOARD HERE]`

---

## 4. Docker — Containerization

### Why Docker?

Without Docker, every team member would need to manually install Python 3.12, all pip packages (FastAPI, Streamlit, SQLAlchemy, etc.), and configure environment variables. One wrong version breaks the entire app. Docker eliminates this "works on my machine" problem.

### What We Did

- Created **2 Dockerfiles** — one for the backend, one for the frontend
- Created a **docker-compose.yml** that orchestrates 4 services:
  - `sentinelx-backend` (FastAPI on port 8003)
  - `sentinelx-frontend` (Streamlit on port 8503)
  - `sentinelx-prometheus` (Metrics collector on port 9090)
  - `sentinelx-grafana` (Monitoring dashboard on port 3000)

### How It Works

```bash
# One command starts the entire platform
docker compose up --build
```

This single command:
1. Builds both Docker images with all dependencies
2. Creates an isolated network for inter-service communication
3. Sets up a persistent volume for the database
4. Starts all 4 services with health checks

### Key Configuration (docker-compose.yml)

```yaml
services:
  backend:
    build:
      dockerfile: backend/Dockerfile
    ports:
      - "8003:8003"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8003/health"]
    volumes:
      - sentinelx-data:/data

  frontend:
    build:
      dockerfile: frontend/Dockerfile
    ports:
      - "8503:8503"
    environment:
      - BACKEND_URL=http://backend:8003
    depends_on:
      backend:
        condition: service_healthy
```

> **📸 Screenshot: Docker containers running**
>
> `[INSERT SCREENSHOT OF "docker compose ps" or "docker ps" OUTPUT HERE]`

> **📸 Screenshot: Docker build output**
>
> `[INSERT SCREENSHOT OF "docker compose up --build" OUTPUT HERE]`

---

## 5. Kubernetes — Container Orchestration

### Why Kubernetes?

Docker Compose runs containers on a **single machine** (your laptop). In production, we need:
- **Auto-restart** if a container crashes
- **Scaling** to handle more users (1 replica → 5 replicas)
- **Zero-downtime deployments** when updating the application
- **Secure secrets management** for API keys and passwords

Kubernetes solves all of these.

### What We Did

Created **11 Kubernetes manifest files** in the `k8s/` directory:

| File | Purpose |
|------|---------|
| `namespace.yaml` | Creates isolated `sentinelx` namespace |
| `configmap.yaml` | Stores application configuration (backend URL, debug mode) |
| `secrets.yaml` | Stores sensitive data — JWT keys, API keys, passwords (base64 encoded) |
| `backend-deployment.yaml` | Defines backend container spec with 1 replica |
| `frontend-deployment.yaml` | Defines frontend container spec with 1 replica |
| `backend-service.yaml` | Exposes backend internally at port 8003 |
| `frontend-service.yaml` | Exposes frontend externally via NodePort 30503 |
| `persistent-volume.yaml` | Reserves 1Gi disk storage for the SQLite database |
| `persistent-volume-claim.yaml` | Claims the reserved storage for the backend |
| `ingress.yaml` | Routes external HTTP traffic to the correct service |
| `kustomization.yaml` | Bundles all manifests for single-command deployment |

### How It Works

```bash
# Deploy the entire application to Kubernetes
kubectl apply -k k8s/
```

### Key Configuration — Backend Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sentinelx-backend
  namespace: sentinelx
spec:
  replicas: 1         # Can scale to 5+ for production
  template:
    spec:
      containers:
        - name: backend
          image: sentinelx-backend:latest
          ports:
            - containerPort: 8003
          envFrom:
            - configMapRef:
                name: sentinelx-config
            - secretRef:
                name: sentinelx-secrets
```

### Key Configuration — Secrets Management

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: sentinelx-secrets
  namespace: sentinelx
type: Opaque
data:
  JWT_SECRET_KEY: <base64-encoded>
  OTX_API_KEY: <base64-encoded>
  ADMIN_PASSWORD: <base64-encoded>
```

> **📸 Screenshot: Kubernetes pods running**
>
> `[INSERT SCREENSHOT OF "kubectl get pods -n sentinelx" HERE]`

> **📸 Screenshot: Kubernetes services**
>
> `[INSERT SCREENSHOT OF "kubectl get svc -n sentinelx" HERE]`

---

## 6. Jenkins — CI/CD Pipeline

### Why Jenkins?

Without automation, every deployment requires manual steps — pull code, build images, start containers, verify. Jenkins automates this entire pipeline so that every code push triggers an automatic build and deployment.

### What We Did

Created a **Jenkinsfile** with a 5-stage pipeline:

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Checkout │ →  │  Verify  │ →  │  Build   │ →  │  Deploy  │ →  │  Verify  │
│   Code   │    │  Docker  │    │  Images  │    │   App    │    │  Health  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
```

### Pipeline Stages

| Stage | What It Does | Command |
|-------|-------------|---------|
| **Checkout** | Pulls latest code from GitHub | `git checkout` |
| **Verify Environment** | Checks Docker and Docker Compose are installed | `docker --version` |
| **Build Docker Images** | Builds backend and frontend images | `docker compose build` |
| **Start Application** | Starts all containers in background | `docker compose up -d` |
| **Verify Deployment** | Checks backend health endpoint responds | `curl http://localhost:8003/health` |

### Key Configuration (Jenkinsfile)

```groovy
pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/siddhant-jadhav/SentinelX.git'
            }
        }
        stage('Build Docker Images') {
            steps {
                sh 'docker compose build'
            }
        }
        stage('Start Application') {
            steps {
                sh 'docker compose up -d'
            }
        }
        stage('Verify Deployment') {
            steps {
                sh 'curl -f http://localhost:8003/health'
            }
        }
    }
}
```

> **📸 Screenshot: Jenkins pipeline dashboard**
>
> `[INSERT SCREENSHOT OF JENKINS PIPELINE VIEW HERE]`

> **📸 Screenshot: Jenkins build success**
>
> `[INSERT SCREENSHOT OF JENKINS BUILD OUTPUT (GREEN) HERE]`

---

## 7. Terraform — Infrastructure as Code

### Why Terraform?

Before we can run our Docker containers anywhere, we need a **server**. Manually creating an AWS server through the console means clicking through dozens of settings — instance type, security groups, SSH keys, startup scripts. If that server crashes or gets terminated, you'd have to remember every setting and redo it all manually.

Terraform lets us define all of that as code. The first time, it creates the server. If the server ever crashes, the same code recreates an identical server.

### What We Did

Created **6 Terraform files** in the `terraform/` directory:

| File | Purpose |
|------|---------|
| `provider.tf` | Configures AWS provider (ap-south-1 Mumbai region) |
| `variables.tf` | Defines configurable parameters (instance type, key pair) |
| `main.tf` | Creates Security Group (firewall) + EC2 instance (server) |
| `userdata.sh` | Bootstrap script — installs Docker on the new server automatically |
| `outputs.tf` | Prints the server's public IP after creation |
| `terraform.tfvars.example` | Example variable values |

### The Actual Workflow

**Step 1 — First-time setup (create the server):**
```bash
cd terraform/
terraform init      # Download AWS provider
terraform plan      # Preview what will be created
terraform apply     # Creates EC2 instance + Security Group on AWS
# Output: public_ip = "13.232.xx.xx"
```

**Step 2 — Deploy the application on that server:**
```bash
ssh -i mykey.pem ubuntu@13.232.xx.xx    # SSH into the server
git clone https://github.com/siddhant-jadhav/SentinelX.git
cd SentinelX
docker compose up --build -d             # Start the application
```

**Step 3 — If the server crashes or gets terminated:**
```bash
cd terraform/
terraform apply     # Recreates the EXACT same infrastructure
# New server with same security group, same ports, Docker pre-installed
# Then SSH in and deploy again
```

### What Gets Created

```
AWS Cloud (ap-south-1)
│
├── Security Group: sentinelx-sg
│   ├── Inbound: Port 22 (SSH)
│   ├── Inbound: Port 8003 (Backend API)
│   ├── Inbound: Port 8503 (Frontend)
│   ├── Inbound: Port 3000 (Grafana)
│   └── Outbound: All traffic
│
└── EC2 Instance: sentinelx-server
    ├── AMI: Ubuntu 22.04
    ├── Type: t2.micro (free tier)
    └── UserData: Installs Docker automatically on boot
```

### Key Configuration (main.tf)

```hcl
resource "aws_instance" "sentinelx" {
  ami           = "ami-0f5ee92e2d63afc18"  # Ubuntu 22.04
  instance_type = var.instance_type         # t2.micro
  key_name      = var.key_pair_name

  vpc_security_group_ids = [aws_security_group.sentinelx.id]
  user_data              = file("userdata.sh")

  tags = {
    Name = "sentinelx-server"
  }
}
```

### How Terraform Enables Disaster Recovery

| Scenario | Without Terraform | With Terraform |
|----------|------------------|---------------|
| Server crashes | Manually recreate everything on AWS console — hope you remember all settings | `terraform apply` — identical server in 2 minutes |
| Need a second server | Repeat all manual steps again | Change `count = 2` in code, run `terraform apply` |
| Decommission everything | Manually find and delete each AWS resource | `terraform destroy` — clean removal |
| Audit trail | No record of what was created or changed | Infrastructure is in Git — full version history |

> **📸 Screenshot: terraform plan output**
>
> `[INSERT SCREENSHOT OF "terraform plan" OUTPUT HERE]`

> **📸 Screenshot: terraform apply output**
>
> `[INSERT SCREENSHOT OF "terraform apply" OUTPUT HERE]`

---

## 8. Prometheus & Grafana — Monitoring & Observability

### Why Monitoring?

The case study requires **observability** — the ability to see what's happening inside the application in real-time. Without monitoring, you won't know if the server is overloaded, running out of memory, or receiving errors until users complain.

### What We Did

**Prometheus** collects metrics from the backend every 15 seconds.
**Grafana** displays those metrics in a visual dashboard.

### How It Works

```
┌──────────────┐  scrapes /metrics  ┌──────────────┐  queries data  ┌──────────────┐
│   FastAPI     │ ←──────────────── │  Prometheus  │ ←───────────── │   Grafana    │
│   Backend     │    every 15s      │   :9090      │                │   :3000      │
└──────────────┘                    └──────────────┘                └──────────────┘
```

1. Backend exposes a `/metrics` endpoint with live stats
2. Prometheus scrapes this endpoint every 15 seconds and stores the data
3. Grafana queries Prometheus and displays it in visual panels

### Metrics We Track

| Metric | What It Measures |
|--------|-----------------|
| `sentinelx_requests_total` | Total HTTP requests received |
| `sentinelx_uptime_seconds` | How long the server has been running |
| `sentinelx_cpu_seconds_total` | CPU time used by the backend process |
| `sentinelx_memory_bytes` | RAM used by the backend process |
| `sentinelx_disk_used_bytes` | Disk space used on the data volume |
| `up{job="sentinelx-backend"}` | Is the backend alive? (1 = UP, 0 = DOWN) |

### Grafana Dashboard Panels

| Panel | Type | What It Shows |
|-------|------|--------------|
| Total Requests | Stat | Number of API calls received |
| Server Uptime | Stat | Time since last restart |
| Backend Status | Stat | UP or DOWN indicator |
| CPU Usage | Line Chart | CPU consumption over time |
| RAM Usage | Line Chart | Memory consumption over time |
| Storage Usage | Gauge | Disk space used (percentage) |

### Key Configuration (prometheus.yml)

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'sentinelx-backend'
    static_configs:
      - targets: ['backend:8003']
```

> **📸 Screenshot: Grafana monitoring dashboard**
>
> `[INSERT SCREENSHOT OF GRAFANA DASHBOARD WITH ALL 6 PANELS HERE]`

> **📸 Screenshot: Prometheus targets page**
>
> `[INSERT SCREENSHOT OF http://localhost:9090/targets SHOWING BACKEND AS "UP" HERE]`

---

## 9. Complete DevOps Pipeline Flow

```
Developer writes code
        │
        ▼
Pushes to GitHub (source code repository)
        │
        ▼
Jenkins detects the push (CI/CD automation)
        │
        ├── Stage 1: Checkout code from GitHub
        ├── Stage 2: Verify Docker is available
        ├── Stage 3: Build Docker images
        ├── Stage 4: Deploy with Docker Compose
        └── Stage 5: Verify health endpoint
                │
                ▼
Docker containers running (containerization)
        │
        ├── sentinelx-backend   (:8003)
        ├── sentinelx-frontend  (:8503)
        ├── sentinelx-prometheus (:9090)
        └── sentinelx-grafana   (:3000)
                │
                ▼
Kubernetes manages containers in production
        │
        ├── Auto-restart on crash
        ├── Scaling (replicas)
        ├── Secrets management
        └── Persistent storage
                │
                ▼
Terraform provisions the AWS infrastructure
        │
        ├── EC2 instance (Ubuntu server)
        ├── Security Group (firewall)
        └── UserData (installs Docker)
                │
                ▼
Prometheus + Grafana monitors everything
        │
        ├── Requests, Uptime, CPU, RAM, Disk
        └── Real-time dashboard at :3000
```

---

## 10. How Each Tool Maps to Case Study Requirements

| Case Study Requirement | Tools Used | Implementation |
|----------------------|-----------|---------------|
| **Extreme reliability** | Kubernetes, Docker | Auto-restart crashed containers, health checks |
| **Regulatory compliance** | Terraform, Git | Infrastructure as code, version-controlled audit trail |
| **Secure data sharing** | K8s Secrets, JWT | Passwords in K8s Secrets, API authenticated with JWT tokens |
| **Rapid incident response** | Jenkins, K8s | Automated deployment pipeline, zero-downtime rolling updates |
| **Scalability** | Kubernetes | Increase replicas from 1 to N with one config change |
| **Observability** | Prometheus, Grafana | Real-time monitoring dashboard with CPU, RAM, requests, uptime |
| **Deployment automation** | Jenkins, Docker Compose | Push code → automatic build → deploy → verify |
| **Disaster recovery** | Terraform, K8s PV | `terraform apply` recreates infrastructure, PersistentVolume preserves data |

---

## 11. Project Repository Structure

```
SentinelX/
├── backend/                  # FastAPI backend source code
│   ├── Dockerfile           # Backend container definition
│   ├── main.py              # API entry point with /metrics endpoint
│   ├── routers/             # API route handlers
│   └── services/            # Business logic
├── frontend/                 # Streamlit frontend source code
│   ├── Dockerfile           # Frontend container definition
│   └── app.py               # Dashboard entry point
├── k8s/                      # Kubernetes manifests (11 files)
├── terraform/                # Terraform infrastructure code (6 files)
├── monitoring/               # Prometheus & Grafana configuration
│   ├── prometheus.yml
│   └── grafana/
│       ├── provisioning/    # Auto-configure datasource
│       └── dashboards/      # Pre-built dashboard JSON
├── docker-compose.yml        # Multi-service orchestration
├── Jenkinsfile              # CI/CD pipeline definition
├── .gitignore               # Ignore venv, cache, secrets
└── README.md                # Project documentation
```

---

*This document demonstrates the complete DevOps implementation for the SentinelX Cyber Threat Intelligence Sharing Platform, covering containerization, orchestration, CI/CD automation, infrastructure as code, and monitoring.*
