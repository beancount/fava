import os
from datetime import datetime

from modgrammar import *
from beancount.core.amount import Amount, decimal
from . import Budgets, Dateline, AccountEntry


grammar_whitespace_mode = 'optional'

def init_budgets_from_file():
    budget_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test-budget.budget')
    parser = AllExpr.parser()
    with open(budget_file, 'r') as f:
        result = parser.parse_text(f.read(), eof=True)
        # remainder = parser.remainder()
        # print()
        # print("Unparsed Text: {}".format(remainder))
        # print()
    accounts = result.value()

    return Budgets(accounts=accounts)

class DateExpr(Grammar):
    """
    A date can represented in these ways:
        2016-01-01 => Budget for a day
        2016-W01   => Budget for a week
        2016-01    => Budget for a month
        2016-Q1    => Budget for a quarter
        2016       => Budget for a year

    Returns a tuple of (date, 'D|W|M|Q|Y') where 'D|W|M|Q|Y' is the period
    """
    grammar = (
                WORD('0-9'),
                OPTIONAL(
                    OR(
                        GRAMMAR(
                            WORD('-'), WORD('0-9'), WORD('-'), WORD('0-9')
                        ) | GRAMMAR(
                            WORD('-'), L('W'), WORD('0-9')
                        ) | GRAMMAR(
                            WORD('-'), L('Q'), WORD('0-9')
                        ) | GRAMMAR(
                            WORD('-'), WORD('0-9')
                        )
                    )
                )
            )

    def value(self):
        string = self.string.strip()
        if string.count('-') == 2:     # 2016-01-01
            return ('D', datetime.strptime(string, "%Y-%m-%d").date())
        elif 'W' in string:   # 2016-W01
            return ('W', datetime.strptime(string + '-1', "%Y-W%U-%w").date())
        elif 'Q' in string:   # 2016-Q1
            if 'Q1' in string:
                return ('Q', datetime.strptime(string + '-01-01', "%Y-Q1-%m-%d").date())
            elif 'Q2' in string:
                return ('Q', datetime.strptime(string + '-04-01', "%Y-Q2-%m-%d").date())
            elif 'Q3' in string:
                return ('Q', datetime.strptime(string + '-07-01', "%Y-Q3-%m-%d").date())
            elif 'Q4' in string:
                return ('Q', datetime.strptime(string + '-10-01', "%Y-Q4-%m-%d").date())
            else:
                raise Exception("Invalid date-string: {}".format(string))
        elif '-' in string:   # 2016-01
            return ('M', datetime.strptime(string + '-01', "%Y-%m-%d").date())
        else:                      # 2016
            return ('Y', datetime.strptime(string + '-01-01', "%Y-%m-%d").date())

class ValueExpr(Grammar):
    grammar = (OPTIONAL(WORD('-')), WORD('0-9'), WORD('.'), WORD('0-9'))

    def value(self):
        return decimal.Decimal(float(self.string))

class CurrencyExpr(Grammar):
    grammar = (WORD('A-Z'))

    def value(self):
        return self.string

class AccountNameExpr(Grammar):
    grammar = (WORD("A-Za-z1-9"), ZERO_OR_MORE(WORD(':'), WORD("A-Za-z1-9")))

    def value(self):
        return AccountEntry(name=self.string.strip())

class DatelineExpr(Grammar):
    grammar = (ONE_OR_MORE((DateExpr, ValueExpr, CurrencyExpr)))

    def value(self):
        value = []
        for e in self[0]:
            value.append(Dateline(date_monday=e[0].value()[1], period=e[0].value()[0], value=e[1].value(), currency=e[2].value()))
        return value

class EntryExpr(Grammar):
    grammar = (AccountNameExpr, ONE_OR_MORE(DatelineExpr))

    def value(self):
        entry = self[0].value()

        for e in self[1]:
            entry.datelines = sorted(e.value(), key=lambda dateline: dateline.date_monday)

        return entry

class AllExpr(Grammar):
    grammar = (ONE_OR_MORE(EntryExpr))

    def value(self):
        return [e.value() for e in self[0]]


# def run():
#     text = """
#     Expenses:Foo
#         2016-W01      70.00 USD
#         2016-W02     350.00 USD

#     Expenses:Foo2
#         2016-W31     250.00 USD
#         2016-W30     111.00 EUR
#         2016-W20    9999.15 USD
#     """

#     parser = AllExpr.parser()
#     result = parser.parse_text(text, eof=True)
#     remainder = parser.remainder()
#     print("Text: \n{}".format(text))
#     print("Parsed Text: {}".format(result))
#     print("Unparsed Text: {}".format(remainder))
#     print("\n\n\nValue: {}".format(result.value()))
#     print("\n\n\nResult: {}".format(len(result.elements[0])))
#     return Budgets(accounts=result.value())

# if __name__ == '__main__':
#     # text = sys.argv[1]
#     d = run()
#     print("##################")
#     date_from = datetime(2016, 1, 4)
#     date_to = datetime(2016, 1, 12)
#     print(d.budget('Expenses:Foo', 'USD', date_from, date_to))
