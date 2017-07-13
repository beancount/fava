# fava @ pythonanywhere

`fava` has two Example pages hosted on
[pythonanywhere.com](https://pythonanywhere.com):

- [fava.pythonanywhere.com](https://fava.pythonanywhere.com), which tracks the
  current version available on PyPI (`pip3 install fava`)
- [favadev.pythonanywhere.com](https://favadev.pythonanywhere.com), which
  tracks the HEAD of the Github repo
  ([github.com/beancount/fava](https://github.com/beancount/fava))

There are four parts to both instances:
1. '/home/$USER/update.sh' does install `fava` and all dependencies and
   generate an example-file
2. A cron job that executes this file daily
3. A WSGI configuration file at `/var/www/fava_pythonanywhere_com_wsgi.py`
4. A web app in [pythonanywhere.com](https://pythonanywhere.com) that uses this
   file

