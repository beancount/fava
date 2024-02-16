"""Types for Beancount importers."""

from __future__ import annotations

from typing import Protocol
from typing import runtime_checkable
from typing import TYPE_CHECKING
from typing import TypeVar

if TYPE_CHECKING:  # pragma: no cover
    import datetime
    from collections.abc import Callable

    from fava.beans.abc import Directive


T = TypeVar("T")


class FileMemo(Protocol):
    """The file with caching support that is passed to importers."""

    name: str

    def convert(self, converter_func: Callable[[str], T]) -> T:
        """Run a conversion function for the file."""

    def mimetype(self) -> str:
        """Get the mimetype of the file."""

    def contents(self) -> str:
        """Get the file contents."""


@runtime_checkable
class BeanImporterProtocol(Protocol):
    """Interface for Beancount importers.

    typing.Protocol version of beancount.ingest.importer.ImporterProtocol

    Importers can subclass from this one instead of the Beancount one to
    get type checking for the methods.
    """

    def name(self) -> str:
        """Return a unique id/name for this importer."""
        cls = self.__class__
        return f"{cls.__module__}.{cls.__name__}"

    def identify(self, file: FileMemo) -> bool:
        """Return true if this importer matches the given file."""

    def extract(
        self,
        file: FileMemo,  # noqa: ARG002
        *,
        existing_entries: list[Directive] | None = None,  # noqa: ARG002
    ) -> list[Directive] | None:
        """Extract transactions from a file."""
        return None

    def file_account(self, file: FileMemo) -> str:
        """Return an account associated with the given file."""

    def file_name(self, file: FileMemo) -> str | None:  # noqa: ARG002
        """A filter that optionally renames a file before filing."""
        return None

    def file_date(
        self,
        file: FileMemo,  # noqa: ARG002
    ) -> datetime.date | None:
        """Attempt to obtain a date that corresponds to the given file."""
        return None
