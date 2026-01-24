Development
===========

Setting up a development environment
------------------------------------

If you want to hack on Rustfava or run the latest development version, make sure
you have recent enough versions of the following installed (ideally with your
system package manager):

- `Python 3`_ - as Rustfava is written in Python,
- `Node.js`_ - with `npm`, to build the frontend,
- Make - to run various build / lint/ test targets,
- `uv`_ - to install the development environment and run scripts.

.. _Python 3: https://www.python.org/
.. _Node.js: https://nodejs.org/
.. _uv: https://docs.astral.sh/uv/

Then this will get you up and running:

.. code:: bash

    git clone https://github.com/rustledger/rustfava.git
    cd rustfava
    # setup a virtual environment (at .venv) and install Rustfava and development
    # dependencies into it:
    make dev

You can start Rustfava in the virtual environment as usual by running ``rustfava``.
Running in debug mode with ``rustfava --debug`` is useful for development.

You can run the tests with ``make test`` and the linters by running ``make
lint``. There are further make targets defined, see the `Makefile` for details.
After any changes to the Javascript code, you will need to re-build the
frontend, which you can do by running ``make``. If you are working on the
frontend code, running ``npm run dev`` in the ``frontend`` folder will watch
for file changes and rebuild the Javascript bundle continuously.

Contributions are very welcome, just open a PR on `GitHub`_.

Rustfava is released under the `MIT License`_.

.. _GitHub: https://github.com/rustledger/rustfava/pulls
.. _MIT License: https://github.com/rustledger/rustfava/blob/main/LICENSE

