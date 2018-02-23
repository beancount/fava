"""(De)serialisation of entries.

When adding entries, these are saved via the JSON API - using the functionality
of this module to obtain the appropriate data structures from
`beancount.core.data`. Similarly, for the full entry completion, a JSON
representation of the entry is provided.

This is not intended to work well enough for full roundtrips yet.
"""

import re

from beancount.core import data
from beancount.core.amount import Amount
from beancount.core.interpolate import AUTOMATIC_META
from beancount.core.number import D

from fava import util
from fava.core.helpers import FavaAPIException


def extract_tags_links(string):
    """Extract tags and links from a narration string.

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


def parse_number(num):
    """Parse a number as entered in an entry form, supporting division."""
    if not num:
        return None
    if '/' in num:
        left, right = num.split('/')
        return D(left) / D(right)
    return D(num)


def serialise(entry):
    """Serialise an entry."""
    if not entry:
        return None
    ret = entry._asdict()
    ret['type'] = entry.__class__.__name__
    if ret['type'] == 'Transaction':
        if entry.tags:
            ret['narration'] += ' ' + ' '.join(['#' + t for t in entry.tags])
        if entry.links:
            ret['narration'] += ' ' + ' '.join(['^' + l for l in entry.links])
        ret['postings'] = []
        for posting in entry.postings:
            pos = dict(posting._asdict())
            if posting.meta and posting.meta.get(AUTOMATIC_META):
                pos['units'] = None
            ret['postings'].append(pos)
    return ret


def deserialise(json_entry):
    """Parse JSON to a Beancount entry.

    Args:
        json_entry: The entry.

    Raises:
        KeyError: if one of the required entry fields is missing.
        FavaAPIException: if the type of the given entry is not supported.
    """
    # pylint: disable=not-callable
    if json_entry['type'] == 'Transaction':
        date = util.date.parse_date(json_entry['date'])[0]
        narration, tags, links = extract_tags_links(json_entry['narration'])
        txn = data.Transaction(json_entry['meta'], date, json_entry['flag'],
                               json_entry['payee'], narration, tags, links, [])

        for posting in json_entry['postings']:
            data.create_simple_posting(txn, posting['account'],
                                       parse_number(posting.get('number')),
                                       posting.get('currency'))

        return txn
    elif json_entry['type'] == 'Balance':
        date = util.date.parse_date(json_entry['date'])[0]
        number = parse_number(json_entry['number'])
        amount = Amount(number, json_entry.get('currency'))

        return data.Balance(json_entry['meta'], date, json_entry['account'],
                            amount, None, None)
    elif json_entry['type'] == 'Note':
        date = util.date.parse_date(json_entry['date'])[0]
        if '"' in json_entry['comment']:
            raise FavaAPIException('Note contains double-quotes (")')

        return data.Note(json_entry['meta'], date, json_entry['account'],
                         json_entry['comment'])
    else:
        raise FavaAPIException('Unsupported entry type.')
