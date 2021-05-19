"""Beancount plugin to tag discovered documents.

It looks through all Document entries that were added by Beancount
automatically through file discovery and adds the tag "#discovered".
"""
from typing import List
from typing import Tuple

from beancount.core.data import Document
from beancount.core.data import Entries

from fava.helpers import BeancountError
from fava.util.typing import BeancountOptions

__plugins__ = ["tag_discovered_documents"]


def tag_discovered_documents(
    entries: Entries, options_map: BeancountOptions
) -> Tuple[Entries, List[BeancountError]]:
    """Tag automatically added documents."""
    errors: List[BeancountError] = []

    if "documents" not in options_map or not options_map["documents"]:
        return entries, errors

    for index, entry in enumerate(entries):
        if isinstance(entry, Document) and entry.meta["lineno"] == 0:
            tags = (
                set(entry.tags).union(["discovered"])
                if entry.tags
                else {"discovered"}
            )
            entries[index] = entry._replace(tags=tags)

    return entries, errors
