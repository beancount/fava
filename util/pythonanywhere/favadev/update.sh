#!/bin/bash

# Add user bin
export PATH=$PATH:/home/favadev/.local/bin

# Update beancount
# pushd ~/beancount
# hg pull
# hg up
# python3 setup.py install --user
# popd

pushd ~/fava
git pull
# python3 setup.py install --user
# pip3 install --user beancount-fava
make build-js
pip3 install --editable .
version=`vcprompt -f "%b:%r"`
popd

# Update default config
cp ~/fava/fava/default-settings.conf /home/favadev/

# Generate fresh example
date=`date +%Y-%m-%d`
site='github.com/aumayr/fava'
name="option \"title\" \"Example beancount-fava @ $version ($date) [$site]\""
bean-example | sed "7s#.*#$name#" > test.bean

# Reload web page
touch /var/www/favadev_pythonanywhere_com_wsgi.py
