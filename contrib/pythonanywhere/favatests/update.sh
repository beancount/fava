#!/bin/bash

# Use latest node lts release
source ~/nvm/nvm.sh
nvm use --lts

# Update fava
cd ~/fava || exit
git pull
make
cd ~ || exit

# Cleanup to stay under pythonanywhere free limits
rm -rf ~/.npm
rm -rf ~/.cache
rm -rf ~/nvm/.cache

# Install fava
pip install --upgrade --upgrade-strategy eager ~/fava

# Copy example files
rm -f ~/example.beancount ~/budgets-example.beancount ~/huge-example.beancount
cp ~/fava/contrib/examples/example.beancount ~/example.beancount
cp ~/fava/contrib/examples/budgets-example.beancount ~/budgets-example.beancount
cp ~/fava/contrib/examples/huge-example.beancount ~/huge-example.beancount
chmod 400 ~/example.beancount ~/budgets-example.beancount ~/huge-example.beancount

# Reload web page
touch /var/www/favatests_eu_pythonanywhere_com_wsgi.py
