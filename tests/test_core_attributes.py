# pylint: disable=missing-docstring


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
