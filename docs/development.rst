Development
===========

Setting up a development environment
------------------------------------

If you want to hack on Fava or run the latest development version, make sure
you have recent enough versions of the following installed (ideally with your
system package manager):

- `Python 3`_ - with `pip` (at least v21.3), to install the Fava Python package,
- `Node.js`_ - with `npm`, to install the Javascript dependencies,
- `tox`_ - to run the Python tests,
- `pre-commit`_ - to lint changes with a git pre-commit hook.

.. _Python 3: https://www.python.org/
.. _Node.js: https://nodejs.org/
.. _tox: https://tox.wiki/en/latest/
.. _pre-commit: https://pre-commit.com/

Then this will get you up and running:

.. code:: bash

    git clone https://github.com/beancount/fava.git
    cd fava
    # using a virtual environment is optional, but recommended
    python -m venv venv
    . venv/bin/activate
    make
    pre-commit install  # add a git pre-commit hook to run linters
    pip install --editable .

You can start Fava in the virtual environment as usual by running ``fava``.
Running in debug mode with ``fava --debug`` is useful for development.

You can run the tests with ``make test``. After any changes to the Javascript
code, you will need to re-run `make`, or, if you are working on the frontend
code, running ``npm run dev`` in the ``frontend`` folder will watch for file
changes and rebuild the Javascript bundle continuously.

If you need a newer version of Beancount than the latest released one, you can
install from source like so (more details `here
<http://furius.ca/beancount/doc/install>`_):

.. code:: bash

    pip install hg+https://bitbucket.org/blais/beancount#egg=beancount

Contributions are very welcome, just open a PR on `GitHub`_.

Fava is released under the `MIT License`_.

.. _GitHub: https://github.com/beancount/fava/pulls
.. _MIT License: https://github.com/beancount/fava/blob/main/LICENSE

