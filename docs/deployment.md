# Deployment

There are a number of deployment options for persistently running rustfava on
the Web, depending on your Web server and WSGI deployment choices. Below you
can find some examples.

## Apache with reverse proxy

Apache configuration:

```apache
ProxyPass "/rustfava" "http://localhost:5000/rustfava"
```

The above will make rustfava accessible at the `/rustfava` URL and proxy requests
arriving there to a locally running rustfava. To make rustfava work properly in
that context, you should run it using the `--prefix` command line option, like
this:

```bash
rustfava --prefix /rustfava /path/to/your/main.beancount
```

To have rustfava run automatically at boot and manageable as a system service
you might want to define a systemd unit file for it, for example:

```ini
[Unit]
Description=Rustfava Web UI for Beancount

[Service]
Type=simple
ExecStart=/usr/bin/rustfava --host localhost --port 5000 --prefix /rustfava /path/to/your/main.beancount
User=your-user
```
