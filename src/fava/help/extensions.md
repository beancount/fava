# Extensions

Fava supports extensions. Extensions allow you to register hooks and generate
your own report pages.

If you use this extension system and need it to do more or need other hooks,
please open an issue on [GitHub](https://github.com/beancount/fava/issues).

A Fava extension is simply a Python module which contains a class that inherits
from `FavaExtensionBase` from `fava.ext`. Invoking an extension is done via the
`fava-extension` option in the beancount file. Check out `fava.ext.auto_commit`
for an example.

Extensions may also contain a report - this is detected when the extension's
class has a `report_title` attribute. The template for the report should be in a
`templates` subdirectory with a report matching the class's name. For example,
check out `fava.ext.portfolio_list` which has its template located at
`fava/ext/portfolio_list/templates/PortfolioList.html`.

Finally, extensions may contain a Javascript module to be loaded in the
frontend. The module should be in a Javascript file matching the class's name
and the extension should have its `has_js_module` attribte set to `True`. The
module can define functions to be called when different events happen. Take a
look at `fava/ext/portfolio_list/PortfolioList.js` for an example. Currently,
the following events/functions can be specified:

- `init`: is called when a Fava report is first opened
- `onPageLoad`: Is called when any page in Fava is loaded (so on first open and
  on any further navigation).
- `onExtensionPageLoad`: Is called when the extension report is loaded.

The whole extension system should be considered unstable and it might change
drastically.

## Fava Extension Setup Options

---

## `fava-extension`

A Python module to load as extension. The path of the Beancount file is searched
in addition to anything on the Python path. Single python files will also be
searched - so for example a `my_extension.py` could be used by giving
`my_extension`. Note that Python has a global namespace for currently loaded
modules, so try avoiding simple names that might coincide with some Python
library (as well as running Fava on two files that have different extensions of
the same name).

Extensions allow for an optional configuration options string, whose structure
is specified by the individual extension.

<pre><textarea is="beancount-textarea">
2010-01-01 custom "fava-extension" "extension-name"
2010-01-01 custom "fava-extension" "extension-with-options" "{'option': 'config_value'}"</textarea></pre>

---

## Hooks

Below is a list of all current hooks.

### `after_load_file()`

Called after a ledger file has been loaded. Use the `self.ledger` object to
access the ledger data.

---

### `before_request()`

Called when starting to process a request. Use Flask’s `request` object to
access the request being processed (`from flask import request`).

---

### `after_write_source(path: str, source: str)`

Called after the string `source` has been written to the Beancount file at
`path`.

---

### `after_insert_metadata(entry: Directive, key: str, value: str)`

Called after metadata (`key: value`) has been added to an `entry`.

---

### `after_insert_entry(entry: Directive)`

Called after an `entry` has been inserted.

---

### `after_entry_modified(entry: Directive, new_lines: str)`

Called after an `entry` has been modified, e.g., via the context popup.

---

### `after_delete_entry(entry: Directive)`

Called after an `entry` has been deleted, e.g., via the context popup.

---

## Extension attributes

### `report_title`

Optional attribute to set extension report title used in the sidebar.
