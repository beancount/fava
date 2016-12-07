"""Entry filters."""

import re

from beancount.core import account
from beancount.core.data import Transaction
from beancount.ops import summarize
from beancount.query import (
    query_compile, query_env, query_execute, query_parser)
from fava.util.date import parse_date


class FilterException(Exception):
    """Filter exception."""

    def __init__(self, filter_type, message):
        super().__init__()
        self.filter_type = filter_type
        self.message = message

    def __str__(self):
        return self.message


class EntryFilter(object):
    """Filters a list of entries. """

    def __init__(self):
        self.value = None

    def set(self, value):
        """Set the filter.

        Subclasses should check for validity of the value in this method.
        """
        if value == self.value:
            return False
        self.value = value
        return True

    def _include_entry(self, entry):
        raise NotImplementedError

    def _filter(self, entries, _):
        return [entry for entry in entries if self._include_entry(entry)]

    def apply(self, entries, options):
        """Apply filter.

        Args:
            entries: a list of entries.
            options: an options_map.

        Returns:
            A list of filtered entries.

        """
        if self.value:
            return self._filter(entries, options)
        else:
            return entries

    def __bool__(self):
        return bool(self.value)


class FromFilter(EntryFilter):  # pylint: disable=abstract-method
    """Filter by a FROM expression in the Beancount Query Language."""

    def __init__(self):
        super().__init__()
        self.parser = query_parser.Parser()
        self.env_entries = query_env.FilterEntriesEnvironment()
        self.c_from = None

    def set(self, value):
        if value == self.value:
            return False
        self.value = value
        if not self.value:
            return True
        try:
            from_clause = self.parser.parse(
                'select * from ' + value).from_clause
            self.c_from = query_compile.compile_from(
                from_clause, self.env_entries)
        except (query_compile.CompilationError,
                query_parser.ParseError) as exception:
            raise FilterException('from', str(exception))
        return True

    def _filter(self, entries, options):
        return query_execute.filter_entries(self.c_from, entries, options)


class TimeFilter(EntryFilter):  # pylint: disable=abstract-method
    """Filter by dates."""

    def __init__(self):
        super().__init__()
        self.begin_date = None
        self.end_date = None

    def set(self, value):
        if value == self.value:
            return False
        self.value = value
        if not self.value:
            return True
        try:
            self.begin_date, self.end_date = parse_date(self.value)
        except TypeError:
            raise FilterException('time', 'Failed to parse date: {}'
                                  .format(self.value))
        return True

    def _filter(self, entries, options):
        entries, _ = summarize.clamp_opt(entries, self.begin_date,
                                         self.end_date, options)
        return entries


class TagFilter(EntryFilter):
    """Filter by tags and links.

    Only keeps entries that can have tags and links.
    """

    def __init__(self):
        super().__init__()
        self.tags = set()
        self.links = set()

    def set(self, value):
        if value == self.value:
            return False
        self.value = value
        if not self.value:
            return True
        self.tags = set()
        self.links = set()
        for tag_or_link in [t.strip() for t in value.split(',')]:
            if tag_or_link.startswith('#'):
                self.tags.add(tag_or_link[1:])
            if tag_or_link.startswith('^'):
                self.links.add(tag_or_link[1:])
        return True

    def _include_entry(self, entry):
        return hasattr(entry, 'tags') and (
            ((entry.tags if entry.tags else set()) & self.tags) or
            ((entry.links if entry.links else set()) & self.links)
        )


def _match(search, string):
    try:
        return re.match(search, string) or search == string
    except re.error:
        return search == string


def _match_account(name, search):
    return (account.has_component(name, search) or
            _match(search, name))


class AccountFilter(EntryFilter):
    """Filter by account.

    The filter string can either a regular expression or a parent account.
    """

    def _include_entry(self, entry):
        if isinstance(entry, Transaction):
            return any(_match_account(posting.account, self.value)
                       for posting in entry.postings)
        else:
            return (hasattr(entry, 'account') and
                    _match_account(entry.account, self.value))


class PayeeFilter(EntryFilter):
    """Filter by payee.

    The filter string can either a regular expression or a full payee name.
    """

    def _include_entry(self, entry):
        return isinstance(entry, Transaction) and \
            _match(self.value, entry.payee or '')
