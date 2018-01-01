Deployment
==========

There are a number of deployment options for persistently running Fava on the
Web, depending on your Web server and WSGI deployment choices. Below you can
find some examples.


Apache with reverse proxy
-------------------------

Apache configuration::

  ProxyPass "/fava" "http://localhost:5000/fava"

The above will make Fava accessible at the ``/fava`` URL and proxy requests
arriving there to a locally running Fava. To make Fava work properly in that
context, you should run it using the ``--prefix`` command line option, like
this::

  fava --prefix /fava /path/to/your/main.beancount

To have Fava run automatically at boot and manageable as a system service you
might want to define a systemd unit file for it, for example::

  [Unit]
  Description=Fava Web UI for Beancount
  
  [Service]
  Type=simple
  ExecStart=/usr/bin/fava --host localhost --port 5000 --prefix /fava /path/to/your/main.beancount
  User=your-user
