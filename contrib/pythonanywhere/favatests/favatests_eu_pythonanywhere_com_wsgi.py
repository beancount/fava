"""Fava WSGI application for `favatests.eu.pythonanywhere.com`."""

from __future__ import annotations

from fava.application import create_app

application = create_app(
    [
        "/home/favatests/example.beancount",
        "/home/favatests/budgets-example.beancount",
        "/home/favatests/huge-example.beancount",
    ],
)
