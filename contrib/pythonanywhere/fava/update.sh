#!/bin/bash

# Start virtualenv
source ~/.virtualenvs/fava/bin/activate

# Update fava
pip install fava --upgrade

curl -o ~/example.beancount https://raw.githubusercontent.com/beancount/fava/master/contrib/examples/example.beancount
curl -o ~/budgets-example.beancount https://raw.githubusercontent.com/beancount/fava/master/contrib/examples/budgets-example.beancount
curl -o ~/huge-example.beancount https://raw.githubusercontent.com/beancount/fava/master/contrib/examples/huge-example.beancount

chmod 400 ~/example.beancount
chmod 400 ~/budgets-example.beancount
chmod 400 ~/huge-example.beancount

# Reload web page
touch /var/www/fava_pythonanywhere_com_wsgi.py
