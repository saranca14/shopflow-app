#!/bin/bash
set -euo pipefail

# ============================================================
# Build and push all microservice images to ECR
# Usage: ./scripts/build-and-push.sh
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Get AWS account ID and region from Terraform outputs
cd "$PROJECT_DIR/terraform"
AWS_REGION=$(terraform output -raw aws_region 2>/dev/null || echo "eu-west-1")
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
PROJECT_NAME="shopflow"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo "============================================"
echo "ECR Registry: ${ECR_REGISTRY}"
echo "Image Tag: ${IMAGE_TAG}"
echo "============================================"

# Login to ECR
echo "Logging into ECR..."
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ECR_REGISTRY"

# Services to build
SERVICES=(
    "frontend"
    "product-service"
    "cart-service"
    "order-service"
    "user-service"
    "payment-service"
)

# Build and push each service
for SERVICE in "${SERVICES[@]}"; do
    echo ""
    echo "============================================"
    echo "Building: ${SERVICE}"
    echo "============================================"
    
    FULL_IMAGE="${ECR_REGISTRY}/${PROJECT_NAME}/${SERVICE}:${IMAGE_TAG}"
    
    docker build \
        -t "${FULL_IMAGE}" \
        -f "$PROJECT_DIR/services/${SERVICE}/Dockerfile" \
        "$PROJECT_DIR/services/${SERVICE}"
    
    echo "Pushing: ${FULL_IMAGE}"
    docker push "${FULL_IMAGE}"
    
    echo "✅ ${SERVICE} pushed successfully"
done

echo ""
echo "============================================"
echo "All images built and pushed successfully!"
echo "============================================"
