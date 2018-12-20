"""Beancount plugin to link transactions to documents.

It goes through all transactions with a `document` metadata-key, and tries to
associate them to Document entries. It then adds a link from transactions to
documents, as well as the "#linked" tag.

"""

import collections
from os.path import join, dirname, normpath, basename

from beancount.core import data
from beancount.core.compare import hash_entry

DocumentError = collections.namedtuple("DocumentError", "source message entry")

__plugins__ = ["link_documents"]


def link_documents(entries, _):
    errors = []

    all_documents = [
        (index, entry)
        for index, entry in enumerate(entries)
        if isinstance(entry, data.Document)
    ]

    transactions = [
        (index, entry)
        for index, entry in enumerate(entries)
        if isinstance(entry, data.Transaction)
    ]

    for index, entry in transactions:
        disk_docs = [
            value
            for key, value in entry.meta.items()
            if key.startswith("document")
        ]

        _hash = hash_entry(entry)[:8]
        for disk_doc in disk_docs:
            disk_doc_path = normpath(
                join(dirname(entry.meta["filename"]), disk_doc)
            )
            documents = [
                (j, document)
                for j, document in all_documents
                if (document.filename == disk_doc_path)
                or (
                    document.account in [pos.account for pos in entry.postings]
                    and basename(document.filename) == disk_doc
                )
            ]

            if not documents:
                errors.append(
                    DocumentError(
                        entry.meta,
                        "Document not found: {}".format(disk_doc),
                        entry,
                    )
                )
                continue

            for j, document in documents:
                tags = (
                    set(document.tags)
                    .union(["linked"])
                    .difference(["discovered"])
                    if document.tags
                    else set(["linked"])
                )
                links = (
                    set(document.links).union([_hash])
                    if document.links
                    else set([_hash])
                )
                entries[j] = document._replace(links=links, tags=tags)

            links = (
                set(entry.links).union([_hash])
                if entry.links
                else set([_hash])
            )
            entries[index] = entry._replace(links=links)

    return entries, errors
