#!/bin/bash

APP_NAME=stuart
REGISTRY=docker.io

VERSION=$1
if [[ -z "$VERSION" ]]; then
  VERSION=$(git describe --tags | sed 's/^v//' )
fi
if [[ -z "$VERSION" ]]; then
  echo "Error: Could not determine the version string." >&2
  exit 1
fi
shift

REVISION="$(git rev-parse HEAD)"

echo "Building version $VERSION..."
echo "  Revision: $REVISION"
docker build \
  -t $APP_NAME:latest \
  --build-arg VERSION="$VERSION" \
  --build-arg REVISION="$REVISION" \
  . "$@"

IMAGE_FULL_NAME="$APP_NAME:$VERSION"
IMAGE_REMOTE_FULL_NAME="$REGISTRY/$IMAGE_FULL_NAME"
docker tag $APP_NAME:latest "$IMAGE_FULL_NAME"
docker tag $APP_NAME:latest "$IMAGE_REMOTE_FULL_NAME"
echo "To push, use: docker push $IMAGE_REMOTE_FULL_NAME"
