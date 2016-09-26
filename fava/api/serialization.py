from datetime import date, datetime

from beancount.core import realization
from beancount.core.amount import Amount, decimal
from beancount.core.data import Close, TxnPosting
from beancount.core.position import Position
from flask.json import JSONEncoder


class BeanJSONEncoder(JSONEncoder):
    def default(self, o):  # pylint: disable=E0202
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


def serialize_inventory(inventory, at_cost=False):
    """Renders an Inventory to a currency -> amount dict."""
    if at_cost:
        inventory = inventory.cost()
    else:
        inventory = inventory.units()
    return {p.units.currency: p.units.number for p in inventory}


def serialize_real_account(real_account):
    return {
        'account': real_account.account,
        'balance_children':
            serialize_inventory(realization.compute_balance(real_account),
                                at_cost=True),
        'balance': serialize_inventory(real_account.balance, at_cost=True),
        'is_leaf': len(real_account) == 0 or bool(real_account.txn_postings),
        'is_closed': isinstance(realization.find_last_active_posting(
            real_account.txn_postings), Close),
        'has_transactions': any(isinstance(t, TxnPosting)
                                for t in real_account.txn_postings),
        'children': [serialize_real_account(a)
                     for n, a in sorted(real_account.items())],
    }


def zip_real_accounts(ra_list):
    if not ra_list:
        return
    first = ra_list[0]
    return {
        'account': first.account,
        'balance_and_balance_children':
            [(serialize_inventory(ra.balance, at_cost=True),
              serialize_inventory(realization.compute_balance(ra),
                                  at_cost=True))
             for ra in ra_list],
        'children': [zip_real_accounts([realization.get(ra, n)
                                        for ra in ra_list])
                     for n, a in sorted(first.items())],
    }
