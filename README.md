# Rustfava

Rustfava is a web interface for the double-entry bookkeeping software
[rustledger](https://github.com/rustledger/rustledger), a Rust-based
implementation of the Beancount format.

This is a fork of [Fava](https://github.com/beancount/fava) that replaces the
Python beancount parser with rustledger, compiled to WebAssembly for faster
parsing and processing.

## Getting Started

### Option 1: Desktop App (Recommended)

Download the desktop app from [GitHub Releases](https://github.com/rustledger/rustfava/releases):

- **macOS**: `rustfava_x.x.x_universal.dmg`
- **Windows**: `rustfava_x.x.x_x64-setup.exe`
- **Linux**: `rustfava_x.x.x_amd64.AppImage`

Double-click to launch, then open your `.beancount` file.

### Option 2: Docker

Run the server in a container:

```bash
docker run -p 5000:5000 -v /path/to/ledger:/data ghcr.io/rustledger/rustfava /data/main.beancount
```

Then visit [http://localhost:5000](http://localhost:5000).

### Option 3: uv install

For developers or advanced users. Requires Python 3.13+ and [wasmtime](https://wasmtime.dev/):

```bash
uv tool install rustfava
rustfava ledger.beancount
```

Then visit [http://localhost:5000](http://localhost:5000).

## Development

See the repository for development instructions. Contributions are welcome!

## Links

- Source: https://github.com/rustledger/rustfava
- Documentation: https://rustledger.github.io/rustfava/
