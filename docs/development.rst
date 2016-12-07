Development
===========

Setting up a development environment
------------------------------------

If you want to hack on Fava or run the latest development version, this will
get you up and running:

.. code:: bash

    git clone https://github.com/beancount/fava.git
    cd fava
    # using a virtual environment is optional, but recommended
    virtualenv -p python3 venv
    . venv/bin/activate
    make build-js
    pip install --editable .

Note that a development installation Fava requires recent versions of Node.js and
npm, both available on OS X and Linux, but currently not on Cygwin.
To package the development version, you can run ``python setup.py bdist_wheel``
(make sure the ``wheel`` Python package is installed), which will produce a
``.whl`` file in the ``dist`` directory which you can install with ``pip`` on a
different machine.

If you need a newer version of ``beancount`` than you can find on PyPi, you can
run from source like so (more details `here <http://furius.ca/beancount/doc/install>`__):

.. code:: bash

    hg clone https://bitbucket.org/blais/beancount
    cd beancount
    # activate the fava virtual environment
    . venv/bin/activate
    pip install --editable .

Contributions are very welcome, just open a PR on `Github
<https://github.com/beancount/fava/pulls>`__.

Fava is released under the `MIT License
<https://github.com/beancount/fava/blob/master/LICENSE>`__.

API Documentation
-----------------

.. note:: There's no stability guarantee as this is just for internal purposes currently.

fava.application
~~~~~~~~~~~~~~~~

.. automodule:: fava.application

fava.api
~~~~~~~~~

.. automodule:: fava.api

fava.api.budgets
~~~~~~~~~~~~~~~~

.. automodule:: fava.api.budgets

fava.api.charts
~~~~~~~~~~~~~~~

.. automodule:: fava.api.charts

fava.api.fava_options
~~~~~~~~~~~~~~~~~~~~~

.. automodule:: fava.api.fava_options

fava.api.file
~~~~~~~~~~~~~

.. automodule:: fava.api.file

fava.api.filters
~~~~~~~~~~~~~~~~

.. automodule:: fava.api.filters

fava.api.helpers
~~~~~~~~~~~~~~~~

.. automodule:: fava.api.helpers

fava.api.watcher
~~~~~~~~~~~~~~~~

.. automodule:: fava.api.watcher

fava.template_filters
~~~~~~~~~~~~~~~~~~~~~

.. automodule:: fava.template_filters

fava.util
~~~~~~~~~

.. automodule:: fava.util

fava.util.date
~~~~~~~~~~~~~~

.. automodule:: fava.util.date

fava.util.excel
~~~~~~~~~~~~~~~

.. automodule:: fava.util.excel
