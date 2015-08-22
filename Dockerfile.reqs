FROM phusion/baseimage:0.9.15

# setting up the baseimage
ENV HOME=/root
RUN rm /etc/my_init.d/*ssh*
RUN rm -r /etc/service/sshd /etc/service/cron /etc/service/syslog-ng

# install nginx
RUN apt-get update; apt-get install -y nginx
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
RUN mkdir /etc/service/nginx
ADD docker/sv-nginx /etc/service/nginx/run
ADD docker/nginx-site.conf /etc/nginx/sites-enabled/default

# install vgmdb requirements
RUN apt-get install -y python-dev python-pip libxml2-dev libxslt1-dev zlib1g-dev git
ADD requirements.txt /requirements.txt
RUN pip install uwsgi
RUN pip install -r /requirements.txt

# other changes
RUN chmod +x /etc/service/*/run

CMD ["/sbin/my_init"]
EXPOSE 80

RUN apt-get autoremove -y python-dev libxml2-dev libxslt1-dev zlib1g-dev
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
