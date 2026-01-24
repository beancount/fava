Rustfava
========

Rustfava is a web interface for the double-entry bookkeeping software `rustledger
<https://github.com/rustledger/rustledger>`__, a Rust-based implementation of the Beancount format.

This is a fork of `Fava <https://github.com/beancount/fava>`__ that replaces the Python
beancount parser with rustledger, compiled to WebAssembly for faster parsing and processing.

Getting Started
---------------

Install Rustfava::

    pip3 install rustfava
    rustfava ledger.beancount

and visit the web interface at `http://localhost:5000
<http://localhost:5000>`__.

Development
-----------

See the repository for development instructions. Contributions are welcome!

Source: https://github.com/rustledger/rustfava
