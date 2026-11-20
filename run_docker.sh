#!/bin/bash

APP_NAME=stuart

VERSION=$1
if [[ -z "$VERSION" ]]; then
  VERSION=$(git describe --tags | sed 's/^v//' )
fi
if [[ -z "$VERSION" ]]; then
  echo "Error: Could not determine the version string." >&2
  exit 1
fi
shift

echo "Running version $VERSION..."

export STUART_SECRET_KEY=''
if [[ -f "instance/vars.sh" ]] ; then
  source instance/vars.sh
fi

docker run --rm -it \
  -p 8080:8080 \
  -e STUART_DB_URI="sqlite:////host/instance/stuart.sqlite" \
  -e STUART_SECRET_KEY="$STUART_SECRET_KEY" \
  -v "$PWD:/host" \
  --add-host=host.docker.internal:host-gateway \
  "$APP_NAME:$VERSION" "$@"
