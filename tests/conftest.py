import os

import pytest

from beancount.loader import load_string
from fava.api import BeancountReportAPI
from fava.application import load_file
from fava.application import app as fava_app


EXAMPLE_FILE = os.path.join(os.path.dirname(__file__), 'example.beancount')


@pytest.fixture
def app():
    fava_app.config['BEANCOUNT_FILES'] = [EXAMPLE_FILE]
    load_file()
    fava_app.testing = True
    return fava_app


@pytest.fixture
def load_doc(request):
    return load_string(request.function.__doc__, dedent=True)


@pytest.fixture
def example_api():
    return BeancountReportAPI(EXAMPLE_FILE)
