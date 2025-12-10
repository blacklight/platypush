#!/bin/sh

[ -z "$DOCKER_USER" ] && echo "Please set the DOCKER_USER environment variable" && exit 1
[ -z "$DOCKER_PASS" ] && echo "Please set the DOCKER_PASS environment variable" && exit 1

export VERSION=$(grep current_version pyproject.toml | sed -r -e "s/.*=\s*['\"]?([^'\"]+)['\"]?\s*$/\1/")
export REGISTRY_ENDPOINT="${REGISTRY_ENDPOINT:-quay.io}"
export IMAGE_NAME="$REGISTRY_ENDPOINT/$DOCKER_USER/platypush"

# Log in to the registry
docker login "$REGISTRY_ENDPOINT" -u "$DOCKER_USER" -p "$DOCKER_PASS"

# Required for multi-platform builds
docker buildx create --name=multiarch --driver=docker-container

# Pull the latest Alpine image
docker pull alpine:latest

# Build and publish the images
docker buildx build \
  -f Dockerfile.alpine \
  -t "$IMAGE_NAME:$VERSION" \
  -t "$IMAGE_NAME:latest" \
  --platform linux/amd64,linux/arm64,linux/arm/v7 \
  --builder multiarch \
  --push .

# Clean up
docker buildx rm multiarch
