#!/bin/bash

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

mkdir -p instance
export STUART_SECRET_KEY=''
if [[ -f "instance/vars.sh" ]] ; then
  source instance/vars.sh
fi

STUART_VERSION="$VERSION"
STUART_REVISION="$REVISION"

python stuart.py \
  --debug \
  --db-uri "sqlite:///$PWD/instance/stuart.sqlite" \
  --secret-key "$STUART_SECRET_KEY" \
  "$@"
