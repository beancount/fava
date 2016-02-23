from datetime import date, datetime

from beancount.core import compare
from beancount.core.data import Transaction
from beancount.core.amount import Amount, decimal
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


transaction_types = {
    '*': 'cleared',
    '!': 'pending',
    'P': 'padding',
    'S': 'summarize',
    'T': 'transfer',
}


def serialize_entry(entry):
    new_entry = entry._asdict()
    new_entry['meta'] = {
        'type': entry.__class__.__name__.lower(),
        'filename': entry.meta['filename'],
        'lineno': entry.meta['lineno'],
    }
    new_entry.update({
        'hash': compare.hash_entry(entry),
        'metadata': entry.meta.copy()
    })

    new_entry['metadata'].pop("__tolerances__", None)
    new_entry['metadata'].pop("filename", None)
    new_entry['metadata'].pop("lineno", None)

    if isinstance(entry, Transaction):
        if entry.flag in transaction_types:
            new_entry['transaction_type'] = transaction_types[entry.flag]
        else:
            new_entry['transaction_type'] = 'other'

        new_entry['tags'] = entry.tags or []
        new_entry['links'] = entry.links or []
        new_entry['postings'] = [serialize_posting(p) for p in entry.postings]

    return new_entry


def serialize_inventory(inventory, at_cost=False):
    """Renders an Inventory to a currency -> amount dict."""
    if at_cost:
        inventory = inventory.cost()
    else:
        inventory = inventory.units()
    return {p.units.currency: p.units.number for p in inventory if p.units.number != ZERO}


def serialize_posting(posting):
    return posting._asdict()
