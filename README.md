# The Migration Arc

Multi-cloud container deployment pipeline: from local VM development to production-grade Kubernetes on AWS and Azure — provisioned entirely with Terraform.

---

## Overview

This project documents a full build-and-deploy journey across four progressive phases, simulating the kind of infrastructure lifecycle you'd encounter in a real DevOps environment:

- **Phase 1 — Local Dev Environment:** Reproducible VM setup using Vagrant + VirtualBox, containerized app with Docker
- **Phase 2 — AWS Cloud Deployment:** Push container to AWS ECR, deploy to AWS ECS with Terraform-managed infrastructure
- **Phase 3 — AWS Kubernetes Orchestration:** Local K3s cluster for dev parity, then full AWS EKS deployment via Terraform
- **Phase 4 — Azure Deployment:** Push image to Azure Container Registry (ACR), deploy to Azure Kubernetes Service (AKS) via Terraform + Azure DevOps CI/CD pipeline

Each phase builds on the last. Phase 4 demonstrates the same workload running on both AWS and Azure — true multi-cloud capability using a single Terraform codebase.

---

## Architecture

```
Local Dev                AWS                          Azure
──────────────           ──────────────────────       ──────────────────────────
Vagrant VM
  └── Docker ──────────► AWS ECR                      Azure Container Registry
       └── Nginx              │                                   │
            App               ▼                                   ▼
                         AWS ECS (Fargate)             Azure Container Instances
                              │                                   │
                              ▼                                   ▼
                         AWS EKS (Kubernetes)          Azure Kubernetes Service
                         Terraform-provisioned         Terraform-provisioned

Local K3s ◄────── Dev parity cluster

CI/CD: Azure DevOps Pipeline ──► ACR ──► AKS
```

---

## Tech Stack

| Layer | AWS | Azure |
|---|---|---|
| Container Registry | AWS ECR | Azure Container Registry (ACR) |
| Container Orchestration | AWS ECS (Fargate) | Azure Container Instances |
| Kubernetes | AWS EKS | Azure Kubernetes Service (AKS) |
| Infrastructure as Code | Terraform | Terraform |
| CI/CD Pipeline | — | Azure DevOps |
| Local VM | Vagrant + VirtualBox | — |
| Local Kubernetes | K3s | — |
| Web Server | Nginx | Nginx |

---

## Project Phases

### Phase 1 — Local Environment Setup ✅
- Vagrant + VirtualBox provisioning a Ubuntu VM
- Dockerized Nginx app running inside the VM
- Reproducible local dev setup via `Vagrantfile`

### Phase 2 — AWS Cloud Deployment ✅
- Docker image tagged and pushed to **AWS ECR**
- ECS task definition and service deployed via **Terraform**
- App running on AWS Fargate (serverless containers)

### Phase 3 — AWS Kubernetes Orchestration 🔄 In Progress
- Local **K3s** cluster for Kubernetes dev parity
- Full **AWS EKS** cluster provisioned with Terraform
- App deployed as Kubernetes workload on EKS

### Phase 4 — Azure Deployment 📋 Planned
- Docker image pushed to **Azure Container Registry (ACR)**
- **Azure Kubernetes Service (AKS)** cluster provisioned with Terraform
- **Azure DevOps Pipeline** — CI/CD: build → push to ACR → deploy to AKS
- Side-by-side comparison: same app running on EKS (AWS) and AKS (Azure)

---

## Repository Structure

```
the-migration-arc/
├── Vagrantfile                  # Local VM provisioning
├── docker/
│   ├── Dockerfile               # App container definition
│   └── nginx.conf               # Nginx config
├── terraform/
│   ├── ecr/                     # AWS ECR repository
│   ├── ecs/                     # AWS ECS cluster, task def, service
│   ├── eks/                     # AWS EKS cluster and node groups
│   ├── acr/                     # Azure Container Registry
│   └── aks/                     # Azure Kubernetes Service cluster
├── k8s/
│   ├── aws/
│   │   └── deployment.yaml      # EKS Kubernetes manifests
│   └── azure/
│       └── deployment.yaml      # AKS Kubernetes manifests
├── azure-pipelines/
│   └── azure-pipelines.yml      # Azure DevOps CI/CD pipeline
└── scripts/
    ├── build-push-aws.sh        # Docker build + ECR push
    ├── build-push-azure.sh      # Docker build + ACR push
    └── deploy.sh                # Terraform apply wrapper
```

---

## Prerequisites

- [Vagrant](https://www.vagrantup.com/) + [VirtualBox](https://www.virtualbox.org/)
- [Docker](https://www.docker.com/)
- [Terraform](https://www.terraform.io/) >= 1.5
- [AWS CLI](https://aws.amazon.com/cli/) configured with IAM permissions
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/) configured with subscription access
- [kubectl](https://kubernetes.io/docs/tasks/tools/) + [K3s](https://k3s.io/) (Phase 3 local)
- Azure DevOps account (Phase 4 CI/CD)

---

## Quick Start

### Phase 1 — Run locally
```bash
git clone https://github.com/imrajankumar95/the-migration-arc.git
cd the-migration-arc
vagrant up
# App running inside VM via Docker + Nginx
```

### Phase 2 — Deploy to AWS ECS
```bash
aws ecr get-login-password --region ca-central-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ca-central-1.amazonaws.com
bash scripts/build-push-aws.sh
cd terraform/ecs && terraform init && terraform apply
```

### Phase 3 — Deploy to AWS EKS
```bash
cd terraform/eks && terraform init && terraform apply
aws eks update-kubeconfig --name migration-arc-cluster --region ca-central-1
kubectl apply -f k8s/aws/deployment.yaml
```

### Phase 4 — Deploy to Azure AKS
```bash
az login
az acr login --name migrationarcacr
bash scripts/build-push-azure.sh
cd terraform/aks && terraform init && terraform apply
az aks get-credentials --resource-group migration-arc-rg --name migration-arc-aks
kubectl apply -f k8s/azure/deployment.yaml
```

---

## Related Projects

- **[infrastructure-monitoring](https://github.com/imrajankumar95/infrastructure-monitoring)** — Prometheus + Grafana observability stack that monitors this app's health metrics and triggers alerts via Slack and email.

---

## Status

| Phase | Description | Status |
|---|---|---|
| Phase 1 | Local Dev — Vagrant + Docker | ✅ Complete |
| Phase 2 | AWS ECS via Terraform | ✅ Complete |
| Phase 3 | AWS K3s + EKS | 🔄 In Progress |
| Phase 4 | Azure ACR + AKS + Azure DevOps | 📋 Planned |
| Observability | Prometheus + Grafana integration | 🔄 In Progress |
