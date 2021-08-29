#!/bin/bash

# Start virtualenv
virtualenv ~/venv --python=python3.8
source ~/venv/bin/activate

# Update fava
pip install fava --upgrade

rm -f ~/example.beancount ~/budgets-example.beancount ~/huge-example.beancount
curl -o ~/example.beancount https://raw.githubusercontent.com/beancount/fava/main/contrib/examples/example.beancount
curl -o ~/budgets-example.beancount https://raw.githubusercontent.com/beancount/fava/main/contrib/examples/budgets-example.beancount
curl -o ~/huge-example.beancount https://raw.githubusercontent.com/beancount/fava/main/contrib/examples/huge-example.beancount

chmod 400 ~/example.beancount
chmod 400 ~/budgets-example.beancount
chmod 400 ~/huge-example.beancount

# Reload web page
touch /var/www/fava_pythonanywhere_com_wsgi.py
