#!/bin/sh

export VERSION=$(grep current_version pyproject.toml | sed -r -e "s/.*=\s*['\"]?([^'\"]+)['\"]?\s*$/\1/")
export IMAGE_NAME="$REGISTRY_ENDPOINT/$DOCKER_USER/platypush"

docker login "$REGISTRY_ENDPOINT" -u "$DOCKER_USER" -p "$DOCKER_PASS"
docker build -f Dockerfile.alpine -t "$IMAGE_NAME:$VERSION" .
docker tag "$IMAGE_NAME:$VERSION" "$IMAGE_NAME:latest"

docker push "$IMAGE_NAME:$VERSION"
docker push "$IMAGE_NAME:latest"
