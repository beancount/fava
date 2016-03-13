Development
===========

If you want to hack on ``fava``, this will get you up and running:

.. code:: bash

    git clone https://github.com/aumayr/fava.git
    cd fava
    # using a virtual environment is optional, but recommended
    virtualenv -p python3 venv
    . venv/bin/activate
    make build-js
    pip install --editable .

Note that you'll need to have the newest version of ``npm`` and
``NodeJS`` installed to build the JavaScript and CSS files.

Contributions are very welcome, just open a PR on `Github <https://github.com/aumayr/fava/pulls>`__.

fava is released under the `MIT License <https://github.com/aumayr/fava/blob/master/LICENSE>`__.
