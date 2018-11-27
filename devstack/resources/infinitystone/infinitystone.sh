#!/bin/bash

cd /opt/tachyonic/luxon
python3 setup.py develop

cd /opt/tachyonic/psychokinetic
python3 setup.py develop

cd /opt/tachyonic/infinitystone
python3 setup.py develop

mkdir /opt/tachyonic/www/infinitystone
cd /opt/tachyonic/www/infinitystone
luxon -i infinitystone .
luxon -d .
luxon -r .
luxon -k .

rm /etc/nginx/sites-enabled/default
ln -s /opt/tachyonic/infinitystone.nginx /etc/nginx/sites-enabled/infinitystone

/etc/init.d/nginx start

