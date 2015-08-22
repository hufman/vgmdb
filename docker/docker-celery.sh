#!/bin/sh
# Stacks on top of a given docker image
# to disable the vgmdb web interface
# Makes a new image named $1_celery
IMAGE="$1"
[ -z "$IMAGE" ] && exit
docker inspect "$IMAGE" > /dev/null || exit
Cmd=`docker inspect -f '[{{ range .Config.Cmd }}"{{ . }}"{{ end }}]' "$IMAGE"`
Ports=`docker inspect -f '[{{ range $key,$value := .Config.ExposedPorts }}"{{ $key }}"{{end}}]' "$IMAGE"`

[ -e cid.celery ] && rm cid.celery || true

docker run --cidfile=cid.celery --entrypoint=/bin/sh "$IMAGE" -c "rm -r /etc/service/vgmdb/; rm -r /etc/service/nginx/"

NEWIMAGE=`echo "${IMAGE}" | sed -E 's/(:|$)/_celery\1/'`
#docker commit --change="ENTRYPOINT" --change="CMD=/sbin/my_init" `cat cid` "${NEWIMAGE}
docker commit --run='{"Cmd":'$Cmd',"Entrypoint":[]}' `cat cid.celery` "${NEWIMAGE}"
[ -e cid.celery ] && rm cid.celery || true
