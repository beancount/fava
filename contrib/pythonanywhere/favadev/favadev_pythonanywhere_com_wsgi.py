import configparser
from fava.api import BeancountReportAPI
from fava.application import app as application

application.beancount_file = '/home/favadev/test.bean'
application.filter_year = None
application.filter_tag = None
application.api = BeancountReportAPI(application.beancount_file)

application.user_config = configparser.ConfigParser()
user_config_defaults_file = '/home/favadev/default-settings.conf'
application.user_config.readfp(open(user_config_defaults_file))
application.user_config['fava']['file_defaults'] = user_config_defaults_file
application.user_config['fava']['file_user'] = ''
