from fava.template_filters import account_level, last_segment


def test_account_level():
    assert account_level('Assets') == 1
    assert account_level('Assets:Test') == 2
    assert account_level('Assets:Test:Test') == 3


def test_last_segment():
    assert last_segment('Assets') == 'Assets'
    assert last_segment('Assets:Test') == 'Test'
    assert last_segment('Assets:Test:Test1') == 'Test1'
