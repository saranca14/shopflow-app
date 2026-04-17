# ShopFlow — Microservices E-Commerce App

Application source code for the ShopFlow e-commerce platform. Part of a 3-repo architecture.

## Repos

| Repo | Purpose |
|------|---------|
| **shopflow-app** (this) | Application source code + Dockerfiles |
| **shopflow-gitops** | K8s manifests, ArgoCD, Tekton |
| **shopflow-infra** | Terraform (3 EKS clusters, VPC, ECR) |

## Services

| Service | Tech | Port | Description |
|---------|------|------|-------------|
| **Frontend** | Flask + Jinja2 | 5000 | Server-side rendered web UI |
| **Product Service** | FastAPI + PostgreSQL | 8001 | Product catalog CRUD |
| **Cart Service** | FastAPI + Redis | 8002 | Shopping cart management |
| **Order Service** | FastAPI + PostgreSQL | 8003 | Order processing (orchestrator) |
| **User Service** | FastAPI + PostgreSQL | 8004 | Auth (JWT) & user profiles |
| **Payment Service** | FastAPI | 8005 | Mock payment processor |

## Local Development

```bash
docker-compose up --build
# Frontend: http://localhost:5000
# RabbitMQ UI: http://localhost:15672 (guest/guest)
```

## CI/CD Flow

Push to this repo → Tekton (on Platform cluster) builds/pushes images → updates `shopflow-gitops` → ArgoCD syncs to Workload cluster.
