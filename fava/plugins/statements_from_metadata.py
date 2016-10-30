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

StatementDocumentError = collections.namedtuple('StatementDocumentError', 'source message entry')

__plugins__ = ['statements_from_metadata']

def statements_from_metadata(entries, options_map):
    errors = []
    key = 'statement'

    if not 'documents' in options_map or len(options_map['documents']) == 0:
        return entries, errors

    def filenames(date, name):
        return [name, '{} {}'.format(date, name), '{}.{}'.format(date, name)]

    for entry in entries:
        type = entry.__class__.__name__.lower()
        if type == 'transaction':
            possible_paths = []  # set of tuples (account, path)
            date = entry.date.strftime("%Y-%m-%d")

            for documents_root in options_map['documents']:
                # If the `statement` metadata key is set on the transaction, assume it belongs to the first posting
                if key in entry.meta:
                    posting = entry.postings[0]
                    account = posting.account.replace(':', '/')
                    for filename in filenames(date, entry.meta[key]):
                        possible_paths.append((posting.account, join(dirname(options_map['filename']), filename)))
                        possible_paths.append((posting.account, join(dirname(options_map['filename']), documents_root, filename)))
                        possible_paths.append((posting.account, join(dirname(options_map['filename']), documents_root, account, filename)))

                # Check if the `statement` metadata key is set on one of the postings
                for posting in entry.postings:
                    if posting.meta and key in posting.meta:
                        account = posting.account.replace(':', '/')
                        for filename in filenames(date, posting.meta[key]):
                            possible_paths.append((posting.account, join(dirname(options_map['filename']), filename)))
                            possible_paths.append((posting.account, join(dirname(options_map['filename']), documents_root, filename)))
                            possible_paths.append((posting.account, join(dirname(options_map['filename']), documents_root, account, filename)))

            if len(possible_paths) == 0:
                continue

            found = False
            for account, path in possible_paths:
                if isfile(path):
                    # TODO link the Document entry with the Transaction
                    meta = data.new_metadata('<fava_statements_plugin>', 0)
                    entries.append(data.Document(meta, entry.date, account, path))
                    found = True

            if not found:
                errors.append(
                    StatementDocumentError(
                        entry.meta,
                        "Statement document not found. Search paths: {}".format(
                            ', '.join([path for _, path in possible_paths])),
                        entry))

    return entries, errors
