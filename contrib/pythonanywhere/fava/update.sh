#!/bin/bash

# Install uv, which we use for the next steps
pip install --upgrade uv

# Create venv and install / update Rustfava
uv venv --allow-existing
uv pip install rustfava --upgrade

# Update example files
rm -f ~/*.beancount
curl -o ~/example.beancount https://raw.githubusercontent.com/rustledger/rustfava/main/contrib/examples/example.beancount
curl -o ~/budgets-example.beancount https://raw.githubusercontent.com/rustledger/rustfava/main/contrib/examples/budgets-example.beancount
curl -o ~/huge-example.beancount https://raw.githubusercontent.com/rustledger/rustfava/main/contrib/examples/huge-example.beancount
chmod 400 ~/*.beancount

# Reload web page
touch /var/www/rustfava_pythonanywhere_com_wsgi.py
