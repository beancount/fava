"""fava wsgi application"""

from __future__ import annotations

from fava.application import create_app

application = create_app(
    [
        "/home/fava/example.beancount",
        "/home/fava/budgets-example.beancount",
        "/home/fava/huge-example.beancount",
    ],
)
