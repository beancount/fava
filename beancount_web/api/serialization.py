import decimal
from datetime import date, datetime

from beancount.core import interpolate, compare
from beancount.core.data import Balance, Transaction, Price
from beancount.core.amount import Amount
from beancount.core.position import Position
from beancount.core.number import ZERO
from flask.json import JSONEncoder


class BeanJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        elif isinstance(o, decimal.Decimal):
            return float(o)
        elif isinstance(o, Amount):
            return str(o)
        elif isinstance(o, Position):
            return str(o)
        elif isinstance(o, (set, frozenset)):
            return list(o)
        return JSONEncoder.default(self, o)


def serialize_entry(posting):
    entry = posting._asdict()
    entry['meta'] = {
        'type': posting.__class__.__name__.lower(),
        'filename': posting.meta['filename'],
        'lineno': posting.meta['lineno'],
    }
    entry.update({
        'hash': compare.hash_entry(posting),
        'metadata': posting.meta.copy()
    })

    entry['metadata'].pop("__tolerances__", None)
    entry['metadata'].pop("filename", None)
    entry['metadata'].pop("lineno", None)

    if isinstance(posting, Price):
        entry['amount'] = {posting.amount.currency: posting.amount.number}

    if isinstance(posting, Balance):
        entry['amount'] = {posting.amount.currency: posting.amount.number}

        if posting.diff_amount:
            entry['diff_amount'] = {posting.diff_amount.currency: posting.diff_amount.number}
            entry['balance'] = {posting.amount.currency: posting.diff_amount.number + posting.amount.number}

    if isinstance(posting, Transaction):
        if posting.flag == 'P':
            entry['meta']['type'] = 'padding'  # TODO handle Padding, Summarize and Transfer

        entry.pop('postings', None)
        entry['tags'] = posting.tags or []
        entry['links'] = posting.links or []
        entry['legs'] = [serialize_posting(p) for p in posting.postings]

    return entry


def serialize_inventory(inventory, at_cost=False):
    """Renders an Inventory to a currency -> amount dict."""
    if at_cost:
        inventory = inventory.cost()
    else:
        inventory = inventory.units()
    return {p.units.currency: p.units.number for p in inventory if p.units.number != ZERO}


def serialize_posting(posting):
    return posting._asdict()
