import datetime
from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from collections.abc import Sequence

from fava.beans.abc import Account
from fava.beans.abc import Directive

class Importer(ABC):
    @property
    def name(self) -> str: ...
    @abstractmethod
    def identify(self, filepath: str) -> bool: ...
    @abstractmethod
    def account(self, filepath: str) -> Account: ...
    def date(self, filepath: str) -> datetime.date | None: ...
    def filename(self, filepath: str) -> str | None: ...
    def extract(
        self, filepath: str, existing: Sequence[Directive]
    ) -> list[Directive]: ...
    def deduplicate(
        self, entries: list[Directive], existing: Sequence[Directive]
    ) -> None: ...
    def sort(
        self, entries: list[Directive], reverse: bool = False
    ) -> None: ...

class Ingest:
    def __init__(
        self,
        importer: Sequence[Importer],
        hooks: Sequence[
            Callable[
                [
                    Sequence[
                        tuple[str, Sequence[Directive], str, Importer]
                    ],  # new_entries
                    Sequence[Directive],  # existing_entries
                ],
                Sequence[
                    tuple[str, Sequence[Directive], str, Importer]
                ],  # (return value)
            ]
        ],
    ) -> None: ...
    def __call__(self) -> None: ...
