# -*- coding: utf-8 -*-
import os
import errno

import click
from werkzeug.wsgi import DispatcherMiddleware

from fava.application import app, load_file
from fava.util import simple_wsgi


@click.command()
@click.argument('filenames', nargs=-1,
                type=click.Path(exists=True, resolve_path=True))
@click.option('-p', '--port', type=int, default=5000,
              help='The port to listen on. (default: 5000)')
@click.option('-H', '--host', type=str, default='localhost',
              help='The host to listen on. (default: localhost)')
@click.option('--prefix', type=str,
              help='Set an URL prefix. (for reverse proxy)')
@click.option('-d', '--debug', is_flag=True,
              help='Turn on debugging. Disables live-reloading.')
@click.option('--profile', is_flag=True,
              help='Turn on profiling. Implies --debug.')
@click.option('--profile-dir', type=click.Path(),
              help='Output directory for profiling data.')
@click.option('--profile-restriction', type=int, default=30,
              help='Number of functions to show in profile.')
def main(filenames, port, host, prefix, debug, profile, profile_dir,
         profile_restriction):
    """Start Fava for FILENAMES on http://host:port.

    If the `BEANCOUNT_FILE` environment variable is set, Fava will use the file
    specified there in addition to FILENAMES.
    """

    if profile_dir:  # pragma: no cover
        profile = True
    if profile:  # pragma: no cover
        debug = True

    env_filename = os.environ.get('BEANCOUNT_FILE', None)
    if env_filename:
        filenames = filenames + (env_filename,)

    if not filenames:
        raise click.UsageError('No file specified')

    app.config['BEANCOUNT_FILES'] = filenames

    load_file()

    if prefix:
        app.wsgi_app = DispatcherMiddleware(simple_wsgi,
                                            {prefix: app.wsgi_app})

    if debug:  # pragma: no cover
        if profile:
            from werkzeug.contrib.profiler import ProfilerMiddleware
            app.config['PROFILE'] = True
            app.wsgi_app = ProfilerMiddleware(
                app.wsgi_app,
                restrictions=(profile_restriction,),
                profile_dir=profile_dir if profile_dir else None)

        app.jinja_env.auto_reload = True

    try:
        app.run(host, port, debug)
    except OSError as error:
        if error.errno == errno.EADDRINUSE:
            raise click.UsageError(
                "Can not start webserver because the port is already in "
                "use. Please choose another port with the '-p' option.")
        else:  # pragma: no cover
            raise


# needed for pyinstaller:
if __name__ == '__main__':  # pragma: no cover
    main()
