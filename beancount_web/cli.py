# -*- coding: utf-8 -*-
import argparse
import os
import sys

from livereload import Server

from beancount_web.api import BeancountReportAPI
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

    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help="Turn on debugging. This uses the built-in Flask \
                              webserver, and live-reloading of beancount-files is disabled.")

    parser.add_argument('filename',
                        type=str,
                        help="Beancount input file.")

    args = parser.parse_args(argv)

    app.beancount_file = args.filename
    app.filter_year = None
    app.filter_tag = None

    app.api = BeancountReportAPI(app.beancount_file)

    if args.debug:
        app.run(args.host, args.port, args.debug)
    else:
        server = Server(app.wsgi_app)

        # auto-reload the main beancount-file and all it's includes
        server.watch(app.beancount_file, app.api.load_file)
        include_path = os.path.dirname(app.beancount_file)
        for filename in app.api.options['include']:
            server.watch(os.path.join(include_path, filename), app.api.load_file)

        server.serve(port=args.port, host=args.host, debug=args.debug)


def main():
    run(sys.argv[1:])

if __name__ == '__main__':
    main()
