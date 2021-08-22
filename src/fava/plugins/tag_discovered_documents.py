"""Beancount plugin to tag discovered documents.

It looks through all Document entries that were added by Beancount
automatically through file discovery and adds the tag "#discovered".
"""
from beancount.core.data import Document

__plugins__ = ["tag_discovered_documents"]


def tag_discovered_documents(entries, options_map):
    """Tag automatically added documents."""
    errors = []

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
