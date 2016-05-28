from beancount.core import account
from beancount.core.data import Transaction
from beancount.ops import summarize
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


class AccountFilter(EntryFilter):
    def _include_entry(self, entry):
        if isinstance(entry, Transaction):
            return any(account.has_component(posting.account, self.value)
                       for posting in entry.postings)
        else:
            return (hasattr(entry, 'account') and
                    account.has_component(entry.account, self.value))


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
