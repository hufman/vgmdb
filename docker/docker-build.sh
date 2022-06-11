#!/bin/sh
# Build the requirements image, and then build an app image on top

MY_PATH=`readlink -f "$0"`
DOCKER_DIR=`dirname "$MY_PATH"`
PROJECT_DIR=`dirname "$DOCKER_DIR"`
[ -n "$PLATFORM" ] || PLATFORM="amd64"

PROJECT=vgmdb
[ -n "$REV" ] || REV=latest

. ${DOCKER_DIR}/_inc.sh

# Build the requirements image, if necessary
REQS_ID=`get_reqs_id`-$PLATFORM
REQS_IMAGE=${PROJECT}_reqs:$REQS_ID
docker inspect $REQS_IMAGE > /dev/null 2>&1 ||
  docker/docker-compile.pl -p "$PLATFORM" -t "$REQS_IMAGE" -f "$PROJECT_DIR"/Dockerfile.reqs

# Build the app image on top
sed -i '/^FROM / s/:.*/:'"$REQS_ID"'/' "$PROJECT_DIR"/Dockerfile.app
docker/docker-compile.pl -p "$PLATFORM" -t "$PROJECT:$REV-$PLATFORM" -f "$PROJECT_DIR"/Dockerfile.app
