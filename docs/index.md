# Welcome to rustfava!

Rustfava is a web interface for double-entry bookkeeping, powered by
[rustledger](https://github.com/rustledger/rustledger), a Rust-based parser for
the Beancount file format compiled to WebAssembly for fast in-browser
processing.

Rustfava is a fork of [Fava](https://beancount.github.io/fava/) that replaces
the Python Beancount parser with rustledger for improved performance. Your
existing Beancount files are fully compatible.

![Rustfava Screenshot](https://i.imgbox.com/rfb9I7Zw.png)

If you are new to rustfava or Beancount-format files, begin with the
[Getting Started](usage.md) guide.

This is enough to get you up and running:

```bash
uv pip install rustfava
rustfava ledger.beancount
```

and visit the web interface at [http://localhost:5000](http://localhost:5000).
