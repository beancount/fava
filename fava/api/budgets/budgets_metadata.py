import os
from datetime import datetime

from modgrammar import *
from beancount.core import realization
from beancount.core.amount import Amount, decimal
from beancount.core.data import Open

from . import Budgets, Dateline, AccountEntry
from .budgets_separate_file import DateExpr, ValueExpr, CurrencyExpr

grammar_whitespace_mode = 'optional'

def init_budgets_from_metadata(root_account):
    parser = MetadataDatelineExpr.parser()

    accounts = []
    for ra in realization.iter_children(root_account):
        if ra.account == '':
            continue
        account = AccountEntry(name=ra.account)

        for posting in ra.txn_postings:
            if isinstance(posting, Open):
                for key in posting.meta:
                    if key.startswith('budget-'):
                        result = parser.parse_text("{}  {}".format(key[7:], posting.meta[key]), eof=True)
                        account.datelines.append(result.value())

        account.datelines = sorted(account.datelines, key=lambda dateline: dateline.date_monday)
        accounts.append(account)

    return Budgets(accounts=accounts)


class MetadataDatelineExpr(Grammar):
    grammar = (DateExpr, ValueExpr, CurrencyExpr)

    def value(self):
        return Dateline(date_monday=self[0].value()[1], period=self[0].value()[0], value=self[1].value(), currency=self[2].value())
