"""Beancount plugin that creates errors from 'todo'-metadata-entries.

It looks through all Transaction entries that have the 'todo'-metadata-entry
and creates errors from these entries.
"""
import collections

from beancount.core.data import Transaction

__plugins__ = ['todo_as_error', ]

TodoError = collections.namedtuple('TodoError', 'source message entry')


def todo_as_error(entries, _):
    errors = []

    for entry in entries:
        if isinstance(entry, Transaction) and 'todo' in entry.meta:
            errors.append(TodoError(entry.meta, entry.meta['todo'], entry))

    return entries, errors
