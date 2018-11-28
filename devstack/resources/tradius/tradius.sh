#!/bin/bash

INSTALLED=/installed

if [ ! -f $INSTALLED ]; then
    cd /opt/tachyonic/luxon
    python3 setup.py develop

    cd /opt/tachyonic/psychokinetic
    python3 setup.py develop

    cd /opt/tachyonic/tradius
    python3 setup.py develop

    mkdir /opt/tachyonic/www/tradius
    cd /opt/tachyonic/www/tradius
    luxon -i tradius .
    luxon -d .
    ln -s /opt/tachyonic/www/infinitystone/public.pem .

    rm /etc/nginx/sites-enabled/default
    ln -s /opt/tachyonic/tradius.nginx /etc/nginx/sites-enabled/tradius
    touch $INSTALLED
fi

/etc/init.d/nginx start
