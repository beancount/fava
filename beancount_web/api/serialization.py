from beancount.core.number import ZERO


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
