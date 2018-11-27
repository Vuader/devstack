#!/bin/bash

cd /opt/tachyonic/luxon
python3 setup.py develop

cd /opt/tachyonic/psychokinetic
python3 setup.py develop

cd /opt/tachyonic/infinitystone
python3 setup.py develop

cd /opt/tachyonic/photonic
python3 setup.py develop

# External Modules...
cd /opt/tachyonic/tradius
python3 setup.py develop

# Continued...

mkdir /opt/tachyonic/www/photonic
cd /opt/tachyonic/www/photonic
luxon -i photonic .
luxon -i infinitystone.ui .
luxon -i tradius.ui .
ln -s /opt/tachyonic/www/infinitystone/public.pem .

rm /etc/nginx/sites-enabled/default
ln -s /opt/tachyonic/photonic.nginx /etc/nginx/sites-enabled/photonic

/etc/init.d/nginx start

