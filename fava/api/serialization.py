from datetime import date, datetime

from beancount.core import compare, realization
from beancount.core.data import Balance, Close, Transaction, TxnPosting
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
    _add_metadata(new_entry, entry)

    if isinstance(entry, Transaction):
        if entry.flag in transaction_types:
            new_entry['transaction_type'] = transaction_types[entry.flag]
        else:
            new_entry['transaction_type'] = 'other'

        new_entry['tags'] = entry.tags or []
        new_entry['links'] = entry.links or []
        new_entry['postings'] = [serialize_posting(p) for p in entry.postings]

    return new_entry


def serialize_entry_with(entry, change, balance):
    new_entry = serialize_entry(entry)
    if isinstance(entry, Balance):
        new_entry['change'] = {}
        if entry.diff_amount:
            new_entry['change'] = {entry.diff_amount.currency:
                                   entry.diff_amount.number}
        new_entry['balance'] = serialize_inventory(balance)

    if isinstance(entry, Transaction):
        new_entry['change'] = serialize_inventory(change)
        new_entry['balance'] = serialize_inventory(balance)

    return new_entry


def serialize_inventory(inventory, at_cost=False):
    """Renders an Inventory to a currency -> amount dict."""
    if at_cost:
        inventory = inventory.cost()
    else:
        inventory = inventory.units()
    return {p.units.currency: p.units.number
            for p in inventory if p.units.number != ZERO}


def serialize_posting(posting):
    new_posting = posting._asdict()

    if posting.flag in transaction_types:
        new_posting['posting_type'] = transaction_types[posting.flag]
    elif posting.flag:
        new_posting['posting_type'] = 'other'

    _add_metadata(new_posting, posting)
    return new_posting


def serialize_real_account(ra):
    return {
        'account': ra.account,
        'balance_children':
            serialize_inventory(realization.compute_balance(ra),
                                at_cost=True),
        'balance': serialize_inventory(ra.balance, at_cost=True),
        'is_leaf': len(ra) == 0 or bool(ra.txn_postings),
        'is_closed': isinstance(realization.find_last_active_posting(
            ra.txn_postings), Close),
        'has_transactions': any(isinstance(t, TxnPosting)
                                for t in ra.txn_postings),
        'children': [serialize_real_account(a) for n, a in sorted(ra.items())],
    }


def _add_metadata(new_entry, entry):
    new_entry['meta'] = {
        'type': entry.__class__.__name__.lower(),
    }
    new_entry['hash'] = compare.hash_entry(entry)

    if entry.meta:
        new_entry['meta']['filename'] = entry.meta['filename']
        new_entry['meta']['lineno'] = entry.meta['lineno']

        new_entry['metadata'] = entry.meta.copy()
        new_entry['metadata'].pop("__tolerances__", None)
        new_entry['metadata'].pop("__automatic__", None)
        new_entry['metadata'].pop("filename", None)
        new_entry['metadata'].pop("lineno", None)

    return new_entry
