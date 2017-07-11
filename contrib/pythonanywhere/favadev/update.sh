#!/bin/bash

cd
cd fava

UPSTREAM=${1:-'@{u}'}
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse "$UPSTREAM")
BASE=$(git merge-base @ "$UPSTREAM")

if [ $LOCAL = $REMOTE ]; then
    echo "Up-to-date"
elif [ $LOCAL = $BASE ]; then
    # Start virtualenv
    source /home/favadev/.virtualenvs/fava/bin/activate

    # source ~/nvm/nvm.sh
    # nvm alias default v6.6

    # Add user bin
    export PATH=$PATH:/home/fava/.local/bin

    # Update fava
    cd
    cd fava
    git pull

    pwd
    make

    cd
    cd fava
    pip install -e .
    version=`python -c "import fava; print(fava.__version__)"`

    # Generate fresh example
    cd
    date=`date +%Y-%m-%d`
    site='PyPI'
    name="option \"title\" \"Example fava @ $version ($date) [$site]\""
    bean-example | sed "7s#.*#$name#" > test1.bean
    name="option \"title\" \"Example (2) fava @ $version ($date) [$site]\""
    bean-example | sed "7s#.*#$name#" > test2.bean
    name="option \"title\" \"Example (3)\""
    bean-example | sed "7s#.*#$name#" > test3.bean

    # Reload web page
    touch /var/www/favadev_pythonanywhere_com_wsgi.py
elif [ $REMOTE = $BASE ]; then
    echo "Need to push"
else
    echo "Diverged"
fi
