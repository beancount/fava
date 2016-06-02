import collections

from flask import url_for


class URLQueue:
    def __init__(self, app):
        self.seen_values = collections.defaultdict(set)
        self.stack = ['/']
        self.all = []
        self.app = app

    def append(self, endpoint, values, current):
        if (endpoint in ['source', 'document', 'add_document'] or
                'REPLACEME' in values.values()):
            return
        real_endpoint = endpoint
        if 'report_name' in values:
            endpoint = values['report_name']
        filters = ['account', 'interval', 'payee', 'tag', 'time']
        value_keys = frozenset([key for key, value in values.items()
                                if value and key not in filters])

        if value_keys not in self.seen_values[endpoint]:
            self.seen_values[endpoint].add(value_keys)
            with self.app.test_request_context(current):
                self.app.preprocess_request()
                url = url_for(real_endpoint, loop=True, **values)
                self.all.append((real_endpoint, values))
                self.stack.append(url)

    def pop(self):
        return self.stack.pop()


filter_combinations = [
    {'account': 'Assets'},
    {'time': '2015'},
    {'payee': 'BayBook'},
    {'tag': 'tag1, tag2'},
    {'time': '2015', 'payee': 'BayBook'},
]


def test_scrape(app):
    urls = URLQueue(app)
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
        assert rv.status_code in [200, 302]
        current = urls.pop()

    for url_values in urls.all:
        for filters in filter_combinations:
            values = url_values[1].copy()
            values.update(filters)

            with app.test_request_context(current):
                app.preprocess_request()
                url = url_for(url_values[0], **values)

            print(url)
            rv = test_app.get(url)
            assert rv.status_code in [200, 302]
