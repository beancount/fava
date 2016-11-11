"""Plugin that looks through all Document entries that were added by beancount
automatically through file discovery and adds the tag "#discovered".
"""
from beancount.core import data

__plugins__ = ['tag_discovered_documents']


def tag_discovered_documents(entries, options_map):
    errors = []

    if 'documents' not in options_map or len(options_map['documents']) == 0:
        return entries, errors

    for i, entry in enumerate(entries):
        if isinstance(entry, data.Document) and entry.meta['lineno'] == 0:
            tags = set(entry.tags).union(['discovered']) \
                   if entry.tags else set(['discovered'])
            entries[i] = entry._replace(tags=tags)

    return entries, errors
