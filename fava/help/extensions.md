Fava supports extensions. Currently they can only register hooks for some
events.

If you use this extension system and need it to do more or need other hooks,
please open an issue on [GitHub](https://github.com/beancount/fava/issues).

A Fava extension is simply a Python module which contains a class that inherits
from `FavaExtensionBase` from `fava.ext`. Invoking an extension is done via the
`fava-extension` option in the beancount file. Check out `fava.ext.auto_commit`
for an example.

Extensions may also contain a report - this is detected when the extension's
directory has a `templates` subdirectory with a report matching the class's
qualified name. For example, check out `fava.ext.portfolio_list` which has its
template located at `fava/ext/portfolio_list/templates/PortfolioList.html`.
Extension report titles default to the extension class's `qualname` unless set
via `report_title` attribute.

The whole extension system should be considered unstable and it might change
drastically.

## Fava Extension Setup Options

---

## `fava-extension`

A Python module to load as extension. The paths used by fava are searched along with what is set via the fava option `extensions-dir`. Single python files will also be searched - so for example a `my_extension.py` could be used by giving `my_extension`. Note that Python has a
global namespace for currently loaded modules, so try avoiding simple names
that might coincide with some Python library (as well as running Fava on two
files that have different extensions of the same name).

Extensions allow for an optional configuration options string, whose structure is specified by the individual extension.

<pre><textarea class="editor-readonly">
2010-01-01 custom "fava-extension" "extension-name"
2010-01-01 custom "fava-extension" "extension-with-options" "{'option': 'config_value'}"</textarea></pre>

---

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

---

### `report_title`

Optional attribute to set extension report title used in sidebar & breadcrumb views.
