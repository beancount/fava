from fava.util import uniquify, slugify


def test_slugify():
    assert slugify('Example Beancount File') == 'example-beancount-file'
    assert slugify('    Example Beancount File  ') == 'example-beancount-file'
    assert slugify('test') == 'test'
    assert slugify('烫烫烫') == '烫烫烫'
    assert slugify('nonun烫icode 烫烫') == 'nonun烫icode-烫烫'
    assert slugify('%✓') == ''
    assert slugify('söße') == 'söße'
    assert slugify('ASDF') == 'asdf'
    assert slugify('ASDF test test') == 'asdf-test-test'


def test_uniquify():
    assert uniquify([1, 1, 2, 3, 3]) == [1, 2, 3]
    assert uniquify([5, 3, 4, 3, 3, 5]) == [5, 3, 4]
