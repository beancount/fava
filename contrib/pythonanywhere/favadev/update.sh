#!/bin/bash

cd ~/fava || exit
git fetch
git reset --hard origin/main

source /home/favadev/.virtualenvs/fava/bin/activate

# Update fava
make
pip install -e ~/fava

# Copy example files
rm -f ~/example.beancount ~/budgets-example.beancount ~/huge-example.beancount
cp contrib/examples/example.beancount ~/example.beancount
cp contrib/examples/budgets-example.beancount ~/budgets-example.beancount
cp contrib/examples/huge-example.beancount ~/huge-example.beancount
chmod 400 ~/example.beancount ~/budgets-example.beancount ~/huge-example.beancount

# Reload web page
touch /var/www/favadev_pythonanywhere_com_wsgi.py
