"""Beancount plugin to link entries to documents.

It goes through all entries with a `document` metadata-key, and tries to
associate them to Document entries. For transactions, it then also adds a link
from the transaction to documents, as well as the "#linked" tag.
"""

from __future__ import annotations

from collections import defaultdict
from os.path import normpath
from pathlib import Path
from typing import Any
from typing import TYPE_CHECKING

from fava.beans.abc import Document
from fava.beans.abc import Transaction
from fava.beans.account import get_entry_accounts
from fava.beans.funcs import hash_entry
from fava.beans.helpers import replace
from fava.helpers import BeancountError
from fava.util.sets import add_to_set

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Directive


class DocumentError(BeancountError):
    """Document-linking related error."""


__plugins__ = ["link_documents"]


def link_documents(
    entries: list[Directive],
    _: Any,
) -> tuple[list[Directive], list[DocumentError]]:
    """Link entries to documents."""
    errors = []

    # All document indices by their full file path.
    by_fullname = {}
    # All document indices by their file basename.
    by_basename = defaultdict(list)

    for index, entry in enumerate(entries):
        if isinstance(entry, Document):
            by_fullname[entry.filename] = index
            by_basename[Path(entry.filename).name].append((index, entry))

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
                Path(entry.meta["filename"]).parent / disk_doc,
            )
            if disk_doc_path in by_fullname:
                documents.append(by_fullname[disk_doc_path])

            if not documents:
                errors.append(
                    DocumentError(
                        entry.meta,
                        f"Document not found: '{disk_doc}'",
                        entry,
                    ),
                )
                continue

            for j in documents:
                # Since we might link a document multiple times, we have to use
                # the index for the replacement here.
                doc: Document = entries[j]  # type: ignore[assignment]
                entries[j] = replace(
                    doc,
                    links=add_to_set(doc.links, hash_),
                    tags=add_to_set(doc.tags, "linked"),
                )

            # The other entry types do not support links, so only add links for
            # txns.
            if isinstance(entry, Transaction):
                entries[index] = replace(
                    entry,
                    links=add_to_set(entry.links, hash_),
                )

    return entries, errors
