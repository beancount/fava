"""fava wsgi application"""

from __future__ import annotations

from fava.application import create_app

application = create_app(
    [
        "/home/favadev/example.beancount",
        "/home/favadev/budgets-example.beancount",
        "/home/favadev/huge-example.beancount",
    ],
)
