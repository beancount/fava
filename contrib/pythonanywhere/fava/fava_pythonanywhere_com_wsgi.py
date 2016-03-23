from fava.application import app as application
from fava.application import load_file, load_settings

application.config['BEANCOUNT_FILE'] = '/home/fava/test.bean'
application.config['USER_SETTINGS'] = None

load_settings()
load_file()
