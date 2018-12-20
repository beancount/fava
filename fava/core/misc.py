"""Some miscellaneous reports."""

from collections import namedtuple
import datetime
import io
import re

from beancount.core.data import Custom, Event
from beancount.core import amount

from fava.core.helpers import FavaModule
from fava.core.fava_options import DEFAULTS

FavaError = namedtuple("FavaError", "source message entry")


class FavaMisc(FavaModule):
    """Provides access to some miscellaneous reports."""

    def __init__(self, ledger):
        super().__init__(ledger)
        self.sidebar_links = None
        self.upcoming_events = None

    def load_file(self):
        custom_entries = self.ledger.all_entries_by_type[Custom]
        self.sidebar_links = sidebar_links(custom_entries)

        self.upcoming_events = upcoming_events(
            self.ledger.all_entries_by_type[Event],
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


def sidebar_links(custom_entries):
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


def upcoming_events(events, max_delta):
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


def align(string, fava_options):
    """Align currencies in one column."""

    column = fava_options.get("currency-column", DEFAULTS["currency-column"])

    output = io.StringIO()
    for line in string.splitlines():
        match = re.match(
            r'([^";]*?)\s+([-+]?\s*[\d,]+(?:\.\d*)?)\s+({}\b.*)'.format(
                amount.CURRENCY_RE
            ),
            line,
        )
        if match:
            prefix, number, rest = match.groups()
            num_of_spaces = column - len(prefix) - len(number) - 4
            spaces = " " * num_of_spaces
            output.write(prefix + spaces + "  " + number + " " + rest)
        else:
            output.write(line)
        output.write("\n")

    return output.getvalue()
