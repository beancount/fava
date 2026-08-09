# Deployment

There are several ways to deploy rustfava depending on your needs.

## Engine

rustfava runs the rustledger engine as a WebAssembly component in-process via
the `wasmtime` Python package, which is installed automatically as a dependency.
Nothing extra to set up.

> The legacy JSON-RPC engine (which shelled out to the `wasmtime` CLI) was
> removed in rustfava 1.31 after its embedding surface was retired upstream;
> `RUSTFAVA_RUSTLEDGER_BACKEND` is no longer used.

## Desktop App

For personal use, the
[desktop app](https://github.com/rustledger/rustfava/releases) is the simplest
option. It runs entirely locally with no server setup required.

## Docker

For server deployments, Docker is recommended:

```bash
docker run -p 5000:5000 -v /path/to/ledger:/data ghcr.io/rustledger/rustfava /data/main.beancount
```

For advanced Docker configurations (authentication, HTTPS, docker-compose), see
the
[Docker deployment guide](https://github.com/rustledger/rustfava/blob/main/contrib/docker/README.md).

## Systemd Service

To run rustfava as a system service on Linux:

```ini
# /etc/systemd/system/rustfava.service
[Unit]
Description=rustfava Web UI for Beancount
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/rustfava --host 127.0.0.1 --port 5000 /path/to/main.beancount
User=your-user
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl enable rustfava
sudo systemctl start rustfava
```

## Reverse Proxy

### Apache

```apache
ProxyPass "/rustfava" "http://localhost:5000/rustfava"
ProxyPassReverse "/rustfava" "http://localhost:5000/rustfava"
```

Run rustfava with the `--prefix` option:

```bash
rustfava --prefix /rustfava /path/to/main.beancount
```

### Nginx

```nginx
location /rustfava/ {
    proxy_pass http://127.0.0.1:5000/rustfava/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### Caddy

```
your-domain.com {
    reverse_proxy localhost:5000
}
```

Caddy automatically handles HTTPS with Let's Encrypt.

## Security Considerations

When exposing rustfava to the internet:

1. **Use HTTPS** - Never expose plain HTTP to the public internet
1. **Add authentication** - Use a reverse proxy with OAuth2 or basic auth
1. **Restrict access** - Use firewall rules to limit access to trusted IPs
1. **Keep updated** - Regularly update rustfava for security patches

See [SECURITY.md](https://github.com/rustledger/rustfava/blob/main/SECURITY.md)
for more security best practices.
