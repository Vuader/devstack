#!/bin/bash

INSTALLED=/installed

if [ ! -f $INSTALLED ]; then
    cd /opt/tachyonic/luxon
    python3 setup.py develop

    cd /opt/tachyonic/psychokinetic
    python3 setup.py develop

    cd /opt/tachyonic/infinitystone
    python3 setup.py develop

    cd /opt/tachyonic/photonic
    python3 setup.py develop

    # External Modules...
    cd /opt/tachyonic/subscriber
    python3 setup.py develop

	cd /opt/tachyonic/netrino
    python3 setup.py develop

    # Continued...

    mkdir /opt/tachyonic/www/photonic
    cd /opt/tachyonic/www/photonic
    luxon -i photonic .
    luxon -i infinitystone.ui .
    luxon -i subscriber.ui .
    luxon -i netrino.ui .
    ln -s /opt/tachyonic/www/infinitystone/public.pem .

    rm /etc/nginx/sites-enabled/default
    ln -s /opt/tachyonic/photonic.nginx /etc/nginx/sites-enabled/photonic
    touch $INSTALLED
fi

/etc/init.d/nginx start

