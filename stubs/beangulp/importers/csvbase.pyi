import csv
import datetime
import enum
from collections.abc import Sequence
from typing import Any
from typing import NamedTuple
from typing import TypeAlias

import beancount.core.amount
import beangulp
from beancount.core import data

from fava.beans.abc import Directive

Row: TypeAlias = NamedTuple

class Order(enum.Enum):
    ASCENDING = ...
    DESCENDING = ...

class Column:
    name: str
    def __init__(self, name: str) -> None: ...
    def parse(self, value: str) -> Any: ...

class Date(Column):
    format: str
    def __init__(self, name: str, frmt: str) -> None: ...
    def parse(self, value: str) -> datetime.date: ...

class Amount(Column):
    subs: dict[str, str]
    def __init__(
        self, name: str, subs: dict[str, str] | None = None
    ) -> None: ...
    def parse(self, value: str) -> beancount.core.amount.Amount: ...

class Columns(Column):
    columns: list[str]
    sep: str
    def __init__(self, *columns: str, sep: str = " ") -> None: ...
    def parse(self, value: str) -> str: ...

class CreditOrDebit(Column):
    credit_name: str
    debit_name: str
    def __init__(self, credit_name: str, debit_name: str) -> None: ...
    def parse(self, value: str) -> beancount.core.amount.Amount: ...

class CSVMeta(type): ...

class CSVReader:
    encoding: str
    skiplines: int
    names: bool
    dialect: str | csv.Dialect
    comments: str
    order: Order | None

    def read(self, filepath: str) -> list[Row]: ...

class Importer(beangulp.Importer, CSVReader):
    def __init__(
        self, account: str, currency: str, flag: str = "*"
    ) -> None: ...
    def account(self, filepath: str) -> str: ...
    def date(self, filepath: str) -> datetime.date: ...
    def extract(
        self, filepath: str, existing: Sequence[Directive]
    ) -> list[Directive]: ...
    def finalize(
        self, txn: data.Transaction, row: Row
    ) -> data.Transaction | None: ...
    def identify(self, filepath: str) -> bool: ...
    def metadata(self, filepath: str, lineno: int, row: Row) -> data.Meta: ...
