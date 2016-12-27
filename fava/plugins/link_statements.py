"""Beancount plugin to link statements to documents.

It goes through all transactions with a `statement` metadata-key, and tries to
match them to Document entries. It then adds a link to the transaction and the
document, and the tag "#statement" to the document.
"""

import collections
from os.path import join, dirname, normpath, basename

from beancount.core import data
from beancount.core.compare import hash_entry

StatementDocumentError = collections.namedtuple('StatementDocumentError',
                                                'source message entry')

__plugins__ = ['link_statements']


def link_statements(entries, _):
    errors = []

    all_documents = [(index, entry) for index, entry in enumerate(entries)
                     if isinstance(entry, data.Document)]

    transactions = [(index, entry) for index, entry in enumerate(entries)
                    if isinstance(entry, data.Transaction)]

    for index, entry in transactions:
        statements = [value for key, value in entry.meta.items()
                      if key.startswith('statement')]

        _hash = hash_entry(entry)[:8]
        for statement in statements:
            statement_path = normpath(join(dirname(entry.meta['filename']),
                                           statement))
            documents = [(j, document) for j, document in all_documents
                         if (document.filename == statement_path) or
                         (document.account in
                          [pos.account for pos in entry.postings] and
                          basename(document.filename) == statement)]

            if not documents:
                errors.append(
                    StatementDocumentError(
                        entry.meta,
                        "Statement Document not found: {}".format(statement),
                        entry))
                continue

            for j, document in documents:
                tags = set(document.tags).union(
                    ['statement']).difference(['discovered']) \
                    if document.tags else set(['statement'])
                links = set(document.links).union([_hash]) \
                    if document.links else set([_hash])
                entries[j] = document._replace(links=links, tags=tags)

            links = set(entry.links).union([_hash]) \
                if entry.links else set([_hash])
            entries[index] = entry._replace(links=links)

    return entries, errors
