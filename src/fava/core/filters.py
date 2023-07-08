"""Entry filters."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

import uromyces
from beancount.core import account
from beancount.ops.summarize import clamp_opt

from fava.beans.account import get_entry_accounts
from fava.core.filter_parser import Match
from fava.core.filter_parser import parse_filter
from fava.helpers import FavaAPIError
from fava.util.date import InvalidDateRangeError
from fava.util.date_parser import parse_date
from fava.util.parsing import ParseError

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Sequence

    from uromyces._uromyces import UromycesOptions

    from fava.beans.abc import Directive
    from fava.beans.types import BeancountOptions
    from fava.core.fava_options import FavaOptions
    from fava.util.date import DateRange


class FilterError(FavaAPIError):
    """Filter exception."""


class TimeFilterParseError(FilterError):
    """Time filter parse error."""

    def __init__(self, value: str, err: Exception) -> None:
        super().__init__(f"Failed to parse date '{value}': {err!s}")


class AdvancedFilterParseError(FilterError):
    """Filter parse error."""

    def __init__(self, value: str, err: Exception) -> None:
        super().__init__(f"Failed to parse filter '{value}': {err!s}")


class EntryFilter(ABC):
    """Filters a list of entries."""

    @abstractmethod
    def apply(self, entries: Sequence[Directive]) -> Sequence[Directive]:
        """Filter a list of directives."""


class TimeFilter(EntryFilter):
    """Filter by dates."""

    __slots__ = ("_options", "_uro_options", "date_range")

    date_range: DateRange

    def __init__(
        self,
        options: BeancountOptions,
        fava_options: FavaOptions,
        value: str,
        uro_options: UromycesOptions | None,
    ) -> None:
        self._options = options
        self._uro_options = uro_options
        try:
            self.date_range = parse_date(value, fava_options.fiscal_year_end)
        except (ParseError, InvalidDateRangeError) as error:
            raise TimeFilterParseError(value, error) from error

    def apply(self, entries: Sequence[Directive]) -> Sequence[Directive]:
        """Filter and summarise the entries in the date range."""
        if self._uro_options:
            return uromyces.summarize_clamp(
                entries,  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]
                self.date_range.begin,
                self.date_range.end,
                self._uro_options,
            )
        clamped_entries, _ = clamp_opt(
            entries,  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]
            self.date_range.begin,
            self.date_range.end,
            self._options,
        )
        return clamped_entries  # type: ignore[return-value]  # ty:ignore[invalid-return-type]


class AdvancedFilter(EntryFilter):
    """Filter by tags and links and keys."""

    __slots__ = ("_include",)

    def __init__(self, value: str) -> None:
        try:
            self._include = parse_filter(value)
        except ParseError as error:
            raise AdvancedFilterParseError(value, error) from error

    def apply(self, entries: Sequence[Directive]) -> Sequence[Directive]:
        """Filter the entries matching the filter expression."""
        include = self._include
        return [entry for entry in entries if include(entry)]


class AccountFilter(EntryFilter):
    """Filter by account.

    The filter string can either be a regular expression or a parent account.
    """

    __slots__ = ("_match", "_value")

    def __init__(self, value: str) -> None:
        self._value = value
        self._match = Match(value)

    def apply(self, entries: Sequence[Directive]) -> Sequence[Directive]:
        """Filter the entries with a posting to a matching account."""
        value = self._value
        if not value:
            return entries
        match = self._match
        return [
            entry
            for entry in entries
            if any(
                account.has_component(name, value) or match(name)
                for name in get_entry_accounts(entry)
            )
        ]
