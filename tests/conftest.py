# pylint: disable=missing-docstring

import os

import pytest

from beancount.loader import load_string
from fava.core import FavaLedger
from fava.application import _load_file, app as fava_app
from fava.core.budgets import parse_budgets


def create_app(bfile):
    key = "BEANCOUNT_FILES"
    if (key not in fava_app.config) or (fava_app.config[key] != [bfile]):
        fava_app.config[key] = [bfile]
        _load_file()


def data_file(filename):
    return os.path.join(os.path.dirname(__file__), "data", filename)


EXAMPLE_FILE = data_file("long-example.beancount")
EXTENSION_REPORT_EXAMPLE_FILE = data_file("extension-report-example.beancount")

API = FavaLedger(EXAMPLE_FILE)

fava_app.testing = True
TEST_CLIENT = fava_app.test_client()
create_app(EXAMPLE_FILE)


@pytest.fixture
def extension_report_app():
    create_app(EXTENSION_REPORT_EXAMPLE_FILE)
    return fava_app


@pytest.fixture
def app():
    create_app(EXAMPLE_FILE)
    return fava_app


@pytest.fixture
def test_client():
    return TEST_CLIENT


@pytest.fixture
def load_doc(request):
    return load_string(request.function.__doc__, dedent=True)


@pytest.fixture
def extension_report_ledger():
    return FavaLedger(EXTENSION_REPORT_EXAMPLE_FILE)


@pytest.fixture
def small_example_ledger():
    return FavaLedger(data_file("example.beancount"))


@pytest.fixture
def example_ledger():
    yield API
    API.filter(account=None, filter=None, time=None)


@pytest.fixture
def budgets_doc(request):
    entries, _, _ = load_string(request.function.__doc__, dedent=True)
    budgets, _ = parse_budgets(entries)
    return budgets
