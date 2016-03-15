Welcome to fava!
================

.. toctree::
    :hidden:

    usage
    screenshots
    changelog
    development

fava is a web interface for the double-entry bookkeeping software `Beancount
<http://furius.ca/beancount/>`__ with a focus on features and usability.

You can try out an online `demo <http://fava.pythonanywhere.com>`__ and there
are some more screenshots :doc:`here <screenshots>`.

.. image:: static/screenshots/income-statement1.png

If you are new to fava and beancount, begin with the :doc:`usage` guide.

If you are already familiar with beancount, this is enough to get you up and running::

    pip3 install beancount-fava
    fava ledger.beancount

and visit the web interface at `http://localhost:5000 <http://localhost:5000>`__.
