import collections

from flask import url_for

from fava.application import app


class URLQueue:
    def __init__(self):
        self.seen_values = collections.defaultdict(set)
        self.stack = ['/']
        self.seen = set(self.stack)

    def append(self, endpoint, values, current):
        if endpoint in ['source', 'document', 'add_document'] or \
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
        assert rv.status_code in [200, 302]
        current = urls.pop()
