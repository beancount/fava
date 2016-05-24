from fava.application import app as application
from fava.application import load_file, load_settings

application.config['BEANCOUNT_FILES'] = [
        '/home/fava/test1.bean', '/home/fava/test2.bean']
application.config['USER_SETTINGS'] = None

load_settings()
load_file()

# app.user_config = configparser.ConfigParser()
# user_config_defaults_file = '/home/fava/default-settings.conf'
# app.user_config.readfp(open(user_config_defaults_file))
# app.user_config['fava']['file_defaults'] = user_config_defaults_file
# app.user_config['fava']['file_user'] = ''
