# Deploying with Docker

## Basic

The Dockerfile in this directory is enough to get started running fava in a
container.  This guide is meant as a compliment to the great documentation
found at https://docs.docker.com/.

### Building

The included Dockerfile builds beancount and fava at HEAD and describes how top
run fava within the container.

To build the container run this command:

    docker build -t fava .

This will build everything and name the image `fava`.  Because docker depends
heavily on caching to improve efficiency, to incorporate a new version of
beancount or fava you must use the `--no-cache` flag when rebuilding the image.

### Deploying

To run the fava container, use this command:

    docker run --detach --publish 5000:5000 \
      --volume $(pwd)/example.beancount:/example.beancount \
      --env BEANCOUNT_INPUT_FILE=/example.beancount fava

Let's look at each argument independently:

1. `--detach` tells docker to start the image and exit.  The default behaviour
   is to run until the command exits, but fava is a daemon so it never does.
1. `--publish 5000:5000` tells docker to expose the container's port 5000 as
   the local machine's port 5000.  This allows us to access fava with the url
   http://localhost:5000/.
1. `--volume $(pwd)/example.beancount:/example.beancount` tells docker to share
   the example.beancount file in the current directory to the container as the
   file `/example.beancount`.
1. `--env BEANCOUNT_INPUT_FILE=/example.beancount` tells the fava command where
   to look for the beancount file.

Going to http://localhost:5000/ will display your fava instance.

## Advanced

### Commit hashes

### Oauth proxy

### Letsencrypt
