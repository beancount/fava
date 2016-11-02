"""Plugin that looks through all transactions and their postings for the
`statement`-metadata-key, and if found it looks for corresponding Document
entries that were added by beancount automatically through file discovery.

It then adds a link to the transaction and the Document, and the tag
"#statement" to the Document.
"""
import collections
from os.path import join, dirname, normpath, basename
from beancount.core import data
from beancount.core.compare import hash_entry

LinkStatementError = collections.namedtuple('LinkStatementError', 'message')

StatementDocumentError = collections.namedtuple('StatementDocumentError',
                                                'source message entry')

__plugins__ = ['link_statements']


def link_statements(entries, options_map):
    errors = []

    if 'documents' not in options_map or len(options_map['documents']) == 0:
        errors.append(LinkStatementError(
            'link_statements requires "documents" option to be set'))
        return entries, errors

    all_documents = [(i, entry) for i, entry in enumerate(entries)
                     if isinstance(entry, data.Document)]

    all_transactions = [(i, entry) for i, entry in enumerate(entries)
                        if isinstance(entry, data.Transaction)]

    for i, entry in all_transactions:
        statements = [value for key, value in entry.meta.items()
                      if key.startswith('statement')]

        _hash = hash_entry(entry)[:8]
        for statement in statements:
            statement_p = normpath(join(dirname(entry.meta['filename']),
                                        statement))
            documents = [(j, document) for j, document in all_documents
                         if (document.filename == statement_p and
                             document.meta['lineno'] == 0) or
                            (document.account in
                                [pos.account for pos in entry.postings] and
                             basename(document.filename) == statement)]

            if (len(documents) == 0):
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
            entries[i] = entry._replace(links=links)

    return entries, errors
