FROM vgmdb_reqs:36a64e

# install vgmdb software
ADD vgmdb /vgmdb
ADD wsgi.py /wsgi.py
RUN mkdir /www_root
ADD static /www_root/static
ADD raml /www_root/raml
ADD schema /www_root/schema
RUN mkdir /etc/service/vgmdb
ADD docker/sv-vgmdb /etc/service/vgmdb/run
RUN mkdir /etc/service/celery-priority
ADD docker/sv-celery-priority /etc/service/celery-priority/run
RUN mkdir /etc/service/celery-background
ADD docker/sv-celery-background /etc/service/celery-background/run

# other changes
RUN chmod +x /etc/service/*/run

CMD ["/sbin/my_init"]
EXPOSE 80
