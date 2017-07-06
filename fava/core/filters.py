"""Entry filters."""

import re

from beancount.core import account
from beancount.core.data import Custom, Transaction
from beancount.ops import summarize
from beancount.query import (
    query_compile, query_env, query_execute, query_parser)

from fava.util.date import parse_date
from fava.core.helpers import FilterException


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
        self.exclude_tags = set()
        self.links = set()
        self.exclude_links = set()

    def set(self, value):
        if value == self.value:
            return False
        self.value = value
        if not self.value:
            return True
        self.tags = set()
        self.exclude_tags = set()
        self.links = set()
        self.exclude_links = set()
        for tag_or_link in [t.strip() for t in value.split(',')]:
            if tag_or_link.startswith('#'):
                self.tags.add(tag_or_link[1:])
            if tag_or_link.startswith('-#'):
                self.exclude_tags.add(tag_or_link[2:])
            if tag_or_link.startswith('^'):
                self.links.add(tag_or_link[1:])
            if tag_or_link.startswith('-^'):
                self.exclude_links.add(tag_or_link[2:])
        return True

    def _include_entry(self, entry):
        include = hasattr(entry, 'tags') and (
            (entry.tags & self.tags) or
            (entry.links & self.links)
        ) if self.tags else True

        exclude = hasattr(entry, 'tags') and (
            (entry.tags & self.exclude_tags) or
            (entry.links & self.exclude_links)
        )

        return include and not exclude


def _match(search, string):
    try:
        return re.match(search, string) or search == string
    except re.error:
        return search == string


def entry_account_predicate(entry, predicate):
    """Predicate for filtering by account.

    Args:
        entry: An entry.
        predicate: A predicate for account names.

    Returns:
        True if predicate is True for any account of the entry.
    """

    if isinstance(entry, Transaction):
        return any(predicate(posting.account) for posting in entry.postings)
    if isinstance(entry, Custom):
        return any(predicate(val.value)
                   for val in entry.values if val.dtype == account.TYPE)
    return hasattr(entry, 'account') and predicate(entry.account)


class AccountFilter(EntryFilter):
    """Filter by account.

    The filter string can either a regular expression or a parent account.
    """

    def _account_predicate(self, name):
        return (account.has_component(name, self.value) or
                _match(self.value, name))

    def _include_entry(self, entry):
        return entry_account_predicate(entry, self._account_predicate)


class PayeeFilter(EntryFilter):
    """Filter by payee.

    The filter string can either a regular expression or a full payee name.
    """

    def _include_entry(self, entry):
        return isinstance(entry, Transaction) and \
            _match(self.value, entry.payee or '')
