# Getting Started

If you're new to Beancount-format files or double-entry accounting in general,
we recommend [Command-line Accounting in Context](https://docs.google.com/document/d/1e4Vz3wZB_8-ZcAwIFde8X5CjzKshE4-OXtVVHm4RQ8s/),
a motivational document written by Martin Blais, the creator of the Beancount
format.

To learn how to create your ledger file, refer to
[Getting Started with Beancount](https://docs.google.com/document/d/1P5At-z1sP8rgwYLHso5sEy3u4rMnIUDDgob9Y_BYuWE/)
guide. There is extensive documentation for the Beancount file format at the
[Beancount Documentation](https://docs.google.com/document/d/1RaondTJCS_IUPBHFNdT8oqFKJjVJDsfsn6JEjBG04eA)
page.

## Installation

Rustfava runs on macOS, Linux, and Windows. You will need
[Python 3](https://www.python.org/downloads/) and
[uv](https://docs.astral.sh/uv/).

Then you can install rustfava or update your existing installation by running:

```bash
uv pip install --upgrade rustfava
```

Rustfava uses [rustledger](https://github.com/rustledger/rustledger), a
Rust-based parser compiled to WebAssembly, to parse your Beancount files. No
separate Beancount installation is required.

If you want to export query results to Microsoft Excel or LibreOffice Calc, use
the following command to install the optional dependencies for this feature:

```bash
uv pip install --upgrade rustfava[excel]
```

## Starting Rustfava

After installing rustfava, you can start it by running:

```bash
rustfava ledger.beancount
```

pointing it to your Beancount file -- and visit the web interface at
[http://localhost:5000](http://localhost:5000).

There are some command-line options available, run `rustfava --help` for an
overview.

For more information on rustfava's features, refer to the help pages that are
available through rustfava's web-interface. Rustfava comes with Gmail-style
keyboard shortcuts; press `?` to show an overview.
