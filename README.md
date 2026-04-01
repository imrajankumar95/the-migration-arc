# The Migration Arc

End-to-end container deployment pipeline: from local VM development to production-grade Kubernetes on AWS - provisioned entirely with Terraform.

---

## Overview

This project documents a full build-and-deploy journey across three progressive phases, simulating the kind of infrastructure lifecycle you'd encounter in a real DevOps environment:

- **Phase 1 - Local Dev Environment:** Reproducible VM setup using Vagrant + VirtualBox, containerized app with Docker
- **Phase 2 - Cloud Deployment:** Push container to AWS ECR, deploy to AWS ECS with Terraform-managed infrastructure
- **Phase 3 - Kubernetes Orchestration:** Local K3s cluster for dev parity, then full AWS EKS deployment via Terraform

Each phase builds on the last, creating a coherent story from laptop to cloud-scale orchestration.

---

## Architecture

```
Local Dev                Cloud (AWS)
──────────────────       ──────────────────────────────────
Vagrant VM
  └── Docker             Docker Image
       └── Nginx  ──────► AWS ECR (Container Registry)
            App                │
                               ▼
                         AWS ECS (Fargate)
                               │
                               ▼
                         AWS EKS (Kubernetes)
                         (Terraform-provisioned)

Local K3s ◄──────────── Dev parity cluster
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Local VM | Vagrant + VirtualBox |
| Containerization | Docker |
| Web Server | Nginx |
| Container Registry | AWS ECR |
| Container Orchestration (Cloud) | AWS ECS (Fargate), AWS EKS |
| Local Kubernetes | K3s |
| Infrastructure as Code | Terraform |
| Cloud Provider | AWS |

---

## Project Phases

### Phase 1 - Local Environment Setup ✅
- Vagrant + VirtualBox provisioning a Ubuntu VM
- Dockerized Nginx app running inside the VM
- Reproducible local dev setup via `Vagrantfile`

### Phase 2 - AWS Cloud Deployment ✅
- Docker image tagged and pushed to **AWS ECR**
- ECS task definition and service deployed via **Terraform**
- App running on AWS Fargate (serverless containers)

### Phase 3 - Kubernetes Orchestration 🔄 In Progress
- Local **K3s** cluster for Kubernetes dev parity
- Full **AWS EKS** cluster provisioned with Terraform
- App deployed as Kubernetes workload on EKS

---

## Repository Structure

```
the-migration-arc/
├── Vagrantfile              # Local VM provisioning
├── docker/
│   ├── Dockerfile           # App container definition
│   └── nginx.conf           # Nginx config
├── terraform/
│   ├── ecr/                 # ECR repository setup
│   ├── ecs/                 # ECS cluster, task def, service
│   └── eks/                 # EKS cluster and node groups
├── k8s/
│   └── deployment.yaml      # Kubernetes manifests
└── scripts/
    ├── build-push.sh        # Docker build + ECR push
    └── deploy.sh            # Terraform apply wrapper
```

---

## Prerequisites

- [Vagrant](https://www.vagrantup.com/) + [VirtualBox](https://www.virtualbox.org/)
- [Docker](https://www.docker.com/)
- [Terraform](https://www.terraform.io/) >= 1.5
- [AWS CLI](https://aws.amazon.com/cli/) configured with appropriate IAM permissions
- [kubectl](https://kubernetes.io/docs/tasks/tools/) + [K3s](https://k3s.io/) (for Phase 3 local)

---

## Quick Start

### Phase 1 - Run locally
```bash
git clone https://github.com/imrajankumar95/the-migration-arc.git
cd the-migration-arc
vagrant up
```

### Phase 2 - Deploy to AWS ECS
```bash
aws ecr get-login-password --region ca-central-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ca-central-1.amazonaws.com
bash scripts/build-push.sh
cd terraform/ecs && terraform init && terraform apply
```

### Phase 3 - Deploy to AWS EKS
```bash
cd terraform/eks && terraform init && terraform apply
aws eks update-kubeconfig --name migration-arc-cluster --region ca-central-1
kubectl apply -f k8s/deployment.yaml
```

---

## Related Projects

- **[infrastructure-monitoring](https://github.com/imrajankumar95/infrastructure-monitoring)** - Prometheus + Grafana observability stack that monitors this app.

---

## Status

| Phase | Status |
|---|---|
| Phase 1 - Local Dev (Vagrant + Docker) | ✅ Complete |
| Phase 2 - AWS ECS via Terraform | ✅ Complete |
| Phase 3 - K3s + AWS EKS | 🔄 In Progress |
| Observability Integration | 🔄 In Progress |
