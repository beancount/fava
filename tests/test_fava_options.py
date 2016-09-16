from fava.api.fava_options import parse_options


def test_fava_options(load_doc):
    """
    2016-06-14 custom "fava-option" "interval" "week"
    2016-04-14 custom "fava-option" "charts" FALSE
    2016-04-14 custom "fava-option" "journal-show" "transaction open"
    2016-04-14 custom "fava-option" "editor-print-margin-column" 10"""

    entries, _, _ = load_doc
    options, _ = parse_options(entries)

    assert options['interval'] == 'week'
    assert not options['charts']
    assert options['journal-show'] == ['transaction', 'open']
    assert options['editor-print-margin-column'] == 10
