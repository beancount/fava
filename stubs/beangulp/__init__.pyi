import datetime
from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from collections.abc import Sequence

from beancount.core import data

from fava.beans.abc import Account

class Importer(ABC):
    @property
    def name(self) -> str: ...
    @abstractmethod
    def identify(self, filepath: str) -> bool: ...
    @abstractmethod
    def account(self, filepath: str) -> Account: ...
    def date(self, filepath: str) -> datetime.date | None: ...
    def filename(self, filepath: str) -> str | None: ...
    def extract(self, filepath: str, existing: data.Entries) -> data.Entries: ...
    def deduplicate(
        self, entries: data.Entries, existing: data.Entries
    ) -> None: ...
    def sort(self, entries: data.Entries, reverse: bool = False) -> None: ...

class Ingest:
    def __init__(
        self,
        importer: Sequence[Importer],
        hooks: Sequence[
            Callable[
                [
                    Sequence[
                        tuple[str, data.Entries, str, Importer]
                    ],  # new_entries
                    data.Entries,  # existing_entries
                ],
                Sequence[
                    tuple[str, data.Entries, str, Importer]
                ],  # (return value)
            ]
        ],
    ) -> None: ...
    def __call__(self) -> None: ...
