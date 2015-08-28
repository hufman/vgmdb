#!/bin/sh
# Stacks on top of a given docker image
# to disable the vgmdb celery workers
# Makes a new image named $1_web
IMAGE="$1"
[ -z "$IMAGE" ] && exit
docker inspect "$IMAGE" > /dev/null || exit
Cmd=`docker inspect -f '[{{ range .Config.Cmd }}"{{ . }}"{{ end }}]' "$IMAGE"`
Ports=`docker inspect -f '[{{ range $key,$value := .Config.ExposedPorts }}"{{ $key }}"{{end}}]' "$IMAGE"`

[ -e cid.web ] && rm cid.web || true

docker run --cidfile=cid.web --entrypoint=/bin/sh "$IMAGE" -c "rm -r /etc/service/celery*/"

NEWIMAGE=`echo "${IMAGE}" | sed -E 's/(:|$)/_web\1/'`
#docker commit --change="ENTRYPOINT" --change="CMD=/sbin/my_init" `cat cid.web` "${NEWIMAGE}
docker commit --run='{"Cmd":'$Cmd',"PortSpecs":'$Ports',"Entrypoint":[]}' `cat cid.web` "${NEWIMAGE}"
[ -e cid.web ] && rm cid.web || true
