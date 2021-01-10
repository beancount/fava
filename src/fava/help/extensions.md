Fava supports extensions. Extensions allow you to register hooks and generate
your own report pages.

If you use this extension system and need it to do more or need other hooks,
please open an issue on [GitHub](https://github.com/beancount/fava/issues).

A Fava extension is simply a Python module which contains a class that inherits
from `FavaExtensionBase` from `fava.ext`. Invoking an extension is done via the
`fava-extension` option in the beancount file. Check out `fava.ext.auto_commit`
for an example.

Extensions may also contain a report - this is detected when the extension's
class has a `report_title` attribute. The template for the report should be in
a `templates` subdirectory with a report matching the class's name. For
example, check out `fava.ext.portfolio_list` which has its template located at
`fava/ext/portfolio_list/templates/PortfolioList.html`.

The whole extension system should be considered unstable and it might change
drastically.

## Fava Extension Setup Options

---

## `fava-extension`

A Python module to load as extension. The path of the Beancount file is
searched in addition to anything on the Python path. Single python files will
also be searched - so for example a `my_extension.py` could be used by giving
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

### `after_write_source(path: str, source: str)`

Called after the string `source` has been written to the Beancount file at `path`.

---

### `after_insert_metadata(entry: Directive, key: str, value: str)`

Called after metadata (`key: value`) has been added to an `entry`.

---

### `after_insert_entry(entry: Directive)`

Called after an `entry` has been inserted.

---

### `after_entry_modified(entry: str, new_lines: str)`

Called after an `entry` has been modified, e.g., via the context popup.

---

## Extension attributes

### `report_title`

Optional attribute to set extension report title used in the sidebar.
