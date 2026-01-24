Rustfava can be hosted on [pythonanywhere.com](https://pythonanywhere.com).

There are four parts to a deployment:

1. `/home/$USER/update.sh` installs Rustfava.
1. A cron job that executes this file daily.
1. A WSGI configuration file at `/var/www/<app>_pythonanywhere_com_wsgi.py`
1. A web app that uses this file.
