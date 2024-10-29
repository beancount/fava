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
from fava.beans.account import get_entry_accounts
from fava.beans.funcs import get_position
from fava.beans.helpers import replace
from fava.helpers import BeancountError
from fava.util.sets import add_to_set

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Sequence

    from fava.beans.abc import Directive


class DocumentError(BeancountError):
    """Document-linking related error."""


__plugins__ = ["link_documents"]


def link_documents(
    entries: Sequence[Directive],
    _: Any,
) -> tuple[Sequence[Directive], list[DocumentError]]:
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

    new_entries = list(entries)
    for index, entry in enumerate(entries):
        disk_docs = [
            value
            for key, value in entry.meta.items()
            if key.startswith("document") and isinstance(value, str)
        ]

        if not disk_docs:
            continue

        # Link the documents by using the entry date. This means that this will
        # not necessarily be unique, but it shows which date the linked entry
        # is on (and it will probably narrow it down enough)
        entry_link = f"dok-{entry.date}"
        entry_accounts = get_entry_accounts(entry)
        entry_filename, _ = get_position(entry)
        for disk_doc in disk_docs:
            documents = [
                j
                for j, document in by_basename[disk_doc]
                if document.account in entry_accounts
            ]
            disk_doc_path = normpath(
                Path(entry_filename).parent / disk_doc,
            )
            if disk_doc_path in by_fullname:
                documents.append(by_fullname[disk_doc_path])

            if not documents:
                errors.append(
                    DocumentError(
                        entry.meta, f"Document not found: '{disk_doc}'", entry
                    ),
                )
                continue

            for j in documents:
                # Since we might link a document multiple times, we have to use
                # the index for the replacement here.
                doc: Document = new_entries[j]  # type: ignore[assignment]
                new_entries[j] = replace(
                    doc,
                    links=add_to_set(doc.links, entry_link),
                    tags=add_to_set(doc.tags, "linked"),
                )

            # Not all entry types support links, so only add links for the ones
            # that do.
            if hasattr(entry, "links"):
                new_entries[index] = replace(
                    entry,
                    links=add_to_set(entry.links, entry_link),
                )

    return new_entries, errors
