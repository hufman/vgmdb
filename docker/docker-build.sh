#!/bin/sh
# Build the requirements image, and then build an app image on top

MY_PATH=`readlink -f "$0"`
DOCKER_DIR=`dirname "$MY_PATH"`
PROJECT_DIR=`dirname "$DOCKER_DIR"`

PROJECT=vgmdb
[ -n "$REV" ] || REV=latest
get_reqs_id() {
  md5sum "$PROJECT_DIR"/requirements.txt | cut -c1-6
}

# Build the requirements image, if necessary
REQS_ID=`get_reqs_id`
REQS_IMAGE=${PROJECT}_reqs:$REQS_ID
docker inspect $REQS_IMAGE > /dev/null 2>&1||
  docker/docker-compile.pl -t "$REQS_IMAGE" -f "$PROJECT_DIR"/Dockerfile.reqs

# Build the app image on top
sed -i '/^FROM / s/:.*/:'"$REQS_ID"'/' "$PROJECT_DIR"/Dockerfile.app
docker/docker-compile.pl -t "$PROJECT:$REV" -f "$PROJECT_DIR"/Dockerfile.app
