# Import

Fava can use Beancount's import system to semi-automatically import entries into
your Beancount ledger. See
[Importing External Data in Beancount](http://furius.ca/beancount/doc/ingest)
for more information on how to write importers.

You can override the hooks that should be run for your importers by specifying a
variable `HOOKS` with the a list of hooks to apply to the list of
`(filename: str, entries: list[Directive])` tuples. On Beancount version 2 the
duplicates detector hook will be run by default and no hooks will run by default
on Beancount version 3. If you want to use beangulp-style hooks that take list
of
`(filename: str, entries: list[Directive], account: str, importer: Importer)`-tuples,
you can annotate them with the appropriate Python types which Fava will detect
and call with these 4-tuples.

Set the `import-config` option to point to your import config and set
`import-dirs` to the directories that contain the files that you want to import.
And if you wish to save new entries elsewhere than main file - use
`insert-entry` option.

Fava currently only supports entries of type `Transaction`, `Balance`, and
`Note`. Set the special metadata key `__source__` to display the corresponding
text (CSV-row, XML-fragment, etc.) for the entry in the list of entries to
import. Note that this metadata (and all other metadata keys starting with an
underscore) will be stripped before saving the entry to file.
