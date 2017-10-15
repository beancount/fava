"""Some miscellaneous reports."""

from collections import namedtuple
import datetime
import re

from beancount.core.data import Custom, Event

from fava.core.helpers import FavaModule

FavaError = namedtuple('FavaError', 'source message entry')


class FavaMisc(FavaModule):
    """Provides access to some miscellaneous reports."""

    # pylint: disable=too-few-public-methods

    def __init__(self, ledger):
        super().__init__(ledger)
        self.sidebar_links = None
        self.upcoming_events = None

    def load_file(self):
        custom_entries = self.ledger.all_entries_by_type[Custom]
        self.sidebar_links = _sidebar_links(custom_entries)

        self.upcoming_events = _upcoming_events(
            self.ledger.all_entries_by_type[Event],
            self.ledger.fava_options['upcoming-events'])

        if not self.ledger.options['operating_currency']:
            self.ledger.errors.append(
                FavaError(None, 'No operating currency specified. '
                          'Please add one to your beancount file.', None))


def _sidebar_links(custom_entries):
    """Parse custom entries for links.

    They have the following format:

    2016-04-01 custom "fava-sidebar-link" "2014" "/income_statement/?time=2014"
    """
    sidebar_link_entries = [
        entry for entry in custom_entries if entry.type == 'fava-sidebar-link'
    ]
    return [(entry.values[0].value, entry.values[1].value)
            for entry in sidebar_link_entries]


def _upcoming_events(events, max_delta):
    """Parse entries for upcoming events.

    Args:
        events: A list of events.
        max_delta: Number of days that should be considered.

    Returns:
        A list of the Events in entries that are less than `max_delta` days
        away.
    """
    today = datetime.date.today()
    upcoming_events = []

    for event in events:
        delta = event.date - today
        if delta.days >= 0 and delta.days < max_delta:
            upcoming_events.append(event)

    return upcoming_events


def extract_tags_links(string):
    """Extract tags and links from a (narration) string.

    Args:
        string: A string, possibly containing tags (`#tag`) and links
        (`^link`).

    Returns:
        A triple (new_string, tags, links) where `new_string` is `string`
        stripped of tags and links.
    """

    tags = re.findall(r'(?:^|\s)#([A-Za-z0-9\-_/.]+)', string)
    links = re.findall(r'(?:^|\s)\^([A-Za-z0-9\-_/.]+)', string)
    new_string = re.sub(r'(?:^|\s)[#^]([A-Za-z0-9\-_/.]+)', '', string).strip()

    return new_string, frozenset(tags), frozenset(links)
