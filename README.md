# Rustfava

Rustfava is a web interface for the double-entry bookkeeping software
[rustledger](https://github.com/rustledger/rustledger), a Rust-based
implementation of the Beancount format.

This is a fork of [Fava](https://github.com/beancount/fava) that replaces the
Python beancount parser with rustledger, compiled to WebAssembly for faster
parsing and processing.

## Getting Started

Install rustfava:

```bash
uv pip install rustfava
rustfava ledger.beancount
```

and visit the web interface at [http://localhost:5000](http://localhost:5000).

## Development

See the repository for development instructions. Contributions are welcome!

## Links

- Source: https://github.com/rustledger/rustfava
- Documentation: https://rustledger.github.io/rustfava/
