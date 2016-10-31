from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from fava.util import simple_wsgi, slugify, next_statement_key


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

def test_next_statement_key():
    assert next_statement_key([]) == 'statement'
    assert next_statement_key(['foo']) == 'statement'
    assert next_statement_key(['foo', 'statement']) == 'statement-2'
    assert next_statement_key(['statement', 'statement-2']) == 'statement-3'
