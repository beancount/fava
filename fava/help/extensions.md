Fava supports extensions. Currently they can only register hooks for some events.

If you use this extension system and need it to do more or need other hooks,
please open an issue on [GitHub](https://github.com/beancount/fava/issues).

A Fava extension is simply a Python module which contains a class that inherits
from `FavaExtensionBase` from `fava.ext`. Check out `fava.ext.auto_commit` for an
example. To use an extension, see the `extensions` option for Fava.

The whole extension system should be considered unstable and it might change
drastically.

## Hooks

Below is a list of all current hooks.

### `after_write_source(path, source)`

Called after the string `source` has been written to the Beancount file at `path`.

---

### `after_insert_metadata(entry, key, value)`

Called after metadata (`key: value`) has been added to an `entry`.

---

### `after_insert_entry(entry)`

Called after an `entry` has been inserted.
