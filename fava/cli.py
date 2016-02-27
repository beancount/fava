# -*- coding: utf-8 -*-
import argparse
import os
import sys
import errno

from livereload import Server

from fava.application import app, load_settings


def run(argv):
    parser = argparse.ArgumentParser(description=__doc__,
                formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-p', '--port',
                        action='store',
                        type=int,
                        default=5000,
                        help="Port to listen on.")

    parser.add_argument('-H', '--host',
                        action='store',
                        type=str,
                        default='localhost',
                        help="Host for the webserver.")

    parser.add_argument('-s', '--settings',
                        action='store',
                        type=str,
                        help="Settings-file for fava.")

    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help="Turn on debugging. This uses the built-in Flask \
                              webserver, and live-reloading of beancount-files is disabled.")

    parser.add_argument('--profile',
                        action = 'store_true',
                        help="Turn on profiling.  Implies --debug.  Profiling \
                              information for each request will be printed to the \
                              log, unless --pstats-output is also specified.")

    parser.add_argument('--pstats-output',
                        type=str,
                        help="Output directory for profiling pstats data.  \
                              Implies --profile.  If this is specified, \
                              profiling information will be saved to the \
                              specified directly and will not be printed to \
                              the log.")

    parser.add_argument('--profile-restriction',
                        type=int,
                        default=30,
                        help='Maximum number of functions to show in profile printed \
                              to the log.')

    parser.add_argument('filename',
                        type=str,
                        help="Beancount input file.")

    args = parser.parse_args(argv)

    if args.pstats_output is not None:
        args.profile = True
    if args.profile:
        args.debug = True

    app.beancount_file = args.filename

    if args.debug:
        app.api.load_file(app.beancount_file)
        if args.settings:
            load_settings(os.path.realpath(args.settings))

        if args.profile:
            from werkzeug.contrib.profiler import ProfilerMiddleware
            app.config['PROFILE'] = True
            kwargs = {}
            if args.pstats_output is not None:
                kwargs['profile_dir'] = args.pstats_output
            app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[args.profile_restriction], **kwargs)

        app.config['ASSETS_CACHE'] = True
        app.config['ASSETS_DEBUG'] = True

        app.run(args.host, args.port, args.debug)
    else:
        server = Server(app.wsgi_app)
        reload_source_files(server)
        if args.settings:
            reload_settings(server, os.path.realpath(args.settings))

        try:
            server.serve(port=args.port, host=args.host, debug=args.debug)
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                print("Error: Can not start webserver because the port/address is already in use.")
                print("Please choose another port with the '-p' option. ({})".format(e))
            else:
                raise
        except:
            print("Unexpected error:", e)
            raise

def reload_source_files(server):
    """Auto-reload the main beancount-file and all it's includes the documents-folder."""
    app.api.load_file( app.beancount_file)
    server.watch(app.beancount_file, lambda: reload_source_files(server))
    include_path = os.path.dirname(app.beancount_file)
    for filename in app.api.options['include']+app.api.options['documents']:
        server.watch(os.path.join(include_path, filename), lambda: reload_source_files(server))

def reload_settings(server, settings_path):
    """Auto-reload the settings-file."""
    load_settings(settings_path)
    server.watch(settings_path, lambda: reload_settings(server, settings_path))

def main():
    run(sys.argv[1:])

if __name__ == '__main__':
    main()
