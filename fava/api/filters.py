import re

from beancount.core import account
from beancount.core.data import Transaction
from beancount.ops import summarize
from beancount.query import (
    query_compile, query_env, query_execute, query_parser)
from fava.util.date import parse_date


class FilterException(Exception):
    pass


class EntryFilter(object):
    def __init__(self):
        self.value = None

    def set(self, value):
        if value == self.value:
            return False
        self.value = value
        return True

    def _include_entry(self, entry):
        raise NotImplementedError

    def _filter(self, entries, options):
        return [entry for entry in entries if self._include_entry(entry)]

    def apply(self, entries, options):
        if self.value:
            return self._filter(entries, options)
        else:
            return entries

    def __bool__(self):
        return bool(self.value)


class FromFilter(EntryFilter):
    def __init__(self):
        self.value = None
        self.parser = query_parser.Parser()
        self.env_entries = query_env.FilterEntriesEnvironment()

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
        except Exception:
            # TODO
            raise FilterException('Failed to parse from clause: {}'
                                  .format(self.value))
        return True

    def _filter(self, entries, options):
        return query_execute.filter_entries(self.c_from, entries, options)


class DateFilter(EntryFilter):
    def set(self, value):
        if value == self.value:
            return False
        self.value = value
        if not self.value:
            return True
        try:
            self.begin_date, self.end_date = parse_date(self.value)
        except TypeError:
            raise FilterException('Failed to parse date: {}'
                                  .format(self.value))
        return True

    def _filter(self, entries, options):
        entries, _ = summarize.clamp_opt(entries, self.begin_date,
                                         self.end_date, options)
        return entries


class TagFilter(EntryFilter):
    def set(self, value):
        if value == self.value:
            return False
        self.value = value
        if not self.value:
            return True
        self.tags = [t.strip() for t in value.split(',')]
        if '' in self.tags:
            self.tags.remove('')
        return True

    def _include_entry(self, entry):
        return isinstance(entry, Transaction) and \
            entry.tags and (entry.tags & set(self.tags))


def _match_account(name, filter):
    if filter == '.*' and not re.match(filter, name):
        print(name)
    return (account.has_component(name, filter) or
            re.match(filter, name))


class AccountFilter(EntryFilter):
    def _include_entry(self, entry):
        if isinstance(entry, Transaction):
            return any(_match_account(posting.account, self.value)
                       for posting in entry.postings)
        else:
            return (hasattr(entry, 'account') and
                    _match_account(entry.account, self.value))


class PayeeFilter(EntryFilter):
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
