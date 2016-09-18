# -*- coding: utf-8 -*-
import os
import errno

import click
from livereload import Server

from fava.application import app, load_file


@click.command()
@click.argument('filenames', nargs=-1,
                type=click.Path(exists=True, resolve_path=True))
@click.option('-p', '--port', type=int, default=5000,
              help='The port to listen on. (default: 5000)')
@click.option('-H', '--host', type=str, default='localhost',
              help='The host to listen on. (default: localhost)')
@click.option('-d', '--debug', is_flag=True,
              help='Turn on debugging. Disables live-reloading.')
@click.option('--profile', is_flag=True,
              help='Turn on profiling. Implies --debug.')
@click.option('--profile-dir', type=click.Path(),
              help='Output directory for profiling data.')
@click.option('--profile-restriction', type=int, default=30,
              help='Number of functions to show in profile.')
def main(filenames, port, host, debug, profile, profile_dir,
         profile_restriction):
    """Start fava for FILENAMES on http://host:port."""

    if profile_dir:
        profile = True
    if profile:
        debug = True

    env_filename = os.environ.get('BEANCOUNT_FILE', None)
    if env_filename:
        filenames = filenames + (env_filename,)

    if not filenames:
        raise click.UsageError('No file specified')

    app.config['BEANCOUNT_FILES'] = filenames

    load_file()

    if debug:
        if profile:
            from werkzeug.contrib.profiler import ProfilerMiddleware
            app.config['PROFILE'] = True
            app.wsgi_app = ProfilerMiddleware(
                app.wsgi_app,
                restrictions=(profile_restriction,),
                profile_dir=profile_dir if profile_dir else None)

        app.run(host, port, debug)
    else:
        server = Server(app.wsgi_app)

        def reload_source_files(api, startup=False):
            if not startup:
                api.load_file()
            include_path = os.path.dirname(api.beancount_file_path)
            paths = api.options['include'] + api.options['documents']
            if api.beancount_file_path not in paths:
                paths.append(api.beancount_file_path)
            for path in paths:
                server.watch(os.path.join(include_path, path),
                             lambda: reload_source_files(api))

        for api in app.config['APIS'].values():
            reload_source_files(api, True)

        try:
            server.serve(port=port, host=host, debug=debug)
        except OSError as error:
            if error.errno == errno.EADDRINUSE:
                print("Error: Can not start webserver because the port/address"
                      "is already in use.")
                print("Please choose another port with the '-p' option.")
            else:
                raise


if __name__ == "__main__":
    main()
