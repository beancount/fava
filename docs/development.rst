Development
===========

If you want to hack on fava or run the latest development version, this will
get you up and running:

.. code:: bash

    git clone https://github.com/aumayr/fava.git
    cd fava
    # using a virtual environment is optional, but recommended
    virtualenv -p python3 venv
    . venv/bin/activate
    make build-js
    pip install --editable .

Note that a development installation fava requires recent versions of Node.js and
npm, both available on OS X and Linux, but currently not on Cygwin.

Contributions are very welcome, just open a PR on `Github <https://github.com/aumayr/fava/pulls>`__.

Fava is released under the `MIT License <https://github.com/aumayr/fava/blob/master/LICENSE>`__.
