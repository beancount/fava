from beancount.core.inventory import Inventory


def inventory_at_dates(transactions, dates, posting_predicate):
    """Generator that yields the aggregate inventory at the specified dates.

    Args:
        transactions: list of transactions, sorted by date.
        dates: iterator of dates
        posting_predicate: only postings for which this evaluates to True will
            be considered.
    """

    iterator = iter(transactions)
    txn = next(iterator, None)

    inventory = Inventory()

    for date in dates:
        while txn and txn.date < date:
            for posting in filter(posting_predicate, txn.postings):
                inventory.add_position(posting)
            txn = next(iterator, None)
        yield inventory
