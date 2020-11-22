"""fava wsgi application"""
from fava.application import app as application

application.config["BEANCOUNT_FILES"] = [
    "/home/fava/example.beancount",
    "/home/fava/budgets-example.beancount",
    "/home/fava/huge-example.beancount",
]
