Welcome to fava!
================

.. toctree::
    :hidden:

    screenshots
    development

fava is a web interface for the double-entry bookkeeping software `beancount
<http://furius.ca/beancount/>`__ with a focus on features and usability.

You can try out an online `demo <http://fava.pythonanywhere.com>`__ and there are some more
screenshots :doc:`here <screenshots>`.

.. image:: screenshots/income-statement1.png

Getting Started
---------------

You'll need Python 3 (>= 3.4) to install fava by running::

    pip3 install beancount-fava

Start fava by running ::

    fava ledger.beancount

pointing it to your beancount file -- and visit the web interface at `http://localhost:5000 <http://localhost:5000>`__.

(fava comes with Gmail-style keyboard shortcuts: Press ``?`` to show an overview)
