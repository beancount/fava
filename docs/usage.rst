Getting Started
===============

If you're new to Beancount or double-entry accounting in general, we
recommend `Command-line Accounting in Context
<https://docs.google.com/document/d/1e4Vz3wZB_8-ZcAwIFde8X5CjzKshE4-OXtVVHm4RQ8s/>`__,
a motivational document written by Martin Blais, the author of Beancount.

To learn how to create your beancount file, refer to `Getting Started with
Beancount
<https://docs.google.com/document/d/1P5At-z1sP8rgwYLHso5sEy3u4rMnIUDDgob9Y_BYuWE/>`__
guide. Martin Blais has written a great deal of very detailed documention for
Beancount, see the `Beancount Documentation
<https://docs.google.com/document/d/1RaondTJCS_IUPBHFNdT8oqFKJjVJDsfsn6JEjBG04eA>`__
page for an index of the available documentation.

Installation
------------

There are two ways to run Fava. You can start the Fava process in a terminal
and access it with you default web browser. Alternatively there is a GUI
version which bundles Fava with a browser basically.  If you know your way
around the terminal, installation via ``pip`` (see below) is recommended,
otherwise, head to the `Releases
<https://github.com/beancount/fava/releases>`__ page on Github and download the
latest GUI version for your platform: ``AppImage`` on Linux (the file needs to
be made executable after downloading) or ``dmg`` for MacOS. There is currently no
build of the GUI for Windows.

Fava is known to run on MacOS, Linux, and Windows (with Cygwin).  You will need
`Python 3 <https://www.python.org/downloads/>`__ (at least version 3.4).  Then
you can use ``pip`` to install Fava by running::

    pip3 install fava

which will also pull in all required dependencies including Beancount, if you
don't have it installed already.

If you want to export query results to Microsoft Excel or LibreOffice Calc, use
the following command to install the optional dependencies for this feature::

   pip3 install fava[excel]


Starting Fava
-------------

If you installed Fava using ``pip``, start it by running::

    fava ledger.beancount

pointing it to your Beancount file -- and visit the web interface at
`http://localhost:5000 <http://localhost:5000>`__.

There are some command-line options available, run ``fava --help`` for an overview.

For more information on Fava's features, refer to the help pages that are
available through Fava's web-interface.  Fava comes with Gmail-style keyboard
shortcuts; press ``?`` to show an overview.
