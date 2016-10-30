"""Plugin that looks through all transactions and their postings for the
`statement`-metadata-key, and if found and present in the filesystem, adds a
corresponding Document-directive.

The file specified in the `statement`-metadata-value will be searched
"intelligently", based on the suggestions by @corani
(https://github.com/beancount/fava/issues/386#issuecomment-256267212).
"""
import collections
from os.path import join, dirname, isfile
from beancount.core import data

StatementDocumentError = collections.namedtuple('StatementDocumentError',
                                                'source message entry')

__plugins__ = ['statements_from_metadata']


def statements_from_metadata(entries, options_map):
    errors = []
    key = 'statement'

    if 'documents' not in options_map or len(options_map['documents']) == 0:
        return entries, errors

    def filenames(date, name):
        d_str = date.strftime("%Y-%m-%d")
        return [name, '{} {}'.format(d_str, name), '{}.{}'.format(d_str, name)]

    for entry in entries:
        type = entry.__class__.__name__.lower()

        if type != 'transaction':
            continue

        paths = []  # set of tuples (account, path)
        b_dir = dirname(options_map['filename'])

        for documents in options_map['documents']:
            statements = []

            # If the `statement` metadata key is set on the transaction, assume
            # it belongs to the first posting
            if key in entry.meta:
                statements.append((entry.meta[key], entry.postings[0].account))

            for posting in entry.postings:
                if posting.meta and key in posting.meta:
                    statements.append((posting.meta[key], posting.account))

            for path, account in statements:
                account_path = account.replace(':', '/')
                for filename in filenames(entry.date, path):
                    paths.append((account, join(b_dir, filename)))
                    paths.append((account, join(b_dir, documents, filename)))
                    paths.append((account, join(b_dir, documents,
                                                account_path, filename)))

        if len(paths) == 0:
            continue

        found = False
        for account, path in paths:
            if isfile(path):
                # TODO link the Document entry with the Transaction
                meta = data.new_metadata('<fava_statements_plugin>', 0)
                entries.append(data.Document(meta, entry.date, account, path))
                found = True

        if not found:
            errors.append(
                StatementDocumentError(
                    entry.meta,
                    "Document not found. Search paths: {}".format(
                        ', '.join([path for _, path in paths])),
                    entry))

    return entries, errors
