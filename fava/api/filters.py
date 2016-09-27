import re

from beancount.core import account
from beancount.core.data import Transaction
from beancount.ops import summarize
from beancount.query import (
    query_compile, query_env, query_execute, query_parser)
from fava.util.date import parse_date


class FilterException(Exception):
    def __init__(self, filter_type, msg):
        super().__init__()
        self.filter_type = filter_type
        self.msg = msg

    def __str__(self):
        return self.msg


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
        if self.value:
            return self._filter(entries, options)
        else:
            return entries

    def __bool__(self):
        return bool(self.value)


class FromFilter(EntryFilter):
    """Filter by a FROM expression in the Beancount Query Language. """
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


class TimeFilter(EntryFilter):
    """Filter by dates. """

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
    """Filter by tags.

    Only keeps entries that might have tags (transactions only).
    """

    def __init__(self):
        super().__init__()
        self.tags = set()

    def set(self, value):
        if value == self.value:
            return False
        self.value = value
        if not self.value:
            return True
        self.tags = set([t.strip() for t in value.split(',')])
        if '' in self.tags:
            self.tags.remove('')
        return True

    def _include_entry(self, entry):
        return isinstance(entry, Transaction) and \
            entry.tags and (entry.tags & self.tags)


def _match_account(name, search):
    return (account.has_component(name, search) or
            re.match(search, name))


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
    """Filter by payee. """

    def __init__(self):
        super().__init__()
        self.payees = []

    def set(self, value):
        if value == self.value:
            return False
        self.value = value
        if not self.value:
            return True
        self.payees = [p.strip() for p in value.split(',')]
        if '' in self.payees and len(self.payees) == 1:
            self.payees.remove('')
        return True

    def _include_entry(self, entry):
        return isinstance(entry, Transaction) and \
            ((entry.payee and (entry.payee in self.payees)) or
             (not entry.payee and ('' in self.payees)))
