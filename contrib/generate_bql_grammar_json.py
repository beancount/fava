"""Generate a JSON file with BQL grammar attributes.

The online code editor needs to have the list of available columns, functions,
and keywords for syntax highlighting and completion.

This script should be run whenever the BQL changes.
"""

import json
import os

from beancount.query import query_env
from beancount.query import query_parser


def _env_to_list(attributes):
    result = []
    for name in attributes.keys():
        if isinstance(name, tuple):
            name = name[0]
        result.append(name)
    return result


TARGET_ENV = query_env.TargetsEnvironment()

DATA = {
    'columns': _env_to_list(TARGET_ENV.columns),
    'functions': _env_to_list(TARGET_ENV.functions),
    'keywords': [kw.lower() for kw in query_parser.Lexer.keywords],
}

PATH = os.path.join(os.path.dirname(__file__),
                    '../fava/static/javascript/codemirror/bql-grammar.json')

with open(PATH, 'w') as fd:
    json.dump(DATA, fd)
