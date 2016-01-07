#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import platform
import configparser
from subprocess import call
from pkg_resources import Requirement, resource_filename

"""
Manage the Beancount URL scheme "beancount://".
"""

# http://stackoverflow.com/a/5423147
_ROOT = os.path.abspath(os.path.dirname(__file__))
def get_resource_path(path):
    return os.path.join(_ROOT, path)

# print get_resource_path('resource1/foo.txt')

def run(arguments):
    #settings_path = resource_filename(Requirement.parse("beancount_urlscheme"), "beancount_urlscheme/beancount-urlscheme-settings.conf")
    settings_path = get_resource_path("beancount-urlscheme-settings.conf")
    parser = argparse.ArgumentParser(description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter)

    subparsers = parser.add_subparsers(dest='subcommand')

    subparser = subparsers.add_parser('register', help='Register the URL scheme in your OS.')
    subparser.add_argument('settings', type=str, help='Path to the beancount-web settings file')

    subparser = subparsers.add_parser('open', help='Open the specified file in the editor.')
    subparser.add_argument('--line', type=int, default=1, help="The line to go to.")
    subparser.add_argument('file', type=str, help="The File to open.")

    args = parser.parse_args(arguments)

    if args.subcommand == "register":
        if platform.system() == "Darwin":
            config = configparser.ConfigParser()
            config.read(settings_path)

            config.set('beancount-urlscheme', 'beancount-web-settings-file', args.settings)

            with open(settings_path, 'w') as configfile:
                config.write(configfile)

            command = get_resource_path("mac/BeancountURLSchemeHandler.app/Contents/MacOS/applet")
            call(command.split(' '))
        else:
            print("Not yet implemented for " + platform.system())

    elif args.subcommand == "open":
        config = configparser.ConfigParser()
        config.read(settings_path)
        settings_path = config['beancount-urlscheme']['beancount-web-settings-file']
        config.read(settings_path)

        command = config['beancount-web']['external-editor-cmd'].format(filename=args.file, line=args.line)
        call(command.split(' '))

def main():
    run(sys.argv[1:])

if __name__ == '__main__':
    main()
