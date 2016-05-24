#!/bin/bash

# Add user bin
export PATH=$PATH:/home/fava/.local/bin

# Updade fava
pip3 install --user beancount-fava --upgrade
version=`python3 -c "import fava; print(fava.__version__)"`

# Update default config
cp ~/fava/fava/default-settings.conf /home/fava/

# Generate fresh example
date=`date +%Y-%m-%d`
site='PyPI'
name="option \"title\" \"Example beancount-fava @ $version ($date) [$site]\""
bean-example | sed "7s#.*#$name#" > test1.bean
name="option \"title\" \"Example (2) beancount-fava @ $version ($date) [$site]\""
bean-example | sed "7s#.*#$name#" > test2.bean

# Reload web page
touch /var/www/fava_pythonanywhere_com_wsgi.py
