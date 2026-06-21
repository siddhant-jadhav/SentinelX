# 🛡️ SentinelX — Cyber Threat Intelligence Sharing Platform

A cyber threat intelligence platform that aggregates public threat intelligence from AlienVault OTX and combines it with community-submitted threat intelligence. Built as a semester project demonstrating DevOps practices with CI/CD, containerization, infrastructure-as-code, and container orchestration.

## 🚀 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit (Python) |
| Backend | FastAPI (Python REST API) |
| Database | SQLite with SQLAlchemy ORM |
| Threat Feed | AlienVault OTX API |
| Auth | JWT (python-jose + bcrypt) |
| Charts | Plotly |
| Containerization | Docker + Docker Compose |
| CI/CD | Jenkins Pipeline |
| Infrastructure | Terraform (AWS) |
| Orchestration | Kubernetes |

## 📋 Quick Start

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/SentinelX.git
cd SentinelX

# Make launch script executable
chmod +x run.sh

# Run SentinelX (installs deps, seeds DB, starts servers)
./run.sh
```

Then open:
- **Frontend**: http://localhost:8503
- **API Docs**: http://localhost:8003/docs

## 🔑 Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `SentinelX@2024` |
| Analyst | `analyst` | `analyst123` |

## 🏗️ Architecture

```
┌─────────────────┐     HTTP/REST      ┌─────────────────┐
│   Streamlit UI   │ ◄──────────────► │   FastAPI API    │
│   (Port 8503)    │                   │   (Port 8003)    │
└─────────────────┘                   └────────┬────────┘
                                               │
                              ┌────────────────┼────────────────┐
                              │                │                │
                        ┌─────▼─────┐   ┌──────▼──────┐  ┌─────▼─────┐
                        │  SQLite   │   │  OTX API    │  │  JWT Auth │
                        │  Database │   │  Service    │  │  Module   │
                        └───────────┘   └─────────────┘  └───────────┘
```

## 📱 Application Modules

| Module | Description |
|--------|-------------|
| 📊 Dashboard | Metrics, trend charts, and recent threat feed |
| 📡 Threat Feed | Unified feed from OTX and Community sources |
| 🔍 Search | Search indicators across local DB and OTX API |
| 📤 Submit Threat | Community threat intelligence submission form |
| 👥 Community | Browse approved community-submitted threats |
| 📈 Analytics | Charts, statistics, and trend analysis |
| ⚙️ Admin Panel | Review, approve, reject, and manage threats |

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/threats` | GET | List threats (with filters) |
| `/threats/{id}` | GET | Get threat by ID |
| `/threats` | POST | Submit new threat |
| `/threats/{id}` | PUT | Update threat (Admin) |
| `/threats/{id}` | DELETE | Delete threat (Admin) |
| `/search` | GET | Search indicators |
| `/otx/latest` | GET | Fetch OTX pulses |
| `/otx/sync` | POST | Sync OTX to DB (Admin) |
| `/analytics/overview` | GET | Analytics overview |
| `/analytics/trends` | GET | Daily trends |
| `/auth/login` | POST | User login |
| `/auth/register` | POST | User registration |
| `/health` | GET | Health check |

## 🐳 Docker Deployment

```bash
cp .env.example .env    # Edit with your OTX key
docker compose up --build -d

# Frontend: http://localhost:8503
# API Docs: http://localhost:8003/docs
```

See [DOCKER.md](DOCKER.md) for detailed Docker instructions.

## 🔧 Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed database
python3 -c "from backend.seed import seed_database; seed_database()"

# Start backend (terminal 1)
uvicorn backend.main:app --reload --port 8003

# Start frontend (terminal 2)
streamlit run frontend/app.py --server.port 8503
```

## 🔑 OTX API Key (Optional)

For live threat intelligence data, add your AlienVault OTX API key to `.env`:

```env
OTX_API_KEY=your_key_here
```

Get a free key at: https://otx.alienvault.com/api

Without a key, the platform runs in **demo mode** with realistic sample data.

## 📁 Project Structure

```
SentinelX/
├── backend/                  # FastAPI backend
│   ├── Dockerfile
│   ├── main.py               # App entry point
│   ├── config.py             # Environment configuration
│   ├── database.py           # SQLAlchemy setup
│   ├── models.py             # Database models
│   ├── schemas.py            # Pydantic schemas
│   ├── auth.py               # JWT authentication
│   ├── seed.py               # Database seeding
│   ├── routers/              # API route handlers
│   └── services/             # Business logic
├── frontend/                 # Streamlit frontend
│   ├── Dockerfile
│   ├── app.py                # Main dashboard
│   ├── assets/styles.css     # Custom CSS
│   ├── components/           # Reusable UI components
│   ├── pages/                # Application pages
│   └── utils/                # Helpers and API client
├── k8s/                      # Kubernetes manifests
├── terraform/                # Terraform IaC scripts
├── tests/                    # Test suites
├── docker-compose.yml        # Docker orchestration
├── Jenkinsfile               # CI/CD pipeline
├── requirements.txt          # Python dependencies
├── run.sh                    # Local launch script
└── .env.example              # Environment template
```

## 🚢 DevOps Deliverables

| Deliverable | Location | Description |
|-------------|----------|-------------|
| Docker | `docker-compose.yml`, `*/Dockerfile` | Containerized deployment |
| Jenkins | `Jenkinsfile`, `JENKINS.md` | CI/CD pipeline with testing |
| Terraform | `terraform/` | AWS infrastructure provisioning |
| Kubernetes | `k8s/` | Container orchestration manifests |
