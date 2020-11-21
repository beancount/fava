"""fava wsgi application"""
from fava.application import app as application

application.config["BEANCOUNT_FILES"] = [
    "/home/favadev/example.beancount",
    "/home/favadev/budgets-example.beancount",
    "/home/favadev/huge-example.beancount",
]
