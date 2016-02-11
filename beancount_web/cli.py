# -*- coding: utf-8 -*-
import argparse
import os
import sys

from livereload import Server

from beancount_web.application import app


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
                        help="Configuration-file for beancount-web.")

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
    app.api.load_file(app.beancount_file)


    if args.settings:
        app.config.user['file_user'] = os.path.realpath(args.settings)
        app.config.raw.read(app.config.user['file_user'])

    if args.debug:
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

        server.serve(port=args.port, host=args.host, debug=args.debug)

def reload_source_files(server):
    app.api.load_file()
    # auto-reload the main beancount-file and all it's includes
    server.watch(app.beancount_file, lambda: reload_source_files(server))
    include_path = os.path.dirname(app.beancount_file)
    for filename in app.api.options['include']:
        server.watch(os.path.join(include_path, filename), lambda: reload_source_files(server))

def main():
    run(sys.argv[1:])

if __name__ == '__main__':
    main()
