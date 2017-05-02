from fava.core.misc import extract_tags_links


def test_extract_tags_links():
    assert extract_tags_links('notag') == ('notag', frozenset(), frozenset())
    assert extract_tags_links('Some text #tag') == (
        'Some text', frozenset(['tag']), frozenset())
    assert extract_tags_links('Some text ^link') == ('Some text', frozenset(),
                                                     frozenset(['link']))
    assert extract_tags_links('Some text #tag #tag2 ^link') == (
        'Some text', frozenset(['tag', 'tag2']), frozenset(['link']))
    assert extract_tags_links('Some text#tag#tag2 ^link') == (
        'Some text#tag#tag2', frozenset(), frozenset(['link']))
    assert extract_tags_links('Some text#tag#tag2^link') == (
        'Some text#tag#tag2^link', frozenset(), frozenset())
    assert extract_tags_links('#tag') == ('', frozenset(['tag']), frozenset())
