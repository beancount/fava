"""Beancount plugin to link entries to documents.

It goes through all entries with a `document` metadata-key, and tries to
associate them to Document entries. For transactions, it then also adds a link
from the transaction to documents, as well as the "#linked" tag.
"""
from collections import defaultdict
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import normpath
from typing import Any
from typing import List
from typing import Tuple

from beancount.core.compare import hash_entry
from beancount.core.data import Document
from beancount.core.data import Entries
from beancount.core.data import Transaction

from fava.core.accounts import get_entry_accounts
from fava.helpers import BeancountError
from fava.util.sets import add_to_set


class DocumentError(BeancountError):
    """Document-linking related error."""


__plugins__ = ["link_documents"]


def link_documents(
    entries: Entries, _: Any
) -> Tuple[Entries, List[DocumentError]]:
    """Link entries to documents."""

    errors = []

    # All document indices by their full file path.
    by_fullname = {}
    # All document indices by their file basename.
    by_basename = defaultdict(list)

    for index, entry in enumerate(entries):
        if isinstance(entry, Document):
            by_fullname[entry.filename] = index
            by_basename[basename(entry.filename)].append((index, entry))

    for index, entry in enumerate(entries):
        disk_docs = [
            value
            for key, value in entry.meta.items()
            if key.startswith("document")
        ]

        if not disk_docs:
            continue

        hash_ = hash_entry(entry)[:8]
        entry_accounts = get_entry_accounts(entry)
        for disk_doc in disk_docs:
            documents = [
                j
                for j, document in by_basename[disk_doc]
                if document.account in entry_accounts
            ]
            disk_doc_path = normpath(
                join(dirname(entry.meta["filename"]), disk_doc)
            )
            if disk_doc_path in by_fullname:
                documents.append(by_fullname[disk_doc_path])

            if not documents:
                errors.append(
                    DocumentError(
                        entry.meta,
                        f"Document not found: '{disk_doc}'",
                        entry,
                    )
                )
                continue

            for j in documents:
                # Since we might link a document multiple times, we have to use
                # the index for the replacement here.
                doc: Document = entries[j]  # type: ignore
                entries[j] = doc._replace(
                    links=add_to_set(doc.links, hash_),
                    tags=add_to_set(doc.tags, "linked"),
                )

            # The other entry types do not support links, so only add links for
            # txns.
            if isinstance(entry, Transaction):
                entries[index] = entry._replace(
                    links=add_to_set(entry.links, hash_)
                )

    return entries, errors
