"""Account close date and metadata."""
import datetime

from beancount.core.data import Meta


class AccountData:
    """Holds information about an account."""

    __slots__ = ("meta", "close_date")

    def __init__(self) -> None:
        #: The date on which this account is closed (or datetime.date.max).
        self.close_date = datetime.date.max

        #: The metadata of the Open entry of this account.
        self.meta: Meta = {}


class AccountDict(dict):
    """Account info dictionary."""

    EMPTY = AccountData()

    def __missing__(self, key: str) -> AccountData:
        return self.EMPTY

    def setdefault(self, key: str, _=None) -> AccountData:
        if key not in self:
            self[key] = AccountData()
        return self[key]
