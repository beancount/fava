Fava integrates with Beancount's import system to automatically generate
transaction entries for your Beancount file from account statements. After
setting up your import process as explained below, the *Import* page in Fava
will show an upload button that lets you upload files into your *import folder*
(the first one, if you have configured several). If you can access the import
folder (e.g., if Fava is running on your local machine), you can also just place
your account statement files there directly.

To import the file contents into your Beancount ledger, you must set up an
*Importer* that can process the file format. Fava lists each file in the import
folder. If any Importer matches the file, a button "Extract" will be visible.
This shows the extracted entries, which you can review, edit, or skip before
saving them to your ledger. Files without a matching Importer are listed in the
collapsed section "Non-importable Files".

You can move any file into your
[documents folder](https://beancount.github.io/docs/beancount_language_syntax.html#documents-from-a-directory)
by clicking the "Move" button. This requires the Beancount option `documents` to
be set; the file is moved to `<documents>/<account>/<new name>`, where you can
edit the account and the new name before moving. If you do not use the document
folder feature of Beancount, you can delete the file from the import folder
after the import is complete by clicking the "x" button.

## Define the import configuration in your Beancount ledger

Add these lines to your Beancount file:

```beancount
2021-01-01 custom "fava-option" "import-dirs" "folder/path/"
2021-01-01 custom "fava-option" "import-config" "my-import.py"
; ...
; ... Beancount entries ...
; ...
; Optional: New entries of all accounts (.*) dated after 2022-01-01 will be
;   inserted before this line. See the Fava help, section "Options".
; 2022-01-01 custom "fava-option" "insert-entry" ".*"
```

The first line specifies the import folder location. The second line defines the
import configuration - a Python script that handles the format of your account
statements. Fava interprets relative paths relative to your main Beancount
ledger file location. You can also use absolute paths.

## Write your import configuration

Your import configuration must be a Python file that defines:

- `CONFIG`: A list of Importers that process your account statement files.
  Create subclasses of `beangulp.Importer` with parsing logic for your specific
  account statement formats, then add instances of each class to this list.
- `HOOKS`: A list of functions to apply to all directives (e.g., transactions)
  after generation by any Importer.

For a small working example with a CSV importer and an import hook, see
[contrib/personal_ledger](https://github.com/beancount/fava/tree/main/contrib/personal_ledger).
For more information on how to write importers, see the documentation of
[beangulp](https://github.com/beancount/beangulp). Hook functions are explained
in more detail further down on this page.

Fava currently only supports entries of type `Transaction`, `Balance`, and
`Note`. Set the special metadata key `__source__` to display the corresponding
text (CSV-row, XML-fragment, etc.) for the entry in the list of entries to
import. Note that this metadata (and all other metadata keys starting with an
underscore) will be stripped before saving the entry to file.

## Hook functions

Hook functions are applied to all imported entries. A hook function receives the
parameters `hook_fn(new_entries_list, existing_entries)` and returns the
modified `new_entries_list`.

The argument `new_entries_list` is a list of
`(filename: str, entries: list[Directive], account: str, importer: Importer)`
tuples, where `Directive` and `Importer` are `beancount.core.data.Directive` and
`beangulp.Importer`, respectively. As Fava imports each file individually (in
contrast to the CLI of Beangulp), this list will always be of length 1. The hook
must return a non-empty list of such tuples; only the entries of the first tuple
are used. If a hook raises an exception or returns something else, Fava shows an
error.

So, in summary, the type signature of a hook function is:

```python
def hook_fn(
    new_entries_list: list[tuple[str, list[Directive], str, Importer]],
    existing_entries: Sequence[Directive],
) -> list[tuple[str, list[Directive], str, Importer]]: ...
```

The `categorize` hook in
[contrib/personal_ledger](https://github.com/beancount/fava/tree/main/contrib/personal_ledger)
is an example of such a hook function.

No hooks are run by default. Before the hooks are applied, each importer's
`deduplicate()` method marks entries that duplicate existing ones. These are
shown with the checkbox "ignore duplicate" checked in the list of entries to
import and are not saved, unless you uncheck it.
