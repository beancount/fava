"""Beancount plugin to link transactions to documents.

It goes through all transactions with a `document` metadata-key, and tries to
associate them to Document entries. It then adds a link from transactions to
documents, as well as the "#linked" tag.
"""
from collections import defaultdict
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import normpath
from typing import AbstractSet
from typing import Any
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

from beancount.core.compare import hash_entry
from beancount.core.data import Document
from beancount.core.data import Entries
from beancount.core.data import Transaction

from fava.helpers import BeancountError


class DocumentError(BeancountError):
    """Document-linking related error."""


__plugins__ = ["link_documents"]


def add_to_set(set_: Optional[AbstractSet[str]], new: str) -> Set[str]:
    """Add an entry to a set (or create it if doesn't exist)."""
    return set(set_).union([new]) if set_ else {new}


def link_documents(
    entries: Entries, _: Any
) -> Tuple[Entries, List[DocumentError]]:
    """Link transactions to documents."""

    errors = []

    transactions = []
    by_fullname = {}
    by_basename = defaultdict(list)
    for index, entry in enumerate(entries):
        if isinstance(entry, Document):
            by_fullname[entry.filename] = index
            by_basename[basename(entry.filename)].append((index, entry))
        elif isinstance(entry, Transaction):
            transactions.append((index, entry))

    for index, entry in transactions:
        disk_docs = [
            value
            for key, value in entry.meta.items()
            if key.startswith("document")
        ]

        if not disk_docs:
            continue

        hash_ = hash_entry(entry)[:8]
        txn_accounts = [pos.account for pos in entry.postings]
        for disk_doc in disk_docs:
            documents = [
                j
                for j, document in by_basename[disk_doc]
                if document.account in txn_accounts
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

            entries[index] = entry._replace(
                links=add_to_set(entry.links, hash_)
            )

    return entries, errors
