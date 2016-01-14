from beancount.core import interpolate, compare
from beancount.core.data import Balance, Transaction, Price
from beancount.core.number import ZERO


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


def serialize_inventory(inventory, at_cost=False, include_currencies=None):
    """
    Renders an Inventory to a currency -> amount dict.

    Args:
        inventory: The inventory to render.
        include_currencies: Array of strings (eg. ['USD', 'EUR']). If set the
                            inventory will only contain those currencies.

    Returns:
        {
            'USD': 123.45,
            'CAD': 567.89,
            ...
        }
    """
    if at_cost:
        inventory = inventory.cost()
    else:
        inventory = inventory.units()
    result = {p.lot.currency: p.number for p in inventory if p.number != ZERO}
    if include_currencies:
        result = {c: result[c]
                  for c in set(include_currencies) & set(result.keys())}
    return result


def serialize_posting(posting):
    leg = {
        'account': posting.account,
        'flag': posting.flag,
    }

    if posting.position:
        cost = interpolate.get_posting_weight(posting)
        leg.update({
            'position': posting.position.number,
            'position_currency': posting.position.lot.currency,
            'cost': cost.number,
            'cost_currency': cost.currency,
        })

    if posting.price:
        leg.update({
            'price': posting.price.number,
            'price_currency': posting.price.currency,
        })

    return leg
