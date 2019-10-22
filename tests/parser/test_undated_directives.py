# pylint: disable=missing-docstring


def test_pushtag_open(snapshot_parse_doc):
    """
    pushtag #testtag
    """
    assert snapshot_parse_doc[1]


def test_pushtag_closed(snapshot_parse_doc):
    """
    pushtag #testtag
    poptag #testtag
    """
    assert not snapshot_parse_doc[1]


def test_pushtag_entries(snapshot_parse_doc):
    """
    pushtag #testtag

    2012-12-12 * "test"
      Assets:Cash    4.00 USD
      Assets:Cash2   -4.00 USD
    poptag #testtag
    """
    assert "testtag" in snapshot_parse_doc[0][0].tags
    assert not snapshot_parse_doc[1]


def test_poptag(snapshot_parse_doc):
    """
    poptag #testtag
    """
    assert snapshot_parse_doc[1]


def test_pushmeta_open(snapshot_parse_doc):
    """
    pushmeta test: "value"
    """
    assert snapshot_parse_doc[1]


def test_pushmeta_complete(snapshot_parse_doc):
    """
    pushmeta test: "value"

    2012-12-12 * "test"
      Assets:Cash    4.00 USD
      Assets:Cash2   -4.00 USD

    2012-12-12 * "test"
      test: "value2"
      Assets:Cash    4.00 USD
      Assets:Cash2   -4.00 USD

    popmeta test:
    """
    entries, errors, _ = snapshot_parse_doc
    assert entries[0].meta["test"] == "value"
    assert entries[1].meta["test"] == "value2"
    assert not errors


def test_plugin(parse_doc):
    """
    plugin "beancount.plugin.unrealized"
    """
    _, errors, options_map = parse_doc
    assert not errors
    assert options_map["plugin"] == [("beancount.plugin.unrealized", None)]


def test_plugin_with_config(parse_doc):
    """
    plugin "beancount.plugin.unrealized" "Test"
    """
    _, errors, options_map = parse_doc
    assert not errors
    assert options_map["plugin"] == [("beancount.plugin.unrealized", "Test")]


def test_plugin_as_option(parse_doc):
    """
    option "plugin" "beancount.plugin.unrealized"
    """
    _, errors, __ = parse_doc
    assert errors
