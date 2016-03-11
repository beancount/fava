import collections
import datetime

from beancount.scripts.example import write_example_file
from flask import url_for
import pytest

from fava.application import app


@pytest.fixture
def setup_app(tmpdir):
    filename = tmpdir.join('beancount.example')
    with filename.open('w') as fd:
        today = datetime.date.today()
        write_example_file(datetime.date(1980, 5, 12),
                           datetime.date(today.year - 3, 1, 1),
                           today, True, fd)
    app.beancount_filename = str(filename)
    app.api.load_file(app.beancount_filename)
    app.testing = True


class URLQueue:
    def __init__(self):
        self.seen_values = collections.defaultdict(set)
        self.stack = ['/income_statement/']
        self.seen = set(self.stack)

    def append(self, endpoint, values, current):
        if endpoint in ['source', 'document'] or\
                'REPLACEME' in values.values():
            return
        real_endpoint = endpoint
        if 'report_name' in values:
            endpoint = values['report_name']
        value_keys = frozenset([key for key, value in values.items() if value])
        if value_keys not in self.seen_values[endpoint]:
            self.seen_values[endpoint].add(value_keys)
            with app.test_request_context(current):
                app.preprocess_request()
                url = url_for(real_endpoint, loop=True, **values)
                if url not in self.seen:
                    self.seen.add(url)
                    self.stack.append(url)

    def pop(self):
        return self.stack.pop()


def test_scrape(setup_app):
    urls = URLQueue()
    current = urls.stack[0]

    @app.url_defaults
    def collect_urls(endpoint, values):
        if 'loop' in values:
            values.pop('loop')
            return
        urls.append(endpoint, values, current)

    test_app = app.test_client()

    while urls.stack:
        print(current)
        rv = test_app.get(current)
        assert rv.status_code == 200
        current = urls.pop()
