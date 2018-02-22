"""(De)serialisation of entries.

When adding entries, these are saved via the JSON API - using the functionality
of this module to obtain the appropriate data structures from
`beancount.core.data`. Similarly, for the full entry completion, a JSON
representation of the entry is provided.

This is not intended to work well enough for full roundtrips yet.
"""

from beancount.core import data
from beancount.core.amount import Amount
from beancount.core.interpolate import AUTOMATIC_META
from beancount.core.number import D

from fava import util
from fava.core.helpers import FavaAPIException
from fava.core.misc import extract_tags_links


def _parse_number(num):
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


def deserialise(json_entry, valid_accounts):
    """Parse JSON to a Beancount entry."""
    # pylint: disable=not-callable
    date = util.date.parse_date(json_entry['date'])[0]
    if json_entry['type'] == 'Transaction':
        narration, tags, links = extract_tags_links(json_entry['narration'])
        txn = data.Transaction(json_entry['metadata'], date,
                               json_entry['flag'], json_entry['payee'],
                               narration, tags, links, [])

        if not json_entry.get('postings'):
            raise FavaAPIException('Transaction contains no postings.')

        for posting in json_entry['postings']:
            if posting['account'] not in valid_accounts:
                raise FavaAPIException('Unknown account: {}.'.format(
                    posting['account']))
            data.create_simple_posting(txn, posting['account'],
                                       _parse_number(posting.get('number')),
                                       posting.get('currency'))

        return txn
    elif json_entry['type'] == 'Balance':
        if json_entry['account'] not in valid_accounts:
            raise FavaAPIException('Unknown account: {}.'.format(
                json_entry['account']))
        number = _parse_number(json_entry['number'])
        amount = Amount(number, json_entry.get('currency'))

        return data.Balance(json_entry['metadata'], date,
                            json_entry['account'], amount, None, None)
    elif json_entry['type'] == 'Note':
        if json_entry['account'] not in valid_accounts:
            raise FavaAPIException('Unknown account: {}.'.format(
                json_entry['account']))

        if '"' in json_entry['comment']:
            raise FavaAPIException('Note contains double-quotes (")')

        return data.Note(json_entry['metadata'], date, json_entry['account'],
                         json_entry['comment'])
    else:
        raise FavaAPIException('Unsupported entry type.')
