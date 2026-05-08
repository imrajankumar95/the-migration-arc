# The Migration Arc

Multi-cloud container deployment pipeline: from local Docker development to production Kubernetes on AWS — deployed across ECS (Fargate) and EKS.

---

## What This Project Does

Takes a Flask API through four deployment stages, each increasing in complexity:

| Phase | Platform | How It Runs |
|-------|----------|-------------|
| **Phase 1** | Local (WSL2) | Docker container on localhost |
| **Phase 2** | AWS ECS | Fargate serverless container via ECR |
| **Phase 3** | AWS EKS | Kubernetes pods with LoadBalancer |
| **Phase 4** | Azure AKS | *(planned)* ACR + AKS + Azure DevOps CI/CD |

Each phase deploys the **same containerized app** to a progressively more complex environment.

---

## Architecture

```
                    ┌─────────────────────────────────┐
                    │         Flask API (app.py)       │
                    │    /  /health  /info  /ping      │
                    └──────────────┬──────────────────┘
                                   │
                            Docker Image
                           (multi-stage build)
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                     │
        Phase 1: Local       Phase 2: ECS          Phase 3: EKS
        ──────────────       ─────────────         ─────────────
        Docker run           ECR → Fargate         ECR → K8s Pods
        localhost:5000       Public IP:5000        LoadBalancer:80
                             1 task, 0.25 vCPU     2 replicas
                             0.5 GB RAM            t3.small nodes
```

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| **Flask** | Python API (5 endpoints) |
| **Docker** | Multi-stage container build |
| **Gunicorn** | Production WSGI server |
| **GitHub Actions** | CI: lint, test, build, push to GHCR |
| **AWS ECR** | Private container registry |
| **AWS ECS (Fargate)** | Serverless container deployment |
| **AWS EKS** | Managed Kubernetes cluster |
| **kubectl** | Kubernetes deployment management |
| **eksctl** | EKS cluster provisioning |

---

## Project Structure

```
the-migration-arc/
├── app/
│   ├── app.py              # Flask API (5 routes)
│   ├── Dockerfile          # Multi-stage build (builder + runtime)
│   └── requirements.txt    # flask + gunicorn
├── k8s/
│   ├── deployment.yaml     # Kubernetes Deployment (2 replicas)
│   └── service.yaml        # LoadBalancer Service (80 → 5000)
├── tests/
│   └── test_app.py         # 5 unit tests (pytest)
├── .github/workflows/
│   └── ci.yml              # CI: lint → test → build → push to GHCR
├── Makefile                # Local dev commands (build/run/stop/test)
└── README.md
```

---

## API Endpoints

| Route | Response |
|-------|----------|
| `GET /` | Service name, status, message |
| `GET /health` | Health check with UTC timestamp |
| `GET /info` | Hostname, OS, Python version, app version |
| `GET /ping` | `{"pong": true}` |
| `GET /metrics/custom` | Request count, uptime, environment |

---

## Phase Details

### Phase 1 — Local Docker (WSL2)

Built and ran the container locally:

```bash
make build        # docker build -t migration-arc-app:local ./app
make run          # docker run --rm -p 5000:5000 migration-arc-app:local
curl localhost:5000
```

**Key decisions:**
- Multi-stage Dockerfile — build dependencies stay out of runtime image
- Non-root user (`appuser`) for container security
- Gunicorn with 2 workers instead of Flask dev server

### Phase 2 — AWS ECS (Fargate)

Pushed container to ECR, deployed as Fargate task:

1. Created private ECR repo (`migration-arc-flask`)
2. Authenticated Docker to ECR, tagged and pushed image
3. Created ECS cluster (`migration-arc-project-cluster`)
4. Defined task (0.25 vCPU, 0.5 GB, port 5000)
5. Created service with public IP + security group (TCP 5000 open)

**Result:** Flask API accessible via public IP on port 5000.

### Phase 3 — AWS EKS (Kubernetes)

Created managed Kubernetes cluster, deployed as pods:

1. Provisioned EKS cluster with `eksctl` (2x t3.small nodes)
2. Created Deployment (2 replicas pulling from ECR)
3. Created LoadBalancer Service (port 80 → container 5000)
4. App accessible via AWS ELB URL

**Result:** Flask API running on Kubernetes with load balancing across 2 pods.

### Phase 4 — Azure AKS *(planned)*

- Push image to Azure Container Registry (ACR)
- Deploy to Azure Kubernetes Service (AKS)
- CI/CD via Azure DevOps pipeline

---

## Issues & Solutions

| # | Issue | Root Cause | Fix |
|---|-------|-----------|-----|
| 1 | `docker build` failed — "no such file or directory" | Dockerfile is in `./app/`, not root. Build context wrong | Used `make build` which runs `docker build ./app` |
| 2 | ECS cluster creation failed — "Unable to assume service linked role" | New AWS account, ECS service-linked role did not exist | Ran `aws iam create-service-linked-role --aws-service-name ecs.amazonaws.com` |
| 3 | ECS cluster creation failed again — CloudFormation stack conflict | First failed attempt left orphaned CloudFormation stack | Deleted failed stack in CloudFormation console, retried with new cluster name |
| 4 | `eksctl create cluster` — AccessDeniedException | IAM user `rajan-admin` lacked EKS permissions | Added EKS policies + AdministratorAccess |
| 5 | YAML parse error — "could not find expected ':'" | Mixed tabs and spaces from Windows editor (Notepad) | Recreated YAML files in terminal using heredoc |
| 6 | Pods stuck in `Pending` — FailedScheduling | `t3.micro` nodes too small — system pods consumed all capacity | Upgraded to `t3.small` nodes via `eksctl create nodegroup` |

---

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`):

1. **On push/PR to main:** Lint with flake8 → Run 5 pytest tests
2. **On merge to main:** Build Docker image → Push to GitHub Container Registry (GHCR)
3. Uses Docker layer caching for fast builds

---

## Cost Notes

| Resource | Cost (24/7) | Notes |
|----------|------------|-------|
| ECS Fargate (0.25 vCPU) | ~$9/month | Serverless, pay per task |
| EKS control plane | $72/month | Fixed cost regardless of nodes |
| EKS nodes (2x t3.small) | ~$30/month | EC2 instances |
| EKS LoadBalancer | ~$18/month | AWS NLB/ALB |
| ECR storage | ~$0.01/month | Just image storage |
| **Total (all live)** | **~$129/month** | |
| **After cleanup** | **~$0.01/month** | Only ECR repo kept |

> Infrastructure was deployed for demonstration, verified working, then torn down to manage costs. Screenshots and deployment evidence in commit history.

---

## What I Learned

- **Docker multi-stage builds** reduce image size and separate build-time from runtime dependencies
- **ECS vs EKS tradeoff:** ECS simpler for single containers; EKS worth it when you need scaling, rolling updates, and multi-container orchestration
- **Fargate** eliminates server management but costs more per unit than EC2
- **Kubernetes YAML** — indentation matters, never edit with editors that mix tabs/spaces
- **IAM least privilege** is ideal but impractical for eksctl — it creates VPCs, roles, CloudFormation stacks, and EC2 instances
- **Node sizing matters** — t3.micro cannot run app pods because AWS system pods consume most capacity
- **Service-linked roles** are auto-created on first use in established accounts but may need manual creation in new accounts

---

## How to Run Locally

```bash
git clone https://github.com/imrajankumar95/the-migration-arc.git
cd the-migration-arc
make build
make run
# Visit http://localhost:5000
```

Run tests:
```bash
make test
```

---

## Author

**Rajan Kumar** — Cloud Computing student at George Brown College, Toronto.
Building toward a Cloud/DevOps co-op role (Fall 2026).

- [LinkedIn](https://www.linkedin.com/in/imrajankumar95/)
- [GitHub](https://github.com/imrajankumar95)
