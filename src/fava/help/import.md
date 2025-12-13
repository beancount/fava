# Importing transactions into Fava

Fava integrates with Beancount's import system to automatically generate
transaction entries for your Beancount ledger from account statements. After
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
beancount, you can delete the file from the import folder after the import is
complete by clicking the button with the cross at the top right.

## Define the upload configuration in your Beancount ledger

Add these lines to your Beancount file:

<pre><textarea is="beancount-textarea">
2021-01-01 custom "fava-option" "import-dirs" "folder/path/"
2021-01-01 custom "fava-option" "import-config" "my-import.py"
; Optional: To save new entries in a separate file instead of the main file 
; 2021-01-01 custom "fava-option" "insert-entry" "current-year.beancount"
</textarea></pre>

The first line specifies the import folder location. The second line defines the
import configuration - a Python script that handles the format of your account
statements. Fava interprets relative paths relative to your main Beancount
ledger file location. You can also use absolute paths.

## Write your import configuration

Your import configuration must be a Python file that defines:

- `CONFIG`: A list of Importers that process your account statement files.
  YCreate subclasses of `beangulp.importers.Importer` with parsing logic for
  your specific account statement formats, then add instances of each class to
  this list.

- `HOOKS`: A list of functions to apply to all directives (e.g., transactions)
  after generation by any Importer.

See the example below and the help document
[Importing External Data in Beancount](http://furius.ca/beancount/doc/ingest)
for more information on how to write importers. Hook functions are explained in
more detail further down on this page.

Fava currently only supports entries of type `Transaction`, `Balance`, and
`Note`. Set the special metadata key `__source__` to display the corresponding
text (CSV-row, XML-fragment, etc.) for the entry in the list of entries to
import. Note that this metadata (and all other metadata keys starting with an
underscore) will be stripped before saving the entry to file.

# Example import configuration

This is an example configuration to read in account statements provided as CSV:

```python
import csv
import re

import beangulp
import beangulp.importers.csvbase as csvbase
from beancount.core import data # Transaction, Posting, ...

class MyCSVImporter(csvbase.Importer):
    """Read a CSV file formatted in German style to demonstrate some formatting
    options: Column separator = ";", decimals are like this: 2.032,43 (dot as
    thousands separator, comma as decimal separator"""

    # The expected column names and formats in the input file are defined
    # as member variables, that are instances of csvbase.Column or subclasses
    #
    # Required columns
    date = csvbase.Date('Buchungstag', '%d.%m.%Y') # German date format
    narration = csvbase.Column('Verwendungszweck')
    # To parse amount, first remove dots, then translate commas to dots,
    # to convert 2.032,43 -> 3032.43
    amount = csvbase.Amount('Betrag', subs={r'\.':'', r',': '.'})
    
    # Optional further columns: 
    # flag, payee, account, currency, tag, link, balance.

    # Any additional members of type "Column" can be used by your own
    # `finalize()` and `metadata()` functions, access e.g. as row.sepa_iban
    sepa_iban = Column('IBAN') 

    # The following variables set the CSV format (see csvbase.CSVReader):
    # encoding = "utf8" # File encoding.
    # header = 0        # Number of header lines to skip.
    # footer = 0        # Number of footer lines to ignore.
    # names = True      # Whether the data file contains a row with column names.
    # dialect = None    # The CSV dialect used in the input file (str or csv.Delimiter object).
    # comments = "#"    # Comment character.
    # order = None      # Order of entries in the CSV file (Default: Infer from file)
    #                   # can be csvbase.Order.ASCENDING or ...DESCENDING

    # Set CSV dialect to use semicolon as separator
    dialect = csv.excel
    dialect.delimiter = ';'

    def __init__(self):
        super().__init__(
            account="Assets:MyBank", # default if no account column is defined
            currency="EUR",
            flag = "*" # optional
        )

    def identify(self, filepath):
        """Return True if this importer is suitable for the file of the given
        name. This allows to auto-choose the right importer for a file."""
        return "MyBank" in filepath

    def read(self, filepath):
        """Override the read method to preprocess the CSV file.
        """
        # Add some pre-processing of the input file, then 
        # call the parent read method with the processed file
        for row in super().read(filepath):
            yield row

    def metadata(self, filepath, lineno, row):
        """
        Called for each row of the input file to set the metadata of the 
        resulting transaction. 
        Arguments: 
          - filepath, lineno: The file path and line number
          - row: Has attributes for each class member of type `Column` (or 
            subtypes)
        """
        # Example: Add the values from the additional sepa_iban column as 
        # metadata
        return data.new_metadata(filepath, lineno, {'iban': row.sepa_iban})

    def finalize(self, txn, row):
        """Called for each generated transaction `txn` to make user-defined
        changes. The input data is available as attributes of `row`"""
        # Example: Add a default second transaction leg to Expenses:Unknown
        # Documentation of Transaction object (txt): 
        # https://beancount.github.io/docs/api_reference/beancount.core.html#beancount.core.data.Transaction
        txn.postings.append(data.Posting(
            account = "Expenses:Unknown", units = -txn.postings[0].units ))

        return txn


# All available importers, one for each file format you need to process
CONFIG = [
  MyCSVImporter()
]

# Process beancount transaction objects after they have been extracted
HOOKS = []

# Allows to call this script as './import extract <filename.csv>'. Not needed
# for Fava, but useful for debugging
if __name__ == "__main__":
    ingest = beangulp.Ingest(CONFIG, HOOKS)
    ingest()
```

## Hook functions

Hook functions are applied to all imported transactions. A hook function
receives the parameters `hook_fn(new_entries_list, existing_entries)` and
returns the modified `new_entries_list`.

The argument `new_entries_list` is itself a list of tuples. As Fava imports each
file individually (in in contrast to the CLI of Beangulp), this list will always
be of length 1.

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
