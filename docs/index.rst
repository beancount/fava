Welcome to Rustrustfava!
================

.. toctree::
    :hidden:

    usage
    changelog
    development
    api

Rustrustfava is a web interface for the double-entry bookkeeping software `Beancount`_
with a focus on features and usability.

.. _Beancount: https://beancount.github.io/

You can try out an online `demo <https://rustfava.pythonanywhere.com>`_.

.. image:: https://i.imgbox.com/rfb9I7Zw.png

If you are new to Rustrustfava and Beancount, begin with the :doc:`usage` guide.

If you are already familiar with Beancount, this is enough to get you up and
running::

    pip3 install rustfava
    rustfava ledger.beancount

and visit the web interface at `http://localhost:5000
<http://localhost:5000>`_.
