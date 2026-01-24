# Development

## Setting up a development environment

If you want to hack on rustfava or run the latest development version, make sure
you have recent enough versions of the following installed (ideally with your
system package manager):

- [Python 3.13+](https://www.python.org/) - as rustfava is written in Python
- [Bun](https://bun.sh/) - to build the frontend
- [just](https://just.systems/) - to run various build / lint / test targets
- [uv](https://docs.astral.sh/uv/) - to install the development environment and run scripts

Then this will get you up and running:

```bash
git clone https://github.com/rustledger/rustfava.git
cd rustfava
# setup a virtual environment (at .venv) and install rustfava and development
# dependencies into it:
just dev
```

You can start rustfava in the virtual environment as usual by running `rustfava`.
Running in debug mode with `rustfava --debug` is useful for development.

You can run the tests with `just test` and the linters by running `just lint`.
Run `just --list` to see all available recipes. After any changes to the
Javascript code, you will need to re-build the frontend, which you can do by
running `just frontend`. If you are working on the frontend code, running
`bun run dev` in the `frontend` folder will watch for file changes and rebuild
the Javascript bundle continuously.

Contributions are very welcome, just open a PR on
[GitHub](https://github.com/rustledger/rustfava/pulls).

Rustfava is released under the [MIT License](https://github.com/rustledger/rustfava/blob/main/LICENSE).
