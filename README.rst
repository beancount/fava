fava
====

.. image:: https://img.shields.io/badge/plaintextaccounting.org-beancount-red.svg
   :target: http://plaintextaccounting.org
.. image:: https://img.shields.io/pypi/l/beancount-fava.svg
   :target: https://pypi.python.org/pypi/beancount-fava
.. image:: https://img.shields.io/pypi/v/beancount-fava.svg
   :target: https://pypi.python.org/pypi/beancount-fava
.. image:: https://img.shields.io/pypi/dm/beancount-fava.svg
   :target: https://pypi.python.org/pypi/beancount-fava
.. image:: https://img.shields.io/github/commits-since/aumayr/fava/v0.2.6.svg
   :target: https://github.com/aumayr/fava/compare/v0.2.6...master
.. image:: https://img.shields.io/travis/aumayr/fava.svg
   :target: https://travis-ci.org/aumayr/fava?branch=master

fava is a web interface for the double-entry bookkeeping software `beancount
<http://furius.ca/beancount/>`__ with a focus on features and usability.

You can try out an online `demo <http://fava.pythonanywhere.com>`__ and there
are some more screenshots `here
<https://aumayr.github.io/fava/screenshots.html>`__.

The `Getting Started
<https://aumayr.github.io/fava/usage.html>`__ guide details the installation and
how to get started with beancount.

If you are familiar with beancount, you can get started with fava::

    pip3 install beancount-fava
    fava ledger.beancount

and visit the web interface at `http://localhost:5000
<http://localhost:5000>`__.

Development
-----------

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

--------------

**Caution**: Consider this *beta*-software. Contributions are very
welcome :-)
