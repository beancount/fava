---
title: Running fava
---

# Running fava

The `fava`-webserver can be started with the `fava`-command:

```bash
$ fava
usage: fava [-h] [-p PORT] [-H HOST] [-s SETTINGS] [-d] [--profile]
            [--pstats-output PSTATS_OUTPUT]
            [--profile-restriction PROFILE_RESTRICTION]
            filename
```

It takes the following arguments:

`-p PORT` or `--port PORT`:
    Port on which the webserver should listen. Default is `5000`.

`-H HOST` or `--host HOST`:
    Host for the webserver. Default is `localhost`.

`-s SETTINGS` or `--settings SETTINGS`:
    Path to the settings file for `fava`.

`-d` or `--debug`:
    Turns on debugging. This uses the built-in Flask webserver, and disables
    live-reloading of the Beancount-files, documents and settings- file.

`--profile`:
    Turn on profiling.  Implies `--debug`.  Profiling information for each
    request will be printed to the log, unless `--pstats-output` is also
    specified.

`--pstats-output PSTATS_OUTPUT`:
    Output directory for profiling pstats data. Implies --profile. If this is
    specified, profiling information will be saved to the specified directly and
    will not be printed to the log.

`--profile-restriction PROFILE_RESTRICTION`:
    Maximum number of functions to show in profile printed to the log. Default
    is `30`.

`filename`:
    The path to the Beancount input file. This is required.


## Examples

Run in normal mode with minimal configuration:

```bash
fava /Volumes/Ledger/ledger-2015.beancount
```

Specify a settings file and enable Debug-mode:

```bash
fava --settings /Volumes/Ledger/fava-settings.conf --debug /Volumes/Ledger/ledger-2016.beancount
```

Specify a different port and enable Debug-mode:

```bash
fava --port 8080 --debug /Volumes/Ledger/ledger-2016.beancount
```
