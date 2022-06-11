
get_reqs_id() {
  MY_PATH=`readlink -f "$BASH_SOURCE"`
  DOCKER_DIR=`dirname "$MY_PATH"`
  PROJECT_DIR=`dirname "$DOCKER_DIR"`
  cat "$PROJECT_DIR"/requirements.txt \
      "$PROJECT_DIR"/Dockerfile.reqs \
      "$PROJECT_DIR"/docker/nginx-site.conf \
      "$PROJECT_DIR"/docker/sv-nginx \
  | md5sum | cut -c1-6
}

