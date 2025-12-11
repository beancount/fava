# Importing entries into Fava

Fava integrates with Beancount's import system to automatically generate
transaction entries for your Beancount file from account statements. After
setting up your import process as explained below, the *Import* page in Fava
will show an upload button that lets you upload files into your *import folder*.
If you can access the import folder (e.g., if Fava is running on your local
machine), you can also just place your account statement files there directly.

To import the file contents into your Beancount ledger, you must set up an
*Importer* that can process the file format. Fava lists each file in the import
folder. If any Importer matches the file, a button "Extract" will be visible.
This will import its contents into your ledger. Files without a matching
Importer appear as "Non-importable file".

You can move any file into your
[documents folder](https://beancount.github.io/docs/beancount_language_syntax.html#documents-from-a-directory)
by clicking the button "Move". If you do not use the document folder feature of
Beancount, you can delete the file from the import folder after the import is
complete by clicking the button with the cross at the top right.

## Define the import configuration in your Beancount ledger

Add these lines to your Beancount file:

<pre><textarea is="beancount-textarea">
2021-01-01 custom "fava-option" "import-dirs" "folder/path/"
2021-01-01 custom "fava-option" "import-config" "my-import.py"
; ...
; ... Beancount entries ...
; ...
; Optional: New entries of all accounts (.*) that date earlier than 2022-01-01
;   will be inserted before this line. See the Fava help, section "Options".
; 2022-01-01 custom "fava-option" "insert-entry" ".*"
</textarea></pre>

The first line specifies the import folder location. The second line defines the
import configuration - a Python script that handles the format of your account
statements. Fava interprets relative paths relative to your main Beancount
ledger file location. You can also use absolute paths.

## Write your import configuration

Your import configuration must be a Python file that defines:

- `CONFIG`: A list of Importers that process your account statement files.
  Create subclasses of `beangulp.importers.Importer` with parsing logic for your
  specific account statement formats, then add instances of each class to this
  list. For CSV files, subclassing `beangulp.importers.csvbase.Importer` is
  recommended.

- `HOOKS`: A list of functions to apply to all directives (e.g., transactions)
  after generation by any Importer.

See the help document
[Importing External Data in Beancount](http://furius.ca/beancount/doc/ingest)
for more information on how to write importers. Hook functions are explained in
more detail further down on this page.

Fava currently only supports entries of type `Transaction`, `Balance`, and
`Note`. Set the special metadata key `__source__` to display the corresponding
text (CSV-row, XML-fragment, etc.) for the entry in the list of entries to
import. Note that this metadata (and all other metadata keys starting with an
underscore) will be stripped before saving the entry to file.

## Hook functions

Hook functions are applied to all imported transactions. A hook function
receives the parameters `hook_fn(new_entries_list, existing_entries)` and
returns the modified `new_entries_list`.

The argument `new_entries_list` is itself a list of tuples. As Fava imports each
file individually (in contrast to the CLI of Beangulp), this list will always be
of length 1.

The tuples can can have two (old style, default) or four elements
(beangulp-style). The type signature of the tuples is either

- `(filename: str, entries: list[Directive])` or
- `(filename: str, entries: list[Directive], account: str, importer: Importer)`.

You can annotate the hook function with the appropriate Python types and Fava
will detect and call it with these 4-tuples. Types `Directive` and `Importer`
are `beancount.core.data.Directive` and `beangulp.Importer`, respectively.

So, in summary, the type signature of a hook function is either:

```
hook_fn(new_entries_list: List[str, List[Directive]],
        existing_entries: Sequence[Directive]) -> List[str, List[Directive]]
```

or

```
hook_fn(new_entries_list: List[str, list[Directive], str, Importer],
        existing_entries: Sequence[Directive]) -> List[str, List[Directive]]
```
