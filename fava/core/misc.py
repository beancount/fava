"""Some miscellaneous reports."""

import datetime

from beancount.core.data import Custom, Event
from beancount.utils.misc_utils import filter_type

from fava.core.helpers import FavaModule


# pylint: disable=too-few-public-methods
class FavaMisc(FavaModule):
    """Provides access to some miscellaneous reports."""

    def __init__(self, ledger):
        super().__init__(ledger)
        self.sidebar_links = None
        self.upcoming_events = None

    def load_file(self):
        custom_entries = list(filter_type(self.ledger.all_entries, Custom))
        self.sidebar_links = _sidebar_links(custom_entries)

        self.upcoming_events = _upcoming_events(
            self.ledger.all_entries,
            self.ledger.fava_options['upcoming-events'])


def _sidebar_links(custom_entries):
    """Parse custom entries for links.

    They have the following format:

    2016-04-01 custom "fava-sidebar-link" "2014" "/income_statement/?time=2014"
    """
    sidebar_link_entries = [
        entry for entry in custom_entries
        if entry.type == 'fava-sidebar-link']
    return [(entry.values[0].value, entry.values[1].value)
            for entry in sidebar_link_entries]


def _upcoming_events(entries, max_delta):
    """Parse entries for upcoming events.

    Args:
        entries: A list of entries.
        max_delta: Number of days that should be considered.

    Returns:
        A list of the Events in entries that are less than `max_delta` days
        away.

    """
    today = datetime.date.today()
    upcoming_events = []

    for event in filter_type(entries, Event):
        delta = event.date - today
        if delta.days >= 0 and delta.days < max_delta:
            upcoming_events.append(event)

    return upcoming_events
