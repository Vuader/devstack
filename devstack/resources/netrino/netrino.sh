#!/bin/bash

INSTALLED=/installed

if [ ! -f $INSTALLED ]; then
    cd /opt/tachyonic/luxon
    python3 setup.py develop

    cd /opt/tachyonic/psychokinetic
    python3 setup.py develop

    cd /opt/tachyonic/netrino
    python3 setup.py develop

    mkdir /opt/tachyonic/www/netrino
    cd /opt/tachyonic/www/netrino
    luxon -i netrino .
    luxon -d .
    ln -s /opt/tachyonic/www/infinitystone/public.pem .

    rm /etc/nginx/sites-enabled/default
    ln -s /opt/tachyonic/netrino.nginx /etc/nginx/sites-enabled/netrino
    touch $INSTALLED
fi

/etc/init.d/nginx start
