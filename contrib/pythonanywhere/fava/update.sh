#!/bin/bash

# Install uv, which we use for the next steps
pip install --upgrade uv

# Create venv and install / update Fava
uv venv --allow-existing
uv pip install fava --upgrade

# Update example files
rm -f ~/*.beancount
curl -o ~/example.beancount https://raw.githubusercontent.com/beancount/fava/main/contrib/examples/example.beancount
curl -o ~/budgets-example.beancount https://raw.githubusercontent.com/beancount/fava/main/contrib/examples/budgets-example.beancount
curl -o ~/huge-example.beancount https://raw.githubusercontent.com/beancount/fava/main/contrib/examples/huge-example.beancount
chmod 400 ~/*.beancount

# Reload web page
touch /var/www/fava_pythonanywhere_com_wsgi.py
