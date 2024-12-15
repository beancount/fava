"""Some miscellaneous reports."""

from __future__ import annotations

import io
import re
from typing import TYPE_CHECKING

from fava.core.module_base import FavaModule
from fava.helpers import BeancountError
from fava.util.date import local_today

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Sequence

    from fava.beans.abc import Custom
    from fava.beans.abc import Event
    from fava.core import FavaLedger

    SidebarLinks = Sequence[tuple[str, str]]


class FavaError(BeancountError):
    """Generic Fava-specific error."""


NO_OPERATING_CURRENCY_ERROR = FavaError(
    None,
    "No operating currency specified. Please add one to your beancount file.",
    None,
)


class FavaMisc(FavaModule):
    """Provides access to some miscellaneous reports."""

    def __init__(self, ledger: FavaLedger) -> None:
        super().__init__(ledger)
        #: User-chosen links to show in the sidebar.
        self.sidebar_links: SidebarLinks = []
        #: Upcoming events in the next few days.
        self.upcoming_events: Sequence[Event] = []

    def load_file(self) -> None:  # noqa: D102
        custom_entries = self.ledger.all_entries_by_type.Custom
        self.sidebar_links = sidebar_links(custom_entries)

        self.upcoming_events = upcoming_events(
            self.ledger.all_entries_by_type.Event,
            self.ledger.fava_options.upcoming_events,
        )

    @property
    def errors(self) -> Sequence[FavaError]:
        """An error if no operating currency is set."""
        return (
            []
            if self.ledger.options["operating_currency"]
            else [NO_OPERATING_CURRENCY_ERROR]
        )


def sidebar_links(custom_entries: Sequence[Custom]) -> SidebarLinks:
    """Parse custom entries for links.

    They have the following format:

    2016-04-01 custom "fava-sidebar-link" "2014" "/income_statement/?time=2014"
    """
    sidebar_link_entries = [
        entry for entry in custom_entries if entry.type == "fava-sidebar-link"
    ]
    return [
        (entry.values[0].value, entry.values[1].value)
        for entry in sidebar_link_entries
    ]


def upcoming_events(
    events: Sequence[Event], max_delta: int
) -> Sequence[Event]:
    """Parse entries for upcoming events.

    Args:
        events: A list of events.
        max_delta: Number of days that should be considered.

    Returns:
        A list of the Events in entries that are less than `max_delta` days
        away.
    """
    today = local_today()
    upcoming = []

    for event in events:
        delta = event.date - today
        if delta.days >= 0 and delta.days < max_delta:
            upcoming.append(event)

    return upcoming


CURRENCY_RE = r"[A-Z][A-Z0-9\'\.\_\-]{0,22}[A-Z0-9]"
ALIGN_RE = re.compile(
    rf'([^";]*?)\s+([-+]?\s*[\d,]+(?:\.\d*)?)\s+({CURRENCY_RE}\b.*)',
)


def align(string: str, currency_column: int) -> str:
    """Align currencies in one column."""
    output = io.StringIO()
    for line in string.splitlines():
        match = ALIGN_RE.match(line)
        if match:
            prefix, number, rest = match.groups()
            num_of_spaces = currency_column - len(prefix) - len(number) - 4
            spaces = " " * num_of_spaces
            output.write(prefix + spaces + "  " + number + " " + rest)
        else:
            output.write(line)
        output.write("\n")

    return output.getvalue()
