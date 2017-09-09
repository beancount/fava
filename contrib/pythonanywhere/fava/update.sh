#!/bin/bash

# Start virtualenv
source /home/fava/.virtualenvs/fava/bin/activate

# Add user bin
export PATH=$PATH:/home/fava/.local/bin

# Updade fava
pip install fava --upgrade
version=$(python -c "import fava; print(fava.__version__)")

# Generate fresh example
date=$(date +%Y-%m-%d)
site='PyPI'
name="option \"title\" \"Example fava @ $version ($date) [$site]\""
bean-example | sed "7s#.*#$name#" > test1.bean
name="option \"title\" \"Example (2) fava @ $version ($date) [$site]\""
bean-example | sed "7s#.*#$name#" > test2.bean
name="option \"title\" \"Example (3)\""
bean-example | sed "7s#.*#$name#" > test3.bean

chmod 400 test1.bean test2.bean test3.bean

# Reload web page
touch /var/www/fava_pythonanywhere_com_wsgi.py
