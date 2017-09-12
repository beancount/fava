from fava.application import app as application
from fava.application import load_file

application.config['BEANCOUNT_FILES'] = [
    '/home/fava/example.beancount',
    '/home/fava/budgets-example.beancount',
    '/home/fava/huge-example.beancount',
]
load_file()
