# Getting Started

If you're new to Beancount-format files or double-entry accounting in general,
we recommend
[Command-line Accounting in Context](https://docs.google.com/document/d/1e4Vz3wZB_8-ZcAwIFde8X5CjzKshE4-OXtVVHm4RQ8s/),
a motivational document written by Martin Blais, the creator of the Beancount
format.

To learn how to create your ledger file, refer to
[Getting Started with Beancount](https://docs.google.com/document/d/1P5At-z1sP8rgwYLHso5sEy3u4rMnIUDDgob9Y_BYuWE/)
guide. There is extensive documentation for the Beancount file format at the
[Beancount Documentation](https://docs.google.com/document/d/1RaondTJCS_IUPBHFNdT8oqFKJjVJDsfsn6JEjBG04eA)
page.

## Installation

### Option 1: Desktop App (Recommended)

Download the desktop app from
[GitHub Releases](https://github.com/rustledger/rustfava/releases):

| Platform    | Download                        |
| ----------- | ------------------------------- |
| **macOS**   | `rustfava_x.x.x_aarch64.dmg`    |
| **Windows** | `rustfava_x.x.x_x64-setup.exe`  |
| **Linux**   | `rustfava_x.x.x_amd64.AppImage` |

Double-click to launch, then open your `.beancount` file. No Python or other
dependencies required.

### Option 2: Command Line (PyPI)

rustfava runs on macOS, Linux, and Windows. You will need
[Python 3.13+](https://www.python.org/downloads/) and
[uv](https://docs.astral.sh/uv/).

```bash
uv tool install rustfava
```

Or to install into a virtual environment:

```bash
uv pip install rustfava
```

rustfava uses [rustledger](https://github.com/rustledger/rustledger), a
Rust-based parser compiled to WebAssembly, to parse your Beancount files. No
separate Beancount installation is required.

To export query results to Microsoft Excel or LibreOffice Calc:

```bash
uv tool install rustfava[excel]
```

To import transactions from files (the import/ingest UI, which uses
[beangulp](https://github.com/beancount/beangulp) importers — this is the only
feature that pulls in `beancount`):

```bash
uv tool install rustfava[ingest]
```

### Option 3: Docker

```bash
docker run -p 5000:5000 -v /path/to/ledger:/data ghcr.io/rustledger/rustfava /data/main.beancount
```

See
[Docker deployment](https://github.com/rustledger/rustfava/blob/main/contrib/docker/README.md)
for advanced options.

## Starting rustfava

### Desktop App

1. Launch the app
1. Click "Open File" or use File → Open
1. Select your `.beancount` file

### Command Line

```bash
rustfava ledger.beancount
```

Then visit [http://localhost:5000](http://localhost:5000).

Run `rustfava --help` for available options.

## Using rustfava

For more information on rustfava's features, refer to the help pages available
through rustfava's web interface. rustfava comes with Gmail-style keyboard
shortcuts; press `?` to show an overview.
