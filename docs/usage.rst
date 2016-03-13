Getting Started
===============

If you're new to beancount or double-entry accounting in general, we
recommend `Command-line Accounting in Context
<https://docs.google.com/document/d/1e4Vz3wZB_8-ZcAwIFde8X5CjzKshE4-OXtVVHm4RQ8s/>`__,
a motivational document written by Martin Blais, the author of beancount. 

To learn how to create your beancount file, refer to `Getting Started with
Beancount
<https://docs.google.com/document/d/1P5At-z1sP8rgwYLHso5sEy3u4rMnIUDDgob9Y_BYuWE/>`__
guide. Martin Blais has written a great deal of very detailed documention for
beancount, see the `Beancount Documentation
<https://docs.google.com/document/d/1RaondTJCS_IUPBHFNdT8oqFKJjVJDsfsn6JEjBG04eA>`__
page for an index of the available documentation.

Installation
------------

You will need `Python 3 <https://www.python.org/downloads/>`__ (at least version 3.4).
Then you can use ``pip`` to install fava by running::

    pip3 install beancount-fava

which will also pull in all required dependencies including beancount, if you
don't have it installed already.

Starting fava
-------------

Start fava by running::

    fava ledger.beancount

pointing it to your beancount file -- and visit the web interface at
`http://localhost:5000 <http://localhost:5000>`__.

There are some command-line options available, run ``fava --help`` for an overview.

For more information on fava's features, refer to the help pages that are
available through fava's web-interface.  fava comes with Gmail-style keyboard
shortcuts; press ``?`` to show an overview.
