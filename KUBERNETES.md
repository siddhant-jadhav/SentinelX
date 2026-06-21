# ☸️ SentinelX — Kubernetes Deployment Guide

Production-ready Kubernetes deployment for the SentinelX threat intelligence platform.

---

## 📋 Prerequisites

| Tool       | Version | Check Command             |
|------------|---------|---------------------------|
| kubectl    | 1.25+   | `kubectl version --client` |
| Docker     | 20.10+  | `docker --version`        |
| Cluster    | 1.25+   | `kubectl cluster-info`    |

### Supported Clusters

| Environment       | Notes                                              |
|-------------------|----------------------------------------------------|
| **Minikube**      | Enable ingress: `minikube addons enable ingress`   |
| **Docker Desktop**| Enable Kubernetes in settings                      |
| **kind**          | Install nginx ingress controller separately        |
| **EKS / GKE / AKS** | Use cloud StorageClass instead of hostPath      |

---

## 🚀 Quick Start

### 1. Build & Push Docker Images

```bash
# Build images
docker build -t sentinelx/backend:latest -f backend/Dockerfile .
docker build -t sentinelx/frontend:latest -f frontend/Dockerfile .

# For minikube — load directly (no push needed)
minikube image load sentinelx/backend:latest
minikube image load sentinelx/frontend:latest

# For remote registry — tag & push
docker tag sentinelx/backend:latest YOUR_REGISTRY/sentinelx/backend:latest
docker tag sentinelx/frontend:latest YOUR_REGISTRY/sentinelx/frontend:latest
docker push YOUR_REGISTRY/sentinelx/backend:latest
docker push YOUR_REGISTRY/sentinelx/frontend:latest
```

### 2. Configure Secrets

```bash
# Option A: Create secrets via kubectl (recommended)
kubectl create namespace sentinelx

kubectl create secret generic sentinelx-secrets \
  --namespace=sentinelx \
  --from-literal=JWT_SECRET_KEY="your-strong-secret-key" \
  --from-literal=OTX_API_KEY="your-otx-api-key" \
  --from-literal=ADMIN_PASSWORD="YourSecurePassword" \
  --from-literal=ANALYST_PASSWORD="analyst123"
```

```bash
# Option B: Edit k8s/secrets.yaml with base64 values
echo -n "your-strong-secret-key" | base64
# Paste output into secrets.yaml
```

### 3. Deploy

```bash
# Deploy all manifests at once
kubectl apply -k k8s/

# Or apply individually in order
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml         # Skip if using Option A above
kubectl apply -f k8s/persistent-volume.yaml
kubectl apply -f k8s/persistent-volume-claim.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
kubectl apply -f k8s/ingress.yaml
```

### 4. Verify Deployment

```bash
# Check all resources
kubectl get all -n sentinelx

# Watch pods come up
kubectl get pods -n sentinelx -w

# Check ingress
kubectl get ingress -n sentinelx
```

### 5. Access the Application

#### Via Ingress (recommended)

```bash
# Minikube
echo "$(minikube ip) sentinelx.local api.sentinelx.local" | sudo tee -a /etc/hosts

# Then open
open http://sentinelx.local          # Frontend
open http://api.sentinelx.local/docs # API Docs
```

#### Via Port-Forward (any cluster)

```bash
# Frontend
kubectl port-forward svc/sentinelx-frontend 8503:8503 -n sentinelx

# Backend
kubectl port-forward svc/sentinelx-backend 8003:8003 -n sentinelx
```

Then open:
- Frontend: http://localhost:8503
- API Docs: http://localhost:8003/docs

---

## 🏗️ Architecture

```
                    ┌──────────────────────────────────────────┐
                    │           Kubernetes Cluster             │
                    │                                          │
                    │  ┌────────────────────────────────────┐  │
                    │  │         Ingress Controller         │  │
                    │  │   sentinelx.local → frontend:8503  │  │
                    │  │   api.sentinelx.local → backend:8003│  │
                    │  └───────────┬──────────┬─────────────┘  │
                    │              │          │                 │
Internet ─────────►│     ┌────────▼───┐  ┌───▼────────┐       │
                    │     │  Frontend  │  │  Backend   │       │
                    │     │  Service   │  │  Service   │       │
                    │     │ (ClusterIP)│  │ (ClusterIP)│       │
                    │     └─────┬──┬──┘  └─────┬──────┘       │
                    │           │  │            │              │
                    │     ┌─────▼──▼──┐  ┌─────▼──────┐       │
                    │     │ Pod   Pod │  │    Pod     │       │
                    │     │ (×2)     │  │   (×1)     │       │
                    │     │ Streamlit│  │  FastAPI   │       │
                    │     └──────────┘  └─────┬──────┘       │
                    │                         │              │
                    │                   ┌─────▼──────┐       │
                    │                   │    PVC     │       │
                    │                   │  SQLite DB │       │
                    │                   └────────────┘       │
                    └──────────────────────────────────────────┘
```

### Component Summary

| Component        | Replicas | Type       | Port | Notes                          |
|------------------|----------|------------|------|--------------------------------|
| Backend          | 1        | Deployment | 8003 | SQLite requires single writer  |
| Frontend         | 2        | Deployment | 8503 | Stateless, horizontally scaled |
| Backend Service  | —        | ClusterIP  | 8003 | Internal DNS                   |
| Frontend Service | —        | ClusterIP  | 8503 | Internal DNS                   |
| Ingress          | —        | Ingress    | 80   | Routes by hostname             |
| SQLite Storage   | —        | PVC        | —    | 1Gi ReadWriteOnce              |

> **Why 1 backend replica?** SQLite is a file-based database. Concurrent writes from
> multiple pods cause `database is locked` errors. For 2+ backend replicas, migrate
> to PostgreSQL or MySQL.

---

## ⚙️ Configuration Reference

### ConfigMap (`sentinelx-config`)

| Key              | Value                              | Description              |
|------------------|------------------------------------|--------------------------|
| `DATABASE_URL`   | `sqlite:////data/sentinelx.db`     | SQLite path in container |
| `BACKEND_URL`    | `http://sentinelx-backend:8003`    | K8s service DNS          |
| `BACKEND_PORT`   | `8003`                             | Backend listen port      |
| `FRONTEND_PORT`  | `8503`                             | Frontend listen port     |
| `DEBUG`          | `false`                            | Debug logging            |

### Secrets (`sentinelx-secrets`)

| Key                | Description                      |
|--------------------|----------------------------------|
| `JWT_SECRET_KEY`   | JWT signing secret               |
| `OTX_API_KEY`      | AlienVault OTX API key           |
| `ADMIN_PASSWORD`   | Admin account password           |
| `ANALYST_PASSWORD` | Analyst account password         |

---

## 📦 Common Operations

### Scale Frontend

```bash
kubectl scale deployment sentinelx-frontend --replicas=3 -n sentinelx
```

### Update Images (rolling)

```bash
kubectl set image deployment/sentinelx-backend \
  backend=sentinelx/backend:v1.1.0 -n sentinelx

kubectl set image deployment/sentinelx-frontend \
  frontend=sentinelx/frontend:v1.1.0 -n sentinelx
```

### Rollback

```bash
kubectl rollout undo deployment/sentinelx-backend -n sentinelx
kubectl rollout undo deployment/sentinelx-frontend -n sentinelx
```

### View Logs

```bash
# Backend logs
kubectl logs -l app.kubernetes.io/component=backend -n sentinelx -f

# Frontend logs
kubectl logs -l app.kubernetes.io/component=frontend -n sentinelx -f

# Specific pod
kubectl logs sentinelx-backend-xxxxx -n sentinelx
```

### Check Health

```bash
# Backend health (via port-forward)
kubectl port-forward svc/sentinelx-backend 8003:8003 -n sentinelx &
curl http://localhost:8003/health
```

### Exec Into Pod

```bash
kubectl exec -it deployment/sentinelx-backend -n sentinelx -- /bin/sh
```

### Backup SQLite Database

```bash
# Copy database from pod to local
kubectl cp sentinelx/$(kubectl get pods -n sentinelx -l app.kubernetes.io/component=backend \
  -o jsonpath='{.items[0].metadata.name}'):/data/sentinelx.db ./backup.db
```

### Full Teardown

```bash
kubectl delete -k k8s/
# Or
kubectl delete namespace sentinelx
```

---

## 🔒 Production Hardening

### TLS with cert-manager

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml

# Create ClusterIssuer
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@yourdomain.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
      - http01:
          ingress:
            class: nginx
EOF
```

Then uncomment the TLS section in `k8s/ingress.yaml`.

### Cloud Storage (replace hostPath)

For **AWS EKS**:
```yaml
# Replace persistent-volume.yaml with:
storageClassName: gp3
```

For **GKE**:
```yaml
storageClassName: standard
```

### Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-only-from-frontend
  namespace: sentinelx
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/component: backend
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app.kubernetes.io/component: frontend
      ports:
        - port: 8003
```

---

## 🐞 Troubleshooting

| Issue                              | Command / Solution                                          |
|------------------------------------|-------------------------------------------------------------|
| Pods stuck in `Pending`            | `kubectl describe pod <name> -n sentinelx` — check PVC     |
| Pods in `CrashLoopBackOff`         | `kubectl logs <pod> -n sentinelx` — check startup errors    |
| `ImagePullBackOff`                 | Verify image exists; check imagePullSecrets                  |
| PVC stuck in `Pending`             | Ensure PV exists with matching `storageClassName`            |
| Ingress not routing                | `kubectl describe ingress -n sentinelx`; check controller   |
| Frontend can't reach backend       | `kubectl exec` into frontend pod; `curl sentinelx-backend:8003/health` |
| Database locked errors             | Ensure only 1 backend replica; check PVC access mode        |
| WebSocket errors in Streamlit      | Verify ingress annotations include upgrade headers          |
