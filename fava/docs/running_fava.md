---
title: Running fava
---

# Running fava

`fava` can be started with the `fava`-command. `fava --help` will show all the
available command-line options.

```
$ fava --help
Usage: fava [OPTIONS] FILENAME

  Start fava for FILENAME on http://host:port.

Options:
  -p, --port INTEGER             The port to listen on. (default: 5000)
  -H, --host TEXT                The host to listen on. (default: localhost)
  -s, --settings PATH            Settings file for fava.
  -d, --debug                    Turn on debugging. Disables live-reloading.
  --profile                      Turn on profiling. Implies --debug.
  --profile-dir PATH             Output directory for profiling data.
  --profile-restriction INTEGER  Number of functions to show in profile.
  --help                         Show this message and exit.
```

## Examples

Run with default configuration:

```bash
fava ledger.beancount
```

Specify a settings file and enable debug-mode:

```bash
fava --debug --settings /Volumes/Ledger/fava-settings.conf /Volumes/Ledger/ledger.beancount
```

Specify a different port and enable debug-mode:

```bash
fava --port 8080 --debug /Volumes/Ledger/ledger.beancount
```
