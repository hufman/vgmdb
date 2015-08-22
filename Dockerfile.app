FROM vgmdb_reqs:467586

# install vgmdb software
ADD vgmdb /vgmdb
ADD wsgi.py /wsgi.py
RUN mkdir /www_root
ADD static /www_root/static
RUN mkdir /etc/service/vgmdb
ADD docker/sv-vgmdb /etc/service/vgmdb/run
RUN mkdir /etc/service/celeryd
ADD docker/sv-celeryd /etc/service/celeryd/run

# other changes
RUN chmod +x /etc/service/*/run

CMD ["/sbin/my_init"]
EXPOSE 80
