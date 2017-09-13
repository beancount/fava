#!/bin/bash

cd ~/fava || exit
git fetch
git reset --hard origin/master

# Start virtualenv
source /home/favadev/.virtualenvs/fava/bin/activate

# source ~/nvm/nvm.sh
# nvm alias default v6.6

# Install Fava.
make
pip install -e .

# Copy example files.
cp contrib/examples/example.beancount ~/example.beancount
cp contrib/examples/budgets-example.beancount ~/budgets-example.beancount
cp contrib/examples/huge-example.beancount ~/huge-example.beancount

chmod 400 ~/example.beancount
chmod 400 ~/budgets-example.beancount
chmod 400 ~/huge-example.beancount

# Reload web page
touch /var/www/favadev_pythonanywhere_com_wsgi.py
