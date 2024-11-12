Fava has two example pages hosted on
[pythonanywhere.com](https://pythonanywhere.com):

- [fava.pythonanywhere.com](https://fava.pythonanywhere.com), which runs the
  latest released version.
- [favadev.pythonanywhere.com](https://favadev.pythonanywhere.com), which tracks
  the HEAD of the GitHub repo
  ([github.com/beancount/fava](https://github.com/beancount/fava))

There are four parts to both instances:

1. `/home/$USER/update.sh` installs Fava.
1. A cron job that executes this file daily.
1. A WSGI configuration file at `/var/www/fava_pythonanywhere_com_wsgi.py`
1. A web app that uses this file.
