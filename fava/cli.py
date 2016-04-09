# -*- coding: utf-8 -*-
import os
import errno

import click
from livereload import Server

from fava.application import app, load_file, load_settings


@click.command()
@click.argument('filenames', nargs=-1,
                type=click.Path(exists=True, resolve_path=True))
@click.option('-p', '--port', type=int, default=5000,
              help='The port to listen on. (default: 5000)')
@click.option('-H', '--host', type=str, default='localhost',
              help='The host to listen on. (default: localhost)')
@click.option('-s', '--settings',
              type=click.Path(exists=True, resolve_path=True),
              help='Settings file for fava.')
@click.option('-d', '--debug', is_flag=True,
              help='Turn on debugging. Disables live-reloading.')
@click.option('--profile', is_flag=True,
              help='Turn on profiling. Implies --debug.')
@click.option('--profile-dir', type=click.Path(),
              help='Output directory for profiling data.')
@click.option('--profile-restriction', type=int, default=30,
              help='Number of functions to show in profile.')
def main(filenames, port, host, settings, debug, profile, profile_dir,
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
    app.config['USER_SETTINGS'] = settings

    load_settings()
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
        if settings:
            server.watch(settings, load_settings)

        def reload_source_files(api):
            filename = api.options['filename']
            api.load_file(filename)
            include_path = os.path.dirname(filename)
            for filename in api.options['include'] + \
                    api.options['documents']:
                server.watch(os.path.join(include_path, filename),
                             lambda: reload_source_files(api))

        for api in app.config['APIS'].values():
            reload_source_files(api)

        try:
            server.serve(port=port, host=host, debug=debug)
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                print("Error: Can not start webserver because the port/address"
                      "is already in use.")
                print("Please choose another port with the '-p' option.")
            else:
                raise
        except:
            print("Unexpected error:", e)
            raise
