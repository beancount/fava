"""The command-line interface for Fava."""
from __future__ import annotations

import errno
import os

import click
from cheroot.wsgi import Server
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.middleware.profiler import ProfilerMiddleware

from fava import __version__
from fava.application import app
from fava.util import simple_wsgi


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
    help="Run in read-only mode, disabling any change through UI/API",
)
@click.option("-d", "--debug", is_flag=True, help="Turn on debugging.")
@click.option(
    "--profile", is_flag=True, help="Turn on profiling. Implies --debug."
)
@click.option(
    "--profile-dir",
    type=click.Path(),
    help="Output directory for profiling data.",
)
@click.version_option(version=__version__, prog_name="fava")
def main(
    filenames: tuple[str],
    port: int,
    host: str,
    prefix: str,
    incognito: bool,
    read_only: bool,
    debug: bool,
    profile: bool,
    profile_dir: str,
) -> None:  # pragma: no cover
    """Start Fava for FILENAMES on http://<host>:<port>.

    If the `BEANCOUNT_FILE` environment variable is set, Fava will use the
    files (space-delimited) specified there in addition to FILENAMES.

    Note you can also specify command-line options via environment variables.
    For example, `--host=0.0.0.0` is equivalent to setting the environment
    variable `FAVA_HOST=0.0.0.0`.
    """
    if profile:
        debug = True

    env_filename = os.environ.get("BEANCOUNT_FILE")
    all_filenames = (
        filenames + tuple(env_filename.split()) if env_filename else filenames
    )

    if not all_filenames:
        raise click.UsageError("No file specified")

    app.config["BEANCOUNT_FILES"] = all_filenames
    app.config["INCOGNITO"] = incognito
    app.config["READ_ONLY"] = read_only

    if prefix:
        app.wsgi_app = DispatcherMiddleware(  # type: ignore
            simple_wsgi, {prefix: app.wsgi_app}
        )

    if host == "localhost":
        # ensure that cheroot does not use IP6 for localhost
        host = "127.0.0.1"

    click.echo(f"Starting Fava on http://{host}:{port}")
    if not debug:
        server = Server((host, port), app)
        try:
            server.start()
        except KeyboardInterrupt:
            click.echo("Keyboard interrupt received: stopping Fava", err=True)
            server.stop()
        except OSError as error:
            if "No socket could be created" in str(error):
                click.echo(
                    f"Cannot start Fava because port {port} is already in use."
                    "\nPlease choose a different port with the '-p' option."
                )
            raise click.Abort from error
    else:
        if profile:
            app.config["PROFILE"] = True
            app.wsgi_app = ProfilerMiddleware(  # type: ignore
                app.wsgi_app,
                restrictions=(30,),
                profile_dir=profile_dir if profile_dir else None,
            )

        app.jinja_env.auto_reload = True
        try:
            app.run(host, port, debug)
        except OSError as error:
            if error.errno == errno.EADDRINUSE:
                click.echo(
                    f"Cannot start Fava because port {port} is already in use."
                    "\nPlease choose a different port with the '-p' option."
                )
                raise click.Abort from error
            raise


# needed for pyinstaller:
if __name__ == "__main__":  # pragma: no cover
    # pylint: disable=no-value-for-parameter
    main()
