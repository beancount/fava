Development
===========

If you want to try out the current `master`-version of Fava and see what we are
working on, check out the online `dev-demo
<https://favadev.pythonanywhere.com>`__ (updated every midnight UTC).

Setting up a development environment
------------------------------------

If you want to hack on Fava or run the latest development version, make sure
you have Python 3 (with `pip`) and Node.js (with `npm`) installed. Then this
will get you up and running:

.. code:: bash

    git clone https://github.com/beancount/fava.git
    cd fava
    # using a virtual environment is optional, but recommended
    virtualenv -p python3 venv
    . venv/bin/activate
    make
    pip install --editable .

You can start Fava in the virtual environment as usual by running ``fava``.

You can run the tests with ``make test`` (requires ``tox``). After any changes
to the Javascript code, you will need to re-run `make`.

If you need a newer version of Beancount than the latest released one, you can
install from source like so (more details `here
<http://furius.ca/beancount/doc/install>`__):

.. code:: bash

    pip install hg+https://bitbucket.org/blais/beancount#egg=beancount

Contributions are very welcome, just open a PR on `GitHub
<https://github.com/beancount/fava/pulls>`__.

Fava is released under the `MIT License
<https://github.com/beancount/fava/blob/master/LICENSE>`__.

API Documentation
-----------------

.. note:: There's no stability guarantee as this is just for internal purposes currently.

fava.application
~~~~~~~~~~~~~~~~

.. automodule:: fava.application

fava.core
~~~~~~~~~

.. automodule:: fava.core

fava.core.attributes
~~~~~~~~~~~~~~~~~~~~

.. automodule:: fava.core.attributes

fava.core.budgets
~~~~~~~~~~~~~~~~~

.. automodule:: fava.core.budgets

fava.core.charts
~~~~~~~~~~~~~~~~

.. automodule:: fava.core.charts

fava.core.fava_options
~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: fava.core.fava_options

fava.core.file
~~~~~~~~~~~~~~

.. automodule:: fava.core.file

fava.core.filters
~~~~~~~~~~~~~~~~~

.. automodule:: fava.core.filters

fava.core.helpers
~~~~~~~~~~~~~~~~~

.. automodule:: fava.core.helpers

fava.core.ingest
~~~~~~~~~~~~~~~~

.. automodule:: fava.core.ingest

fava.core.inventory
~~~~~~~~~~~~~~~~~~~

.. automodule:: fava.core.inventory

fava.core.misc
~~~~~~~~~~~~~~

.. automodule:: fava.core.misc

fava.core.query_shell
~~~~~~~~~~~~~~~~~~~~~

.. automodule:: fava.core.query_shell

fava.core.tree
~~~~~~~~~~~~~~

.. automodule:: fava.core.tree

fava.core.watcher
~~~~~~~~~~~~~~~~~

.. automodule:: fava.core.watcher

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
