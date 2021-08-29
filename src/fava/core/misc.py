"""Some miscellaneous reports."""
import datetime
import io
import re
from typing import List
from typing import Tuple
from typing import TYPE_CHECKING

from beancount.core.amount import CURRENCY_RE
from beancount.core.data import Custom
from beancount.core.data import Event

from fava.core.module_base import FavaModule
from fava.helpers import BeancountError

if TYPE_CHECKING:
    from fava.core import FavaLedger


class FavaError(BeancountError):
    """Generic Fava-specific error."""


SidebarLinks = List[Tuple[str, str]]


class FavaMisc(FavaModule):
    """Provides access to some miscellaneous reports."""

    def __init__(self, ledger: "FavaLedger") -> None:
        super().__init__(ledger)
        #: User-chosen links to show in the sidebar.
        self.sidebar_links: SidebarLinks = []
        #: Upcoming events in the next few days.
        self.upcoming_events: List[Event] = []

    def load_file(self) -> None:
        custom_entries = self.ledger.all_entries_by_type.Custom
        self.sidebar_links = sidebar_links(custom_entries)

        self.upcoming_events = upcoming_events(
            self.ledger.all_entries_by_type.Event,
            self.ledger.fava_options["upcoming-events"],
        )

        if not self.ledger.options["operating_currency"]:
            self.ledger.errors.append(
                FavaError(
                    None,
                    "No operating currency specified. "
                    "Please add one to your beancount file.",
                    None,
                )
            )


def sidebar_links(custom_entries: List[Custom]) -> List[Tuple[str, str]]:
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


def upcoming_events(events: List[Event], max_delta: int) -> List[Event]:
    """Parse entries for upcoming events.

    Args:
        events: A list of events.
        max_delta: Number of days that should be considered.

    Returns:
        A list of the Events in entries that are less than `max_delta` days
        away.
    """
    today = datetime.date.today()
    upcoming = []

    for event in events:
        delta = event.date - today
        if delta.days >= 0 and delta.days < max_delta:
            upcoming.append(event)

    return upcoming


ALIGN_RE = re.compile(
    rf'([^";]*?)\s+([-+]?\s*[\d,]+(?:\.\d*)?)\s+({CURRENCY_RE}\b.*)'
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
