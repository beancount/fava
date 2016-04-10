from datetime import datetime
from beancount.core.data import Custom

from . import Budgets, Dateline, AccountEntry


def init_budgets_from_entries(entries):
    accounts = {}
    for entry in entries:
        if isinstance(entry, Custom):
            if entry.type == 'budget':
                account_name = entry.values[0].value

                if not account_name in accounts:
                    accounts[account_name] = AccountEntry(name=account_name)

                accounts[account_name].datelines.append(
                    Dateline(date_monday=entry.date,
                             period=entry.values[1].value,
                             value=entry.values[2].value.number,
                             currency=entry.values[2].value.currency)
                )

    for name, account in accounts.items():
        accounts[name].datelines = sorted(accounts[name].datelines, key=lambda dateline: dateline.date_monday)

    return Budgets(accounts=accounts.values())
