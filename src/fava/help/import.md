Fava can use Beancount's import system to semi-automatically import entries
into your Beancount ledger. See [Importing External Data in
Beancount](http://furius.ca/beancount/doc/ingest) for more information on how
to write importers.

Set the `import-config` option to point to your import config and set
`import-dirs` to the directories that contain the files that you want to
import. And if you wish to save new entries elsewhere than main file - use
`insert-entry` option.

Fava currently only supports entries of type `Transaction` and `Balance`. Set
the special metadata key `__source__` to display the corresponding text
(CSV-row, XML-fragment, etc.) for the entry in the list of entries to import.
Note that this metadata will be stripped before saving the entry to file.
