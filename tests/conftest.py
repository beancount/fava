import os

import pytest

from beancount.loader import load_string
from fava.api import BeancountReportAPI
from fava.application import app, load_file


EXAMPLE_FILE = os.path.join(os.path.dirname(__file__), 'example.beancount')


@pytest.fixture
def setup_app():
    app.config['BEANCOUNT_FILES'] = [EXAMPLE_FILE]
    load_file()
    app.testing = True


@pytest.fixture
def load_doc(request):
    return load_string(request.function.__doc__, dedent=True)


@pytest.fixture
def example_api():
    api = BeancountReportAPI()
    api.load_file(EXAMPLE_FILE)
    return api
