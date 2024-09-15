"""The command-line interface for Fava."""

from __future__ import annotations

import errno
import logging
import os
from pathlib import Path

import click
from cheroot.wsgi import Server
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.middleware.profiler import ProfilerMiddleware

from fava import __version__
from fava.application import create_app
from fava.util import simple_wsgi


class AddressInUse(click.ClickException):  # noqa: D101
    def __init__(self, port: int) -> None:  # pragma: no cover
        super().__init__(
            f"Cannot start Fava because port {port} is already in use."
            "\nPlease choose a different port with the '-p' option.",
        )


class NonAbsolutePathError(click.UsageError):  # noqa: D101
    def __init__(self, path: str) -> None:
        super().__init__(
            f"Paths in BEANCOUNT_FILE need to be absolute: {path}"
        )


class NoFileSpecifiedError(click.UsageError):  # noqa: D101
    def __init__(self) -> None:  # pragma: no cover
        super().__init__("No file specified")


def _add_env_filenames(filenames: tuple[str, ...]) -> tuple[str, ...]:
    """Read additional filenames from BEANCOUNT_FILE."""
    env_filename = os.environ.get("BEANCOUNT_FILE")
    if not env_filename:
        return tuple(dict.fromkeys(filenames))

    env_names = env_filename.split(os.pathsep)
    for name in env_names:
        if not Path(name).is_absolute():
            raise NonAbsolutePathError(name)

    all_names = tuple(env_names) + filenames
    return tuple(dict.fromkeys(all_names))


@click.command(context_settings={"auto_envvar_prefix": "FAVA"})
@click.argument(
    "filenames",
    nargs=-1,
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
)
@click.option(
    "-p",
    "--port",
    type=int,
    default=5000,
    show_default=True,
    metavar="<port>",
    help="The port to listen on.",
)
@click.option(
    "-H",
    "--host",
    type=str,
    default="localhost",
    show_default=True,
    metavar="<host>",
    help="The host to listen on.",
)
@click.option("--prefix", type=str, help="Set an URL prefix.")
@click.option(
    "--incognito",
    is_flag=True,
    help="Run in incognito mode and obscure all numbers.",
)
@click.option(
    "--read-only",
    is_flag=True,
    help="Run in read-only mode, disable any change through Fava.",
)
@click.option("-d", "--debug", is_flag=True, help="Turn on debugging.")
@click.option(
    "--profile",
    is_flag=True,
    help="Turn on profiling. Implies --debug.",
)
@click.option(
    "--profile-dir",
    type=click.Path(),
    help="Output directory for profiling data.",
)
@click.option(
    "--poll-watcher", is_flag=True, help="Use old polling-based watcher."
)
@click.version_option(version=__version__, prog_name="fava")
def main(  # noqa: PLR0913
    *,
    filenames: tuple[str, ...] = (),
    port: int = 5000,
    host: str = "localhost",
    prefix: str | None = None,
    incognito: bool = False,
    read_only: bool = False,
    debug: bool = False,
    profile: bool = False,
    profile_dir: str | None = None,
    poll_watcher: bool = False,
) -> None:  # pragma: no cover
    """Start Fava for FILENAMES on http://<host>:<port>.

    If the `BEANCOUNT_FILE` environment variable is set, Fava will use the
    files (delimited by ';' on Windows and ':' on POSIX) given there in
    addition to FILENAMES.

    Note you can also specify command-line options via environment variables
    with the `FAVA_` prefix. For example, `--host=0.0.0.0` is equivalent to
    setting the environment variable `FAVA_HOST=0.0.0.0`.
    """
    all_filenames = _add_env_filenames(filenames)

    if not all_filenames:
        raise NoFileSpecifiedError

    app = create_app(
        all_filenames,
        incognito=incognito,
        read_only=read_only,
        poll_watcher=poll_watcher,
    )

    if prefix:
        app.wsgi_app = DispatcherMiddleware(  # type: ignore[method-assign]
            simple_wsgi,
            {prefix: app.wsgi_app},
        )

    # ensure that cheroot does not use IP6 for localhost
    host = "127.0.0.1" if host == "localhost" else host
    # Debug mode if profiling is active
    debug = debug or profile

    click.secho(f"Starting Fava on http://{host}:{port}", fg="green")
    if not debug:
        server = Server((host, port), app)
        try:
            server.start()
        except KeyboardInterrupt:
            click.echo("Keyboard interrupt received: stopping Fava", err=True)
            server.stop()
        except OSError as error:
            if "No socket could be created" in str(error):
                raise AddressInUse(port) from error
            raise click.Abort from error
    else:
        logging.getLogger("fava").setLevel(logging.DEBUG)
        if profile:
            app.wsgi_app = ProfilerMiddleware(  # type: ignore[method-assign]
                app.wsgi_app,
                restrictions=(30,),
                profile_dir=profile_dir or None,
            )

        app.jinja_env.auto_reload = True
        try:
            app.run(host, port, debug)
        except OSError as error:
            if error.errno == errno.EADDRINUSE:
                raise AddressInUse(port) from error
            raise


# needed for pyinstaller:
if __name__ == "__main__":  # pragma: no cover
    main()
