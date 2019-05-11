# pylint: disable=missing-docstring

from fava.core.attributes import get_active_years


def test_get_active_years(load_doc):
    """
    2010-11-12 * "test"
        Assets:T   4.00 USD
        Expenses:T
    2011-11-12 * "test"
        Assets:T   4.00 USD
        Expenses:T
    2012-12-12 * "test"
        Assets:T   4.00 USD
        Expenses:T
    """

    entries, _, __ = load_doc
    assert get_active_years(entries, "12-31") == ["2012", "2011", "2010"]
    assert get_active_years(entries, "12-01") == ["FY2013", "FY2011", "FY2010"]
    assert get_active_years(entries, "11-01") == ["FY2013", "FY2012", "FY2011"]


def test_payee_accounts(example_ledger):
    attr = example_ledger.attributes
    assert attr.payee_accounts("NOTAPAYEE") == attr.accounts

    verizon = attr.payee_accounts("Verizon Wireless")
    assert verizon[:2] == ["Assets:US:BofA:Checking", "Expenses:Home:Phone"]
    assert len(verizon) == len(attr.accounts)


def test_payee_transaction(example_ledger):
    attr = example_ledger.attributes
    assert attr.payee_transaction("NOTAPAYEE") is None

    assert str(attr.payee_transaction("BayBook").date) == "2016-05-05"
