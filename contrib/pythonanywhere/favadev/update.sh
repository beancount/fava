#!/bin/bash

cd ~/fava || exit

UPSTREAM=${1:-'@{u}'}
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse "$UPSTREAM")
BASE=$(git merge-base @ "$UPSTREAM")

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "Up-to-date"
elif [ "$LOCAL" = "$BASE" ]; then
    # Start virtualenv
    source /home/favadev/.virtualenvs/fava/bin/activate

    # source ~/nvm/nvm.sh
    # nvm alias default v6.6

    # Add user bin
    export PATH=$PATH:/home/fava/.local/bin

    # Update fava
    cd ~/fava || exit
    git pull
    make

    pip install -e ~/fava

    cp ~/fava/contrib/examples/example.beancount ~/example.beancount
    cp ~/fava/contrib/examples/budgets-example.beancount ~/budgets-example.beancount
    cp ~/fava/contrib/examples/huge-example.beancount ~/huge-example.beancount

    chmod 400 ~/example.beancount
    chmod 400 ~/budgets-example.beancount
    chmod 400 ~/huge-example.beancount

    # Reload web page
    touch /var/www/favadev_pythonanywhere_com_wsgi.py
elif [ "$REMOTE" = "$BASE" ]; then
    echo "Need to push"
else
    echo "Diverged"
fi
