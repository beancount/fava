import os

import pytest

from beancount.loader import load_string
from fava.core import FavaLedger
from fava.application import load_file
from fava.application import app as fava_app


EXAMPLE_FILE = os.path.join(os.path.dirname(__file__), 'example.beancount')
API = FavaLedger(EXAMPLE_FILE)


fava_app.testing = True
TEST_CLIENT = fava_app.test_client()
fava_app.config['BEANCOUNT_FILES'] = [EXAMPLE_FILE]
load_file()


@pytest.fixture
def app():
    return fava_app


@pytest.fixture
def test_client():
    return TEST_CLIENT


@pytest.fixture
def load_doc(request):
    return load_string(request.function.__doc__, dedent=True)


@pytest.fixture
def example_ledger():
    yield API
    API.filter(**{name: None for name in API._filters.keys()})
