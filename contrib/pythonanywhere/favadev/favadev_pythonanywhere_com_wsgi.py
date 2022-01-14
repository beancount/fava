"""fava wsgi application"""
from __future__ import annotations

from fava.application import app as application

application.config["BEANCOUNT_FILES"] = [
    "/home/favadev/example.beancount",
    "/home/favadev/budgets-example.beancount",
    "/home/favadev/huge-example.beancount",
]
