from fava.util import slugify


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
