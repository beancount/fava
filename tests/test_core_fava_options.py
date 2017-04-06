from fava.core.fava_options import parse_options


def test_fava_options(load_doc):
    """
    2016-06-14 custom "fava-option" "interval" "week"
    2016-04-14 custom "fava-option" "show-closed-accounts" "true"
    2016-04-14 custom "fava-option" "journal-show" "transaction open"
    2016-04-14 custom "fava-option" "editor-print-margin-column" "10"
    2016-04-14 custom "fava-option" "invalid"
    """

    entries, _, _ = load_doc
    options, errors = parse_options(entries)

    assert len(errors) == 1

    assert options['interval'] == 'week'
    assert options['charts']
    assert options['show-closed-accounts']
    assert options['journal-show'] == ['transaction', 'open']
    assert options['editor-print-margin-column'] == 10
