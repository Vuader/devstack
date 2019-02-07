#!/bin/bash

INSTALLED=/installed

if [ ! -f $INSTALLED ]; then
    cd /opt/tachyonic/luxon
    python3 setup.py develop

    cd /opt/tachyonic/psychokinetic
    python3 setup.py develop

    cd /opt/tachyonic/subscriber
    python3 setup.py develop

    mkdir /opt/tachyonic/www/subscriber
    cd /opt/tachyonic/www/subscriber
    luxon -i subscriber .
    luxon -d .
    subscriber radius setup
    ln -s /opt/tachyonic/www/infinitystone/public.pem .

    rm /etc/nginx/sites-enabled/default
    ln -s /opt/tachyonic/subscriber.nginx /etc/nginx/sites-enabled/subscriber
    touch $INSTALLED
fi

/etc/init.d/nginx start
/etc/init.d/freeradius start
