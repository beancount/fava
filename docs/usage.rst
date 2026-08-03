Getting Started
===============

If you're new to Beancount or double-entry accounting in general, we
recommend `Command-line Accounting in Context
<https://docs.google.com/document/d/1e4Vz3wZB_8-ZcAwIFde8X5CjzKshE4-OXtVVHm4RQ8s/>`_,
a motivational document written by Martin Blais, the author of Beancount.

To learn how to create your beancount file, refer to `Getting Started with
Beancount
<https://docs.google.com/document/d/1P5At-z1sP8rgwYLHso5sEy3u4rMnIUDDgob9Y_BYuWE/>`_
guide. Martin Blais has written a great deal of very detailed documentation for
Beancount, see the `Beancount Documentation
<https://docs.google.com/document/d/1RaondTJCS_IUPBHFNdT8oqFKJjVJDsfsn6JEjBG04eA>`_
page for an index of the available documentation.

Installation
------------

Fava is known to run on macOS, Linux, and Windows.  You will need `Python 3
<https://www.python.org/downloads/>`_.  Then you can use ``pip`` to install
Fava or update your existing Installation by running::

    pip install --upgrade fava

which will also pull in all required dependencies including Beancount. If you
do not have Beancount installed already, you might want to have a look at its
`installation instructions
<https://docs.google.com/document/d/1FqyrTPwiHVLyncWTf3v5TcooCu9z5JRX8Nm41lVZi0U>`_.

If you want to export query results to Microsoft Excel or LibreOffice Calc, use
the following command to install the optional dependencies for this feature::

   pip install --upgrade fava[excel]


Installing with uv
------------------

Alternatively, you can install Fava using `uv <https://docs.astral.sh/uv/>`_,
a fast Python package manager. This approach uses a dedicated folder for Fava
and a so-called virtual environment, keeping Fava and its dependencies isolated
from other Python projects on your system.

First, `install uv <https://docs.astral.sh/uv/getting-started/installation/>`_
if you haven't already. Then create a project folder and install Fava::

    uv init --package ~/personal-ledger
    cd ~/personal-ledger
    uv add fava

The ``--package`` option sets the folder up as a Python package, so you can
write your own Beancount plugins and importers in ``src/personal_ledger`` and
use them from your ledger, for example with ``plugin "personal_ledger"``. See
`contrib/personal_ledger
<https://github.com/beancount/fava/tree/main/contrib/personal_ledger>`_ for an
example.

To start Fava, either activate the virtual environment at ``.venv`` or run
Fava directly without activation, passing the path to your Beancount file (here
assumed to be in the project folder)::

    uv run fava ledger.beancount

To update Fava and the other dependencies later::

    uv lock --upgrade
    uv sync


Starting Fava
-------------

After installing Fava, you can start it by running::

    fava ledger.beancount

pointing it to your Beancount file -- and visit the web interface at
`http://localhost:5000 <http://localhost:5000>`_.

There are some command-line options available, run ``fava --help`` for an overview.

For more information on Fava's features, refer to the help pages that are
available through Fava's web-interface.  Fava comes with Gmail-style keyboard
shortcuts; press ``?`` to show an overview.
