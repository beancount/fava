from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from fava.util import simple_wsgi, slugify


def test_simple_wsgi():
    c = Client(simple_wsgi, BaseResponse)
    resp = c.get('/any_path')
    assert resp.status_code == 200
    assert resp.data == b''


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
