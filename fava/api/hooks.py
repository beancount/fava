import os
import sys
import importlib
from flask import g


def get_hooks():
    '''
    Attempts to import the specified script name and return the functions
    defined there (may return an empty list).

    Uses the base directory for beancount_file_path if it is absolute,
    otherwise uses current working directory.
    '''
    script_name = g.api.options['post-add-hooks']
    if script_name:
        # Kinda a hack, any better way to specify path?
        if os.path.isabs(g.api.beancount_file_path):
            directory = os.path.dirname(g.api.beancount_file_path)
        else:
            directory = os.getcwd()
        sys.path.insert(0, directory)
        module = importlib.import_module(script_name)
        retval = [module.__dict__[f] for f in dir(module)
                  if not f.startswith('__')]
        sys.path.pop(0)
        return retval
    return []


def post_api_add_transaction(transaction):
    hooks = get_hooks()
    for h in hooks:
        if h.__name__.startswith('add_transaction_'):
            try:
                h(transaction)
            except:
                pass  # No point in handling exceptions from hooks?


def post_api_add_document_metadata(bfilename, blineno, filepath):
    hooks = get_hooks()
    for h in hooks:
        if h.__name__.startswith('add_document_metadata'):
            try:
                h(bfilename, blineno, filepath)
            except:
                pass  # No point in handling exceptions from hooks?
