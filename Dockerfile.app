FROM vgmdb_reqs:fafeba09eb80

# install vgmdb software
ADD vgmdb /vgmdb
RUN touch /vgmdb/local_settings.py
ADD run.py /run.py
ADD wsgi.py /wsgi.py
RUN mkdir /www_root
ADD static /www_root/static
ADD raml /www_root/raml
ADD schema /www_root/schema
ADD scripts /scripts
ADD static/robots.txt /www_root/robots.txt
RUN mkdir /etc/service/vgmdb
ADD docker/sv-vgmdb /etc/service/vgmdb/run
RUN mkdir /etc/service/celery-priority
ADD docker/sv-celery-priority /etc/service/celery-priority/run
RUN mkdir /etc/service/celery-background
ADD docker/sv-celery-background /etc/service/celery-background/run
RUN ln -s /vgmdb /venv/lib/python3.11/site-packages/vgmdb

# other changes
RUN chmod +x /etc/service/*/run

CMD ["/sbin/my_init"]
EXPOSE 80
