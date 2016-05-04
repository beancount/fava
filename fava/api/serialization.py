from datetime import date, datetime

from beancount.core import compare, realization
from beancount.core.amount import Amount, decimal
from beancount.core.data import Balance, Close, Transaction, TxnPosting, Custom
from beancount.core.inventory import Inventory
from beancount.core.number import ZERO
from beancount.core.position import Position
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

    if isinstance(entry, Custom):
        if entry.type == 'budget':
            new_entry['meta']['type'] = 'budget'
            _serialize_budget_entry(new_entry, entry)

    return new_entry


def _serialize_budget_entry(new_entry, entry):
    # TODO validate budget entry
    new_entry['account'] = entry.values[0].value
    new_entry['period_type'] = entry.values[1].value
    new_entry['value'] = entry.values[2].value


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


def subtract_inventory_from_curr_dict(currency_dict, inventory, at_cost=False):
    """Subtracts an inventory from a dictionary of currency => number."""
    new_dict = {}

    if at_cost:
        inventory = inventory.cost()
    else:
        inventory = inventory.units()

    for currency in currency_dict:
        for q in inventory:
            if currency == q.units.currency:
                if currency not in new_dict:
                    new_dict[currency] = decimal.Decimal(0.0)
                # round to 10 decimal places to avoid representation issues
                new_dict[currency] = round(
                    currency_dict[currency] - q.units.number, 10)

    return new_dict


def serialize_real_account(ra, begin_date=None, end_date=None, budget_fn=None):
    budgets = budget_fn(ra.account, begin_date, end_date) if budget_fn \
                                                          else Inventory()
    balance_children = realization.compute_balance(ra)

    serialized_account = {
        'account': ra.account,
        'balance': serialize_inventory(ra.balance, at_cost=True),
        'balance_children': serialize_inventory(
            balance_children, at_cost=True),
        'budget': subtract_inventory_from_curr_dict(
            budgets, ra.balance, at_cost=True),
        'budget_children': subtract_inventory_from_curr_dict(
            budgets, balance_children, at_cost=True),
        'is_leaf': len(ra) == 0 or bool(ra.txn_postings),
        'is_closed': isinstance(realization.find_last_active_posting(
            ra.txn_postings), Close),
        'has_transactions': any(isinstance(t, TxnPosting)
                                for t in ra.txn_postings),
        'children': [serialize_real_account(a, begin_date, end_date, budget_fn)
                     for n, a in sorted(ra.items())],
    }

    return serialized_account


def _add_metadata(new_entry, entry):
    new_entry['meta'] = {
        'type': entry.__class__.__name__.lower(),
    }
    new_entry['hash'] = compare.hash_entry(entry)

    if entry.meta:
        new_entry['meta']['filename'] = getattr(entry.meta, 'filename', None)
        new_entry['meta']['lineno'] = getattr(entry.meta, 'lineno', None)

        new_entry['metadata'] = entry.meta.copy()
        new_entry['metadata'].pop("__tolerances__", None)
        new_entry['metadata'].pop("__automatic__", None)
        new_entry['metadata'].pop("filename", None)
        new_entry['metadata'].pop("lineno", None)

    return new_entry
