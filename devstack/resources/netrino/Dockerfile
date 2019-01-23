FROM ubuntu
RUN apt-get update
RUN apt-get --assume-yes upgrade
RUN apt-get --assume-yes autoremove

RUN apt-get --assume-yes install libcurl4-openssl-dev libssl-dev libffi-dev
RUN apt-get --assume-yes install python3
RUN apt-get --assume-yes install python3-pip
RUN apt-get --assume-yes install git
RUN apt-get --assume-yes install sqlite3
RUN apt-get --assume-yes install mariadb-client
RUN apt-get --assume-yes install freeradius-mysql

RUN apt-get --assume-yes install gunicorn3
RUN apt-get --assume-yes install nginx

# @Vuader: There is no neat cross-platform way to link host tz to container
# (https://forums.docker.com/t/synchronize-timezone-from-host-to-container/39116)
# Just this hack:
RUN apt-get --assume-yes install wget
RUN export DEBIAN_FRONTEND=noninteractive && apt-get --assume-yes install tzdata
RUN export tz=`wget -qO - http://geoip.ubuntu.com/lookup | sed -n -e 's/.*<TimeZone>\(.*\)<\/TimeZone>.*/\1/p'` &&  dpkg-reconfigure -f noninteractive tzdata

# @Vuader: The following 3 are not nessecary, but I enjoy them:
RUN apt-get --assume-yes install ansible
RUN apt-get --assume-yes install screen
RUN apt-get --assume-yes install vim

RUN apt-get clean

CMD /bin/bash /opt/tachyonic/netrino.sh && cd /opt/tachyonic/www/netrino && gunicorn3 --workers 10 --bind unix:wsgi.sock wsgi:application
