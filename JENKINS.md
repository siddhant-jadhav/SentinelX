# 🔧 SentinelX — Jenkins CI/CD Setup Guide

Complete guide for setting up Jenkins CI/CD pipeline for SentinelX.

---

## 📋 Prerequisites

| Requirement           | Version | Notes                                    |
|-----------------------|---------|------------------------------------------|
| Jenkins               | 2.400+  | LTS recommended                          |
| Docker                | 20.10+  | Must be accessible from Jenkins agent    |
| Docker Compose        | 2.0+    | V2 plugin (built into Docker CLI)        |
| Python                | 3.10+   | On Jenkins agent                         |
| Git                   | 2.30+   | For SCM checkout                         |
| GitHub account        | —       | For webhook integration                  |

---

## 1️⃣ Jenkins Installation

### Option A: Docker (Recommended)

```bash
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts
```

> **Important:** Mounting `docker.sock` allows Jenkins to run Docker commands.

Get the initial admin password:

```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### Option B: Native Install (macOS)

```bash
brew install jenkins-lts
brew services start jenkins-lts
```

Access Jenkins at: **http://localhost:8080**

---

## 2️⃣ Required Jenkins Plugins

Install these plugins via **Manage Jenkins → Plugin Manager → Available**:

| Plugin                    | Purpose                                |
|---------------------------|----------------------------------------|
| **Pipeline**              | Declarative pipeline support           |
| **Git**                   | Git SCM integration                    |
| **GitHub Integration**    | GitHub webhook triggers                |
| **Docker Pipeline**       | Docker build/push from pipelines       |
| **Credentials Binding**   | Inject secrets into pipeline           |
| **HTML Publisher**         | Publish test/coverage HTML reports     |
| **JUnit**                 | Parse and display test results         |
| **Timestamper**           | Add timestamps to console output       |
| **AnsiColor**             | Colored console output                 |
| **Pipeline Utility Steps**| File operations in pipeline            |
| **Warnings Next Gen**     | Parse lint/analysis warnings           |

### Install via CLI

```bash
jenkins-cli install-plugin \
  workflow-aggregator git github \
  docker-workflow credentials-binding \
  htmlpublisher junit timestamper \
  ansicolor pipeline-utility-steps warnings-ng
```

---

## 3️⃣ Jenkins Credentials Configuration

Navigate to: **Manage Jenkins → Credentials → System → Global credentials**

### Required Credentials

| Credential ID           | Type              | Description                         |
|-------------------------|-------------------|-------------------------------------|
| `DOCKER_REGISTRY_CREDS` | Username/Password | Docker Hub or registry credentials  |
| `OTX_API_KEY`           | Secret text       | AlienVault OTX API key              |
| `JWT_SECRET_KEY`        | Secret text       | JWT signing secret for production   |
| `ADMIN_PASSWORD`        | Secret text       | Admin account password              |

### How to Add Each Credential

#### Secret Text (OTX_API_KEY, JWT_SECRET_KEY, ADMIN_PASSWORD)

1. Click **Add Credentials**
2. Kind: **Secret text**
3. Scope: **Global**
4. Secret: *(paste your value)*
5. ID: `OTX_API_KEY` *(exact match)*
6. Description: `AlienVault OTX API Key`
7. Click **Create**

#### Username/Password (DOCKER_REGISTRY_CREDS)

1. Click **Add Credentials**
2. Kind: **Username with password**
3. Scope: **Global**
4. Username: *(your Docker Hub username)*
5. Password: *(your Docker Hub password or access token)*
6. ID: `DOCKER_REGISTRY_CREDS`
7. Click **Create**

---

## 4️⃣ Create Jenkins Pipeline Job

1. Go to **Dashboard → New Item**
2. Enter name: `SentinelX`
3. Select: **Pipeline**
4. Click **OK**

### Configure the Job

#### General

- ✅ **GitHub project**: `https://github.com/YOUR_USERNAME/SentinelX`
- ✅ **Do not allow concurrent builds**

#### Build Triggers

- ✅ **GitHub hook trigger for GITScm polling**

#### Pipeline

- **Definition**: Pipeline script from SCM
- **SCM**: Git
- **Repository URL**: `https://github.com/YOUR_USERNAME/SentinelX.git`
- **Credentials**: *(select your GitHub credentials)*
- **Branch Specifier**: `*/main`
- **Script Path**: `Jenkinsfile`

Click **Save**.

---

## 5️⃣ GitHub Webhook Configuration

### Step 1: Generate a GitHub Personal Access Token

1. Go to **GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. Click **Generate new token (classic)**
3. Scopes: `repo`, `admin:repo_hook`
4. Copy the token

### Step 2: Add GitHub Server in Jenkins

1. **Manage Jenkins → System → GitHub → GitHub Servers**
2. Click **Add GitHub Server**
3. Name: `GitHub`
4. API URL: `https://api.github.com`
5. Credentials: Add → Secret text → paste your GitHub token
6. ✅ **Manage hooks**
7. Click **Test connection** → should show "Credentials verified"

### Step 3: Configure the Webhook

#### Option A: Automatic (Jenkins manages hooks)

If you enabled "Manage hooks" above, Jenkins creates the webhook automatically when you build the first time.

#### Option B: Manual

1. Go to your GitHub repo → **Settings → Webhooks → Add webhook**
2. Configure:

| Field          | Value                                        |
|----------------|----------------------------------------------|
| Payload URL    | `http://YOUR_JENKINS_URL/github-webhook/`    |
| Content type   | `application/json`                           |
| Secret         | *(optional — shared secret)*                 |
| Events         | ✅ Just the push event                        |
| Active         | ✅ Checked                                    |

3. Click **Add webhook**

> **Note:** If Jenkins is behind a firewall, you'll need a tunnel (e.g., ngrok) or a public-facing URL.

### Step 4: Verify Webhook

1. Push a commit to your repository
2. Check **GitHub → Settings → Webhooks** → Recent Deliveries
3. Check **Jenkins → SentinelX job** → should trigger automatically

---

## 6️⃣ Environment Variables

### Pipeline-Level Variables (set in Jenkinsfile)

| Variable            | Default              | Description                    |
|---------------------|----------------------|--------------------------------|
| `APP_NAME`          | `sentinelx`          | Application name               |
| `DOCKER_REGISTRY`   | `docker.io`          | Docker registry URL            |
| `DOCKER_NAMESPACE`  | `sentinelx`          | Docker image namespace         |
| `PYTHON_VERSION`    | `3.12`               | Python version for tests       |

### Jenkins Global Variables (optional)

Set via **Manage Jenkins → System → Global Properties → Environment variables**:

| Variable            | Example              | Description                    |
|---------------------|----------------------|--------------------------------|
| `DOCKER_REGISTRY`   | `ghcr.io`            | Override default registry      |
| `DOCKER_NAMESPACE`  | `myorg/sentinelx`    | Override image namespace       |

### Job Parameters

The pipeline defines these build parameters:

| Parameter               | Type    | Default | Description                          |
|-------------------------|---------|---------|--------------------------------------|
| `SKIP_TESTS`            | Boolean | false   | Skip test stages (emergency deploy)  |
| `DEPLOY_TO_PRODUCTION`  | Boolean | false   | Force production deployment          |
| `DOCKER_TAG_OVERRIDE`   | String  | *(auto)* | Override Docker image tag            |

---

## 7️⃣ Pipeline Stages Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    SentinelX CI/CD Pipeline                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Checkout                                                │
│     └─ Clone repo, extract git metadata                    │
│                                                             │
│  2. Install Dependencies                                    │
│     └─ Create venv, install requirements + test deps        │
│                                                             │
│  3. Code Quality                                            │
│     └─ Flake8 lint, Python syntax validation                │
│                                                             │
│  4. Testing (parallel)                                      │
│     ├─ Backend Tests (pytest + coverage)                    │
│     └─ Frontend Validation (structure + syntax + imports)   │
│                                                             │
│  5. Docker Build                                            │
│     └─ Build backend + frontend images with labels          │
│                                                             │
│  6. Tag & Push Images (main branch only)                    │
│     └─ Push to Docker registry                              │
│                                                             │
│  7. Deploy (main branch only)                               │
│     └─ docker compose up with secrets                       │
│                                                             │
│  8. Post-Deployment Validation (main branch only)           │
│     └─ Health checks, container status, resource usage      │
│                                                             │
│  9. Generate Reports                                        │
│     └─ Build summary, archive artifacts                     │
│                                                             │
│  Post: Archive logs, publish HTML reports, clean workspace  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 8️⃣ Build Reports & Artifacts

After each build, Jenkins archives:

| Artifact                         | Description                          |
|----------------------------------|--------------------------------------|
| `reports/build-summary.txt`      | Build metadata summary               |
| `reports/backend-test-report.html` | Backend test results (HTML)        |
| `reports/frontend-test-report.html` | Frontend test results (HTML)      |
| `reports/backend-junit.xml`      | Backend JUnit XML (parsed by Jenkins)|
| `reports/frontend-junit.xml`     | Frontend JUnit XML                   |
| `reports/backend-coverage/`      | Code coverage HTML report            |
| `reports/backend-coverage.xml`   | Coverage XML (Cobertura format)      |
| `reports/flake8-report.txt`      | Lint results                         |
| `reports/docker-compose-logs.txt`| Docker container logs                |
| `reports/container-status.txt`   | Container status snapshot            |

Access reports at: **Jenkins → SentinelX → Build #N → Test Reports / Backend Coverage**

---

## 9️⃣ Troubleshooting

| Issue                                    | Solution                                                      |
|------------------------------------------|---------------------------------------------------------------|
| `docker: command not found`              | Install Docker on Jenkins agent or mount Docker socket        |
| `Permission denied on docker.sock`       | Add jenkins user to docker group: `usermod -aG docker jenkins`|
| Webhook not triggering                   | Check GitHub webhook delivery logs; verify Jenkins URL is reachable |
| Tests fail with `ModuleNotFoundError`    | Ensure `pip install -r requirements.txt` succeeds            |
| Docker build fails on Apple Silicon      | Add `--platform linux/amd64` to Dockerfile `FROM` line       |
| `No credentials found for DOCKER_REGISTRY_CREDS` | Add credential with exact ID match in Jenkins           |
| Pipeline timeout                         | Increase `timeout(time: 30)` in Jenkinsfile options          |
| Port already in use during deploy        | Change `BACKEND_PORT`/`FRONTEND_PORT` in env                 |

---

## 🔁 Running Locally (without Jenkins)

You can run the test suite locally:

```bash
# Install test dependencies
pip install pytest pytest-html pytest-cov flake8

# Run backend tests
DATABASE_URL="sqlite:///./test.db" pytest tests/test_backend.py -v

# Run frontend validation
pytest tests/test_frontend.py -v

# Run all tests with coverage
pytest tests/ -v --cov=backend --cov-report=html
```
