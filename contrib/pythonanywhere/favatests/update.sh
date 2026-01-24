#!/bin/bash

# Use latest node lts release
source ~/nvm/nvm.sh
nvm use --lts

# Update rustfava
cd ~/rustfava || exit
git pull
make
cd ~ || exit

# Cleanup to stay under pythonanywhere free limits
rm -rf ~/.npm
rm -rf ~/.cache
rm -rf ~/nvm/.cache

# Install rustfava
uv pip install --upgrade ~/rustfava

# Copy example files
rm -f ~/example.beancount ~/budgets-example.beancount ~/huge-example.beancount
cp ~/rustfava/contrib/examples/example.beancount ~/example.beancount
cp ~/rustfava/contrib/examples/budgets-example.beancount ~/budgets-example.beancount
cp ~/rustfava/contrib/examples/huge-example.beancount ~/huge-example.beancount
chmod 400 ~/example.beancount ~/budgets-example.beancount ~/huge-example.beancount

# Reload web page
touch /var/www/rustfavatests_pythonanywhere_com_wsgi.py
