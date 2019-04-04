#!/bin/bash

INSTALLED=/installed

if [ ! -f $INSTALLED ]; then
    useradd tachyonic -m -U -d /var/tachyonic
    apt-get update
    apt-get --assume-yes upgrade
    apt-get --assume-yes autoremove
    apt-get --assume-yes install libcurl4-openssl-dev libssl-dev libffi-dev
    apt-get --assume-yes install python3 python3-pip
    apt-get --assume-yes install mariadb-client sqlite3
    apt-get --assume-yes install gunicorn3 nginx 
    apt-get --assume-yes install git ansible
    apt-get --assume-yes install wget curl screen vim htop
    apt-get --assume-yes install openssh-client inetutils-telnet ftp
    apt-get --assume-yes install iputils-ping net-tools tcpdump
    export DEBIAN_FRONTEND=noninteractive && apt-get --assume-yes install tzdata
    export tz=`wget -qO - http://geoip.ubuntu.com/lookup | sed -n -e 's/.*<TimeZone>\(.*\)<\/TimeZone>.*/\1/p'` &&  dpkg-reconfigure -f noninteractive tzdata
    apt-get clean

    cd /opt/tachyonic/luxon
    python3 setup.py develop

    cd /opt/tachyonic/psychokinetic
    python3 setup.py develop

    cd /opt/tachyonic/infinitystone
    python3 setup.py develop

    cd /opt/tachyonic/photonic
    python3 setup.py develop

    # External Modules...
    cd /opt/tachyonic/calabiyau
    python3 setup.py develop

	cd /opt/tachyonic/netrino
    python3 setup.py develop

    # Continued...

    mkdir /opt/tachyonic/www/photonic
    cd /opt/tachyonic/www/photonic
    luxon -i photonic .
    luxon -i infinitystone.ui .
    luxon -i calabiyau.ui .
    luxon -i netrino.ui .
    ln -s /opt/tachyonic/www/infinitystone/public.pem .

    rm /etc/nginx/sites-enabled/default
    ln -s /opt/tachyonic/photonic.nginx /etc/nginx/sites-enabled/photonic
    touch /var/log/gunicorn.log
    touch $INSTALLED
fi

/etc/init.d/nginx start

cd /opt/tachyonic/www/photonic

gunicorn3 --capture-output --error-logfile /var/log/gunicorn.log --daemon --workers 2 --threads 4 --bind unix:wsgi.sock wsgi:application

tail -f /var/log/gunicorn.log
