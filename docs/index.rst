Welcome to Rustfava!
====================

.. toctree::
    :hidden:

    usage
    changelog
    development
    api

Rustfava is a web interface for double-entry bookkeeping, powered by
`rustledger`_, a Rust-based parser for the Beancount file format compiled to
WebAssembly for fast in-browser processing.

.. _rustledger: https://github.com/rustledger/rustledger

Rustfava is a fork of `Fava <https://beancount.github.io/fava/>`_ that replaces
the Python Beancount parser with rustledger for improved performance. Your
existing Beancount files are fully compatible.

.. image:: https://i.imgbox.com/rfb9I7Zw.png

If you are new to Rustfava or Beancount-format files, begin with the :doc:`usage` guide.

This is enough to get you up and running::

    uv pip install rustfava
    rustfava ledger.beancount

and visit the web interface at `http://localhost:5000
<http://localhost:5000>`_.
