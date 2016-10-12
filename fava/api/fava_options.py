from collections import namedtuple

OptionError = namedtuple('OptionError', 'source message entry')

DEFAULTS = {
    'default-file': None,
    'account-journal-include-children': True,
    'charts': True,
    'use-external-editor': False,
    'show-closed-accounts': False,
    'show-accounts-with-zero-balance': True,
    'show-accounts-with-zero-transactions': True,
    'uptodate-indicator-grey-lookback-days': 60,
    'sidebar-show-queries': 5,
    'editor-print-margin-column': 60,
    'journal-show': ['transaction', 'balance', 'note', 'document', 'custom',
                     'budget'],
    'journal-show-transaction': ['cleared', 'pending'],
    'language': None,
    'interval': 'month',
}

BOOL_OPTS = [
    'account-journal-include-children',
    'charts',
    'use-external-editor',
    'show-closed-accounts',
    'show-accounts-with-zero-balance',
    'show-accounts-with-zero-transactions',
]

INT_OPTS = [
    'editor-print-margin-column',
    'sidebar-show-queries',
    'uptodate-indicator-grey-lookback-days',
]

LIST_OPTS = [
    'journal-show',
    'journal-show-transaction',
]

STR_OPTS = [
    'language',
    'interval',
]


def _parse_option_entry(entry):
    key = entry.values[0].value
    assert key in DEFAULTS.keys()

    if key == 'default-file':
        value = entry.meta['filename']
    else:
        value = entry.values[1].value
        assert isinstance(value, str)

    if key in BOOL_OPTS:
        value = value.lower() == 'true'
    if key in INT_OPTS:
        value = int(value)
    if key in LIST_OPTS:
        value = str(value).strip().split(' ')

    return key, value


def parse_options(custom_entries):
    """ Parse custom entries for fava options. They have the following format:

    2016-04-01 custom "fava-option" "[setting_name]" "[setting_value]"
    """

    options = DEFAULTS.copy()
    errors = []

    for entry in custom_entries:
        if entry.type == 'fava-option':
            try:
                key, value = _parse_option_entry(entry)
                options[key] = value
            except (IndexError, TypeError, AssertionError):
                errors.append(OptionError(
                    entry.meta,
                    'Failed to parse fava-option entry',
                    entry))

    return options, errors
