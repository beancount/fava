from fava.application import app as application
from fava.application import load_file

application.config['BEANCOUNT_FILES'] = ['/home/fava/test1.bean', '/home/fava/test2.bean', '/home/fava/test3.bean']
load_file()
