# ruff: noqa: ERA001, INP001, ARG002
"""An example import configuration with explanations."""

from __future__ import annotations

import csv
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

import beangulp  # Importing tools
import beangulp.importer
from beancount.core import data  # Transaction, Posting, ...
from beangulp.importers import csvbase

if TYPE_CHECKING:
    import beancount

    Meta = beancount.core.data.Meta
    Transaction = beancount.core.data.Transaction
    Row = "Row"  # a dynamically defined type based on NamedTuple


class MyCSVImporter(csvbase.Importer):
    """Read the csv file called "import.csv", in this directory.

    This is a CSV file formatted in German style to demonstrate some formatting
    options: Column separator = ";", decimals are like this: 2.032,43 (dot as
    thousands separator, comma as decimal separator.
    """

    # The expected column names and formats in the input file are defined
    # as member variables, that are instances of csvbase.Column or subclasses
    #
    # Required columns
    date = csvbase.Date("Buchungsdatum", "%Y-%m-%d")
    narration = csvbase.Column("Umsatztext")
    # To parse amount, first remove dots, then translate commas to dots,
    # to convert 2.032,43 -> 3032.43
    amount = csvbase.Amount("Betrag", subs={r"\.": "", r",": "."})

    # Optional further columns:
    # flag, payee, account, currency, tag, link, balance.
    # Providing 'balance' will auto-generate a balance assertion after the
    # imported entries.
    balance = csvbase.Amount("Saldo", subs={r"\.": "", r",": "."})

    # Any additional members of type "Column" can be used by your own
    # `finalize()` and `metadata()` functions, access e.g. as row.sepa_iban
    sepa_iban = csvbase.Column("IBAN")

    # The following variables set the CSV format (see csvbase.CSVReader):
    # encoding = "utf8" # File encoding.
    # skiplines = 0     # NOTE: Will be renamed to "header" in beangulp 0.3.0
    # names = True      # Whether the input contains a row with column names.
    # dialect = None    # The CSV dialect used in the input file
    #                   #   (str or csv.Delimiter object).
    # comments = "#"    # Comment character.
    # order = None      # Order of entries in the CSV file
    #                   #   (Default: Infer from file)
    order = csvbase.Order.DESCENDING

    # Set CSV dialect to use semicolon as separator
    dialect = csv.excel
    dialect.delimiter = ";"

    def __init__(self) -> None:
        super().__init__(
            account="Assets:MyBank",  # default if no account column is defined
            currency="EUR",
            flag="*",  # optional
        )

    def identify(self, filepath: str) -> bool:
        """Return True if this importer is suitable for the given filename.

        This allows to auto-choose the right importer for a file.

        Arguments:
            filepath: File path to read.
        """
        return filepath.endswith("import.csv")

    # ruff: noqa: SIM115
    def read(self, filepath: str) -> Row:
        """Override the read method to preprocess the CSV file.

        Arguments:
            filepath: File path to read.

        Returns:
            Values from one line of the input. Named tuple with attributess
               named like class members of type Column.
        """
        # Add some pre-processing of the input file, then
        # call the parent read method with the processed file

        # Truncate the last line
        try:
            tmp = NamedTemporaryFile("w", delete=False)
            with tmp:
                lines = Path(filepath).read_text().splitlines()
                lines = lines[:-1]
                tmp.write("\n".join(lines))

            yield from super().read(tmp.name)

        finally:
            Path(tmp.name).unlink()

    def metadata(self, filepath: str, lineno: int, row: Row) -> Meta:
        """Set the metadata of imported transactions.

        This is called for each row of the input file.

        Arguments:
          filepath: Import file name
          lineno: Import file line number
          row: Values from one line of the input. Named tuple with
            attributes named like class members of type Column.

        Returns:
          Object as created by beancount.core.data.new_metadata()
        """
        # Example: Add the values from the additional sepa_iban column as
        # metadata
        return data.new_metadata(filepath, lineno, {"iban": row.sepa_iban})
        # To set posting metadata, use the finalize() function. There you can
        # access txn.postings[i].meta as a simple dictionary.

    def finalize(self, txn: Transaction, row: Row) -> Transaction:
        """Called for each generated transaction to make user-defined changes.

        Arguments:
          txn: beancount.data.core.Transaction.
          row: Values from one line of the input. Named tuple with
            attributes named like class members of type Column.

        Returns:
          beancount.core.data.Transaction object.
        """
        # Example: Add a default second transaction leg to Expenses:Unknown
        # Documentation of Transaction object (txt):
        # https://beancount.github.io/docs/api_reference/beancount.core.html#beancount.core.data.Transaction
        txn.postings.append(
            data.Posting(
                "Expenses:Unknown",
                -txn.postings[0].units,
                None,
                None,
                None,
                None,
            )
        )

        return txn


# All available importers, one for each file format you need to process
CONFIG = [MyCSVImporter()]

# Process beancount transaction objects after they have been extracted
HOOKS = []

# Allows to call this script as './import extract <filename.csv>'. Not needed
# for Fava, but useful for debugging
if __name__ == "__main__":
    ingest = beangulp.Ingest(CONFIG, HOOKS)
    ingest()
