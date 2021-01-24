# Deploying with Docker

## Basic

The Dockerfile in this directory is enough to get started running Fava in a
container. This guide is meant as a compliment to the great documentation found
at https://docs.docker.com/.

### Building

To build the image using the provided Dockerfile run this command:

```
docker build -t fava .
```

This will build everything and name the image `fava`. Because docker depends
heavily on caching to improve efficiency, to incorporate a new version of
Beancount or Fava you must use the `--no-cache` flag when rebuilding the image.

### Deploying

To run the Fava container, use this command:

```
docker run --detach --name="beancount" --publish 5000:5000 \
  --volume $(pwd)/example.beancount:/input.beancount \
  --env BEANCOUNT_FILE=/input.beancount fava
```

Let's look at each argument independently:

1. `--detach` tells Docker to start the image and run it in the background as a
   daemon.
1. `--name` specifies a name to give the Docker instance instead of generating a
   random id. This will be used later.
1. `--publish` tells Docker to expose the container's port 5000 as the local
   machine's port 5000. This allows us to access Fava with the url
   http://localhost:5000/.
1. `--volume` tells Docker to share the example.beancount file in the current
   directory to the container as the file `/input.beancount`.
1. `--env` tells Fava where to find the Beancount file.

Going to http://localhost:5000/ will display your Fava instance.

## Advanced

Hosting a local Docker instance is nice and all, but what we really want is a
globally available, authenticated, secure deployment of Fava. To do that we need
two other parts: oauth proxy and letsencrypt.

### Oauth proxy

Oauth is an authentication standard that makes it easy to authenticate using a
third party account. Using oauth means we can limit access to our site without
requiring mobile users to enter complicated passwords.

We will be using bitly's [oauth2_proxy](https://github.com/bitly/oauth2_proxy)
to manage access to our site.

I recommend using the
[skippy/oauth2_proxy](https://hub.docker.com/r/skippy/oauth2_proxy/) Docker
image. It is an alpinelinux-based Docker image with bitly's oauth2_proxy
packaged. It uses an older version of oauth2_proxy, which is fine enough for
Fava, but it is left as an exercise to the reader to build an updated version.

It can be configured entirely using command line flags, but it is generally
easier to configure using a file.

Follow the Google Auth Provider instructions in the
[oauth2_proxy](https://github.com/bitly/oauth2_proxy) README to generate a
Client ID and Client Secret and fill out the `oauth2_proxy.cfg`.

The file will look something like this:

```
## OAuth2 Proxy Config File
## https://github.com/bitly/oauth2_proxy

## <addr>:<port> to listen on for HTTP/HTTPS clients
# http_address = "127.0.0.1:4180"
# https_address = ":443"

## TLS Settings
# tls_cert_file = ""
# tls_key_file = ""

## the OAuth Redirect URL.
# defaults to the "https://" + requested host header + "/oauth2/callback"
redirect_url = "https://bean.xennet.org/oauth2/callback"

## the http url(s) of the upstream endpoint. If multiple, routing is based on path
upstreams = [
    "http://beancount:5000/"
]

## Log requests to stdout
request_logging = true

## pass HTTP Basic Auth, X-Forwarded-User and X-Forwarded-Email information to upstream
# pass_basic_auth = true
## pass the request Host Header to upstream
## when disabled the upstream Host is used as the Host Header
# pass_host_header = true

## Email Domains to allow authentication for (this authorizes any email on this domain)
## for more granular authorization use `authenticated_emails_file`
## To authorize any email addresses use "*"
# email_domains = [
#     "yourcompany.com"
# ]

## The OAuth Client ID, Secret
client_id = "<Client ID goes here>"
client_secret = "<Client Secret goes here>"

## Pass OAuth Access token to upstream via "X-Forwarded-Access-Token"
# pass_access_token = false

## Authenticated Email Addresses File (one email per line)
authenticated_emails_file = "/etc/authenticated-emails"

## Htpasswd File (optional)
## Additionally authenticate against a htpasswd file. Entries must be created with "htpasswd -s" for SHA encryption
## enabling exposes a username/login signin form
# htpasswd_file = ""

## Templates
## optional directory with custom sign_in.html and error.html
# custom_templates_dir = ""

## Cookie Settings
## Name     - the cookie name
## Secret   - the seed string for secure cookies; should be 16, 24, or 32 bytes
##            for use with an AES cipher when cookie_refresh or pass_access_token
##            is set
## Domain   - (optional) cookie domain to force cookies to (ie: .yourcompany.com)
## Expire   - (duration) expire timeframe for cookie
## Refresh  - (duration) refresh the cookie when duration has elapsed after cookie was initially set.
##            Should be less than cookie_expire; set to 0 to disable.
##            On refresh, OAuth token is re-validated.
##            (ie: 1h means tokens are refreshed on request 1hr+ after it was set)
## Secure   - secure cookies are only sent by the browser of a HTTPS connection (recommended)
## HttpOnly - httponly cookies are not readable by javascript (recommended)
# cookie_name = "_oauth2_proxy"
cookie_secret = "<Long unguessable string>"
# cookie_domain = ""
# cookie_expire = "168h"
# cookie_refresh = ""
cookie_secure = true
cookie_httponly = true
```

Create an `authenticated-emails` file in the same directory filled with all the
gmail accounts you want to have access to your Fava web interface.

To run your proxy docker image use the following command:

    docker run --detach --link beancount --publish 4180:4180 \
      --name beancount-oauth \
      --volume $(pwd)/oauth2_proxy.cfg:/etc/oauth2_proxy.cfg \
      --volume $(pwd)/authenticated-emails:/etc/authenticated-emails \
      --env "VIRTUAL_HOST=<your domain>" \
      --env "LETSENCRYPT_HOST=<your domain>" \
      --env "LETSENCRYPT_EMAIL=<your email>" \
      skippy/oauth2_proxy -config=/etc/oauth2_proxy.cfg \
      -http-address="0.0.0.0:4180" -provider=google

Let's document the new arguments:

1. `--link` tells docker to link one container to another, so they can access
   each other's exposed ports, and properly set up hostname mappings. This is
   why `upstreams` in the oauth2_proxy config is `http://beancount:5000`.
1. `--volume` maps host paths into docker instances. This is one way of getting
   data into a docker instance.
1. `--env` sets arbitrary environment values in docker instances. We will use
   these values in later sections to hook up automatically generate and refresh
   Let's Encrypt SSL certificates. Without a Let's Encrypt certificate, your
   oauth2_proxy cookie will be visible to anyone who can see your network
   traffic. You don't want this.
1. Everything after the `skippy/oauth2_proxy` are arguments to oauth2_proxy.

This will start an oauth2 proxy using your config to do authentication using
Google's OAuth service. It's important that you don't try to access your service
immediately on port 4180, otherwise you may expose your authentication cookie to
the internet.

### Letsencrypt

[Let's Encrypt](https://letsencrypt.org/) is a very popular project aimed at
making SSL certificates available to everyone for free. This will be a great way
to secure our Fava instance so that we can share secret cookies without fear of
anyone impersonating us.

We don't just want to set up a static Let's Encrypt config. We want to use the
magic of docker instances to generate our configs and keep them up to date at
all times. To accomplish this we will use three separate docker instances
working in conjunction. These instructions will mostly be a specific
implementation of the instructions found in
[JrCs/docker-letsencrypt-nginx-proxy-companion](https://github.com/JrCs/docker-letsencrypt-nginx-proxy-companion#separate-containers).

We will run three separate containers:

```
docker run --detach --publish 80:80 --publish 443:443 \
    --name nginx \
    --volume /etc/nginx/conf.d \
    --volume /etc/nginx/vhost.d \
    --volume /usr/share/nginx/html \
    --volume $(pwd)/certs:/etc/nginx/certs:ro \
    --volume $(pwd)/htpasswd:/etc/nginx/htpasswd:ro \
    --label com.github.jrcs.letsencrypt_nginx_proxy_companion.nginx_proxy=true \
    nginx
```

```
docker run --detach \
    --name nginx-gen \
    --volumes-from nginx \
    --volume /var/run/docker.sock:/tmp/docker.sock:ro \
    jwilder/docker-gen \
    -notify-sighup nginx -watch -only-exposed -wait 5s:30s \
    /etc/docker-gen/templates/nginx.tmpl /etc/nginx/conf.d/default.conf
```

```
docker run --detach \
    --name nginx-letsencrypt \
    --env "NGINX_DOCKER_GEN_CONTAINER=nginx-gen" \
    --volumes-from nginx \
    --volume $(dirname $(realpath $0))/certs:/etc/nginx/certs:rw \
    --volume /var/run/docker.sock:/var/run/docker.sock:ro \
    jrcs/letsencrypt-nginx-proxy-companion
```

The main new argument in these three images is `--volumes-from`. This flag
allows containers to share paths and make their data visible to each other.

Another interesting thing is that the non-nginx docker images need access to the
docker socket so that they can read the environment variables of other instances
and also send sighups to the nginx process when configs change.

Now all you have to do is expose port 80 and 443 from your host machine to the
internet and point the domain you specified in `VIRTUAL_HOST` and
`LETSENCRYPT_HOST` to your IP. Once all these parts are set up point your
browser to your virtual host domain and enjoy a fully authenticated, secure,
publicly addressable Fava instance.
