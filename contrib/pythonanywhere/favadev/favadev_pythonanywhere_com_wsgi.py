from fava.application import app as application
from fava.application import load_file

application.config['BEANCOUNT_FILES'] = ['/home/favadev/test1.bean', '/home/favadev/test2.bean', '/home/favadev/test3.bean']
load_file()
