#!/bin/bash
set -euo pipefail

# ============================================================
# Deploy all Kubernetes manifests to EKS
# Usage: ./scripts/deploy.sh
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
K8S_DIR="$PROJECT_DIR/kubernetes"

# Get cluster info from Terraform
cd "$PROJECT_DIR/terraform"
CLUSTER_NAME=$(terraform output -raw cluster_name 2>/dev/null || echo "shopflow-eks")
AWS_REGION=$(terraform output -raw aws_region 2>/dev/null || echo "eu-west-1")
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo "============================================"
echo "Cluster: ${CLUSTER_NAME}"
echo "Region:  ${AWS_REGION}"
echo "============================================"

# Update kubeconfig
echo "Updating kubeconfig..."
aws eks update-kubeconfig --region "$AWS_REGION" --name "$CLUSTER_NAME"

# Replace placeholder image references in K8s manifests
echo "Preparing manifests..."
TEMP_DIR=$(mktemp -d)
cp -r "$K8S_DIR"/* "$TEMP_DIR/"

# Replace ACCOUNT_ID and REGION placeholders
find "$TEMP_DIR" -name "*.yaml" -exec sed -i.bak \
    -e "s|ACCOUNT_ID|${AWS_ACCOUNT_ID}|g" \
    -e "s|REGION|${AWS_REGION}|g" \
    -e "s|:latest|:${IMAGE_TAG}|g" \
    {} \;

# Apply manifests in order
echo ""
echo "1. Creating namespace..."
kubectl apply -f "$TEMP_DIR/namespace.yaml"

echo ""
echo "2. Deploying datastores..."
kubectl apply -f "$TEMP_DIR/datastores/"

echo "Waiting for datastores to be ready..."
kubectl -n ecommerce wait --for=condition=ready pod -l app=postgres --timeout=120s
kubectl -n ecommerce wait --for=condition=ready pod -l app=redis --timeout=60s
kubectl -n ecommerce wait --for=condition=ready pod -l app=rabbitmq --timeout=60s

echo ""
echo "3. Deploying microservices..."
kubectl apply -f "$TEMP_DIR/services/"

echo ""
echo "4. Deploying ingress..."
kubectl apply -f "$TEMP_DIR/ingress/"

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "============================================"
echo "Deployment complete!"
echo ""
echo "Check pod status:"
echo "  kubectl -n ecommerce get pods"
echo ""
echo "Get ingress URL:"
echo "  kubectl -n ecommerce get ingress"
echo "============================================"
