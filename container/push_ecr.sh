#!/bin/bash

# Variables
IMAGE=scheduled-sagemaker-app-ecr-image
TAG=dev # stageによって切り替える
DOCKERFILE=train.dockerfile
ECR_URI=xxxxxxxxxxxxxxx.dkr.ecr.ap-northeast-1.amazonaws.com/scheduled-sagemaker-app-ecr-image

# Build image
docker build -t "${IMAGE}:${TAG}" -f "${DOCKERFILE}" .

# Docker login
$(aws ecr get-login --no-include-email --region ap-northeast-1)

# Tag that image
docker tag "${IMAGE}:${TAG}" "${ECR_URI}:${TAG}"

# Push
docker push "${ECR_URI}:${TAG}"