Fava can be started with the `fava` command. `fava --help` will show all the
available command-line options.

```
$ fava --help
Usage: fava [OPTIONS] [FILENAMES]...

  Start fava for FILENAMES on http://host:port.

Options:
  -p, --port INTEGER             The port to listen on. (default: 5000)
  -H, --host TEXT                The host to listen on. (default: localhost)
  -d, --debug                    Turn on debugging. Disables live-reloading.
  --profile                      Turn on profiling. Implies --debug.
  --profile-dir PATH             Output directory for profiling data.
  --profile-restriction INTEGER  Number of functions to show in profile.
  --help                         Show this message and exit.
```

If the `BEANCOUNT_FILE` environment variable is set, Fava will use the file
specified there as the Beancount file.

## Examples

Run with default configuration:

```
fava ledger.beancount
```

Enable debug mode:

```
fava --debug /Volumes/Ledger/ledger.beancount
```

Specify a different port and enable debug-mode:

```
fava --port 8080 --debug /Volumes/Ledger/ledger.beancount
```
