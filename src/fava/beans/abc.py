"""Abstract base classes for Beancount types."""  # noqa: A005

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import TYPE_CHECKING

from beancount.core import amount
from beancount.core import data
from beancount.core import position

if TYPE_CHECKING:  # pragma: no cover
    import datetime
    from collections.abc import Mapping
    from collections.abc import Sequence
    from decimal import Decimal
    from typing import TypeAlias

    from fava.beans import protocols

    MetaValue: TypeAlias = (
        str | int | bool | Decimal | datetime.date | protocols.Amount
    )
    Meta: TypeAlias = Mapping[str, MetaValue]
    TagsOrLinks: TypeAlias = set[str] | frozenset[str]
    Account = str


class Amount(ABC):
    """An amount in some currency."""

    @property
    @abstractmethod
    def number(self) -> Decimal:
        """Number of units in the amount."""

    @property
    @abstractmethod
    def currency(self) -> str:
        """Currency of the amount."""


Amount.register(amount.Amount)


class Cost(ABC):
    """A cost (basically an amount with date and label)."""

    @property
    @abstractmethod
    def number(self) -> Decimal:
        """Number of units in the cost."""

    @property
    @abstractmethod
    def currency(self) -> str:
        """Currency of the cost."""

    @property
    @abstractmethod
    def date(self) -> datetime.date:
        """Date of the cost."""

    @property
    @abstractmethod
    def label(self) -> str | None:
        """Label of the cost."""


Cost.register(position.Cost)


class Position(ABC):
    """A Beancount position - just cost and units."""

    @property
    @abstractmethod
    def units(self) -> Amount:
        """Units of the posting."""

    @property
    @abstractmethod
    def cost(self) -> Cost | None:
        """Units of the position."""


Position.register(position.Position)


class Posting(Position):
    """A Beancount posting."""

    @property
    @abstractmethod
    def account(self) -> str:
        """Account of the posting."""

    @property
    @abstractmethod
    def units(self) -> Amount:
        """Units of the posting."""

    @property
    @abstractmethod
    def cost(self) -> Cost | None:
        """Units of the posting."""

    @property
    @abstractmethod
    def price(self) -> Amount | None:
        """Price of the posting."""

    @property
    @abstractmethod
    def meta(self) -> Meta | None:
        """Metadata of the posting."""

    @property
    @abstractmethod
    def flag(self) -> str | None:
        """Flag of the posting."""


Posting.register(data.Posting)


class Directive(ABC):
    """A Beancount directive."""

    @property
    @abstractmethod
    def date(self) -> datetime.date:
        """Metadata of the directive."""

    @property
    @abstractmethod
    def meta(self) -> Meta:
        """Metadata of the directive."""


class Transaction(Directive):
    """A Beancount Transaction directive."""

    @property
    @abstractmethod
    def flag(self) -> str:
        """Flag of the transaction."""

    @property
    @abstractmethod
    def payee(self) -> str:
        """Payee of the transaction."""

    @property
    @abstractmethod
    def narration(self) -> str:
        """Narration of the transaction."""

    @property
    @abstractmethod
    def postings(self) -> Sequence[Posting]:
        """Payee of the transaction."""

    @property
    @abstractmethod
    def tags(self) -> TagsOrLinks:
        """Entry tags."""

    @property
    @abstractmethod
    def links(self) -> TagsOrLinks:
        """Entry links."""


class Balance(Directive):
    """A Beancount Balance directive."""

    @property
    @abstractmethod
    def account(self) -> str:
        """Account of the directive."""

    @property
    @abstractmethod
    def diff_amount(self) -> Amount | None:
        """Account of the directive."""


class Commodity(Directive):
    """A Beancount Commodity directive."""

    @property
    @abstractmethod
    def currency(self) -> str:
        """Currency."""


class Close(Directive):
    """A Beancount Close directive."""

    @property
    @abstractmethod
    def account(self) -> str:
        """Account of the directive."""


class Custom(Directive):
    """A Beancount Custom directive."""

    @property
    @abstractmethod
    def type(self) -> str:
        """Directive type."""

    @property
    @abstractmethod
    def values(self) -> Sequence[Any]:
        """Custom values."""


class Document(Directive):
    """A Beancount Document directive."""

    @property
    @abstractmethod
    def filename(self) -> str:
        """Filename of the document."""

    @property
    @abstractmethod
    def account(self) -> str:
        """Account of the directive."""

    @property
    @abstractmethod
    def tags(self) -> TagsOrLinks:
        """Entry tags."""

    @property
    @abstractmethod
    def links(self) -> TagsOrLinks:
        """Entry links."""


class Event(Directive):
    """A Beancount Event directive."""

    @property
    @abstractmethod
    def account(self) -> str:
        """Account of the directive."""


class Note(Directive):
    """A Beancount Note directive."""

    @property
    @abstractmethod
    def account(self) -> str:
        """Account of the directive."""

    @property
    @abstractmethod
    def comment(self) -> str:
        """Note comment."""


class Open(Directive):
    """A Beancount Open directive."""

    @property
    @abstractmethod
    def account(self) -> str:
        """Account of the directive."""

    @property
    @abstractmethod
    def currencies(self) -> Sequence[str]:
        """Valid currencies for the account."""

    @property
    @abstractmethod
    def booking(self) -> data.Booking | None:
        """Booking method for the account."""


class Pad(Directive):
    """A Beancount Pad directive."""

    @property
    @abstractmethod
    def account(self) -> str:
        """Account of the directive."""

    @property
    @abstractmethod
    def source_account(self) -> str:
        """Source account of the pad."""


class Price(Directive):
    """A Beancount Price directive."""

    @property
    @abstractmethod
    def currency(self) -> str:
        """Currency for which this is a price."""

    @property
    @abstractmethod
    def amount(self) -> Amount:
        """Price amount."""


class Query(Directive):
    """A Beancount Query directive."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of this query."""

    @property
    @abstractmethod
    def query_string(self) -> str:
        """BQL query."""


class TxnPosting(ABC):
    """A transaction and a posting."""

    @property
    @abstractmethod
    def txn(self) -> Transaction:
        """Transaction."""

    @property
    @abstractmethod
    def posting(self) -> Posting:
        """Posting."""


Balance.register(data.Balance)
Commodity.register(data.Commodity)
Close.register(data.Close)
Custom.register(data.Custom)
Document.register(data.Document)
Event.register(data.Event)
Note.register(data.Note)
Open.register(data.Open)
Pad.register(data.Pad)
Price.register(data.Price)
Transaction.register(data.Transaction)
Query.register(data.Query)
