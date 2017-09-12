from fava.application import app as application
from fava.application import load_file

application.config['BEANCOUNT_FILES'] = [
    '/home/favadev/example.beancount',
    '/home/favadev/budgets-example.beancount',
    '/home/favadev/huge-example.beancount',
]
load_file()
